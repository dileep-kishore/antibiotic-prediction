#!/usr/bin/env python

import argparse
import multiprocessing as mp
import pathlib
import subprocess
import warnings
from collections import defaultdict
from itertools import combinations

warnings.filterwarnings("ignore", category=DeprecationWarning)


def run_parse_clinker(
    antibiotic_bgc: pathlib.Path,
    target_bgc: pathlib.Path,
    output_dir: pathlib.Path,
    perc_complete: float,
) -> str:
    cmd = [
        "python",
        "run_parse_clinker.py",
        str(antibiotic_bgc),
        str(target_bgc),
        "--output_dir",
        str(output_dir),
    ]
    if output_dir.is_dir():
        return f"Clinker output for {output_dir.parent.stem} already exists"
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)
    callback = f"{perc_complete:.2f}%. Running BGC function prediction on {output_dir.parent.stem}"
    print(callback, flush=True)
    return callback


def run_rgi(
    genome: pathlib.Path, output_dir: pathlib.Path, file_name: str, perc_complete: float
) -> str:
    cmd = [
        "bash",
        "run_rgi.sh",
        str(genome),
        str(output_dir),
        file_name,
    ]
    if output_dir.is_dir():
        return f"RGI output for {genome.stem} already exists"
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)
    callback = f"{perc_complete:.2f}%. Running RGI on {genome.stem}"
    print(callback, flush=True)
    return callback


def parse_align_rgi(
    rgi_query: pathlib.Path,
    rgi_target: pathlib.Path,
    output_dir: pathlib.Path,
    filter: bool,
    perc_complete: float,
) -> str:
    cmd = [
        "python",
        "parse_align_rgi.py",
        str(rgi_query),
        str(rgi_target),
        "--output_dir",
        str(output_dir),
    ]
    if filter:
        cmd.append("--filter")
    if output_dir.is_dir():
        return f"Alignment output for {rgi_query.stem} already exists"
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)
    callback = f"{perc_complete:.2f}%. Running alignment on {rgi_query.stem} and {rgi_target.stem}"
    print(callback, flush=True)
    return callback


def get_data_files(
    data_dir: pathlib.Path, glob: str, sub_folder: str
) -> dict[str, list[pathlib.Path]]:
    data_dict = defaultdict(list)
    for genome_folder in data_dir.iterdir():
        if not genome_folder.is_dir():
            continue
        antismash_folder = genome_folder / sub_folder
        for data_file in antismash_folder.glob(glob):
            if data_file.stem == genome_folder.stem:
                continue
            data_dict[genome_folder.name].append(data_file)
    return data_dict


def get_target_bgcs(
    query_genome: str, genome_bgc_dict: dict[str, list[pathlib.Path]]
) -> list[pathlib.Path]:
    target_bgcs = []
    for genome in genome_bgc_dict:
        if genome == query_genome:
            continue
        target_bgcs.extend(genome_bgc_dict[genome])
    return target_bgcs


def main(
    data_dir: pathlib.Path,
    genomes: list[pathlib.Path],
    output_dir: pathlib.Path,
    ncpus: int,
) -> None:
    genome_bgc_dict = get_data_files(data_dir, glob="*.gbk", sub_folder="antismash")
    genome_bgc_rgi_dict = get_data_files(data_dir, glob="**/*.txt", sub_folder="rgi")
    if ncpus == -1:
        npools = mp.cpu_count()
    else:
        npools = ncpus
    with mp.Pool(npools) as pool:
        # Run RGI on all the genomes
        rgi_task_args = []
        for i, genome in enumerate(genomes):
            perc_complete = (i + 1) / len(genomes) * 100
            file_name = genome.stem
            rgi_dir = output_dir / genome.stem / "rgi"
            rgi_task_args.append((genome, rgi_dir, file_name, perc_complete))
        pool.starmap(run_rgi, rgi_task_args)
        # Get all combinations of gbks and run run_parse_clinker
        for i, genome in enumerate(genome_bgc_dict):
            clinker_task_args = []
            print("--------------------------------------------", flush=True)
            print(f"{i+1}: Running clinker on BGCs from {genome}", flush=True)
            clinker_dir = output_dir / genome / "clinker"
            query_bgcs = genome_bgc_dict[genome]
            # FIXME: Genome combinations are not exhaustive!!
            target_bgcs = get_target_bgcs(genome, genome_bgc_dict)
            # TODO: Can increase efficiency by preventing reverse comparisons
            for j, query_bgc in enumerate(query_bgcs):
                perc_complete = (j + 1) / len(query_bgcs) * 100
                for target_bgc in target_bgcs:
                    if query_bgc == target_bgc:
                        continue
                    clinker_task_args.append(
                        (query_bgc, target_bgc, clinker_dir, perc_complete)
                    )
            pool.starmap(run_parse_clinker, clinker_task_args)
        # Run parse_align_rgi on all the query_rgi_dict vs. genomes
        for i, query_genome in enumerate(genome_bgc_rgi_dict):
            alignment_task_args = []
            print("--------------------------------------------", flush=True)
            print(
                f"{i+1}: Running alignment on RGI makers from {query_genome}",
                flush=True,
            )
            rgi_align_dir = output_dir / query_genome / "rgi_align"
            query_bgc_markers = genome_bgc_rgi_dict[query_genome]
            for j, query_rgi_file in enumerate(query_bgc_markers):
                perc_complete = (j + 1) / len(query_bgc_markers) * 100
                for target_genome in genomes:
                    target_genome_dir = output_dir / target_genome.stem
                    if target_genome.stem == query_genome:
                        continue
                    target_rgi_file = (
                        target_genome_dir / "rgi" / f"{target_genome.stem}.txt"
                    )
                    alignment_task_args.append(
                        (
                            query_rgi_file,
                            target_rgi_file,
                            rgi_align_dir,
                            True,
                            perc_complete,
                        )
                    )
            pool.starmap(parse_align_rgi, alignment_task_args)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "data_dir", type=str, help="Path to the output folder of pipeline 1"
    )
    PARSER.add_argument(
        "genomes_glob",
        type=str,
        help="Paths to input genome files containing glob",
    )
    PARSER.add_argument("--output_dir", type=str, help="Path to the output directory")
    PARSER.add_argument(
        "--ncpus",
        type=int,
        default=-1,
        help="Number of CPUs to use for parallelization",
    )
    ARGS = PARSER.parse_args()

    data_dir = pathlib.Path(ARGS.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"{data_dir} does not exist")

    genomes_glob = ARGS.genomes_glob
    genome_parent_dir = pathlib.Path(genomes_glob).parent
    genome_glob_pattern = pathlib.Path(genomes_glob).name
    genomes = []
    for genome_path in genome_parent_dir.glob(genome_glob_pattern):
        if not genome_path.is_file():
            continue
        genomes.append(genome_path)

    output_dir = pathlib.Path(ARGS.output_dir)
    ncpus = ARGS.ncpus

    main(data_dir, genomes, output_dir, ncpus)
