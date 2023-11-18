#!/usr/bin/env python

import argparse
import multiprocessing as mp
import pathlib
import subprocess
from typing import List


def aggregate_results_cmd(genomes: List[pathlib.Path], output_dir: str):
    cmd = ["python", "aggregate_results.py", *genomes, "--output_dir", output_dir]
    return cmd


def run_predict_function(
    genome: pathlib.Path, output_dir: str, no_SSN: str, perc_complete: float
) -> str:
    cmd = ["bash", "predict_function.sh", genome, genome.stem, output_dir, no_SSN]
    subprocess.run(cmd, check=True)
    perc_str = "%:.2f".format(perc_complete)
    callback = perc_str + ". Running BGC function prediction on " + genome.stem
    print(callback, flush=True)
    return callback


def main(genomes: List[pathlib.Path], output_dir: str, no_SSN: str, ncpus: int):
    # Step 1: Run BGC function prediction
    if ncpus == -1:
        npools = mp.cpu_count()
    else:
        npools = ncpus
    with mp.Pool(npools) as pool:
        task_args = []
        for i, genome in enumerate(genomes):
            perc_complete = (i + 1) / len(genomes) * 100
            task_args.append((genome, output_dir, no_SSN, perc_complete))
        pool.starmap(
            run_predict_function,
            task_args,
        )
    # Step 2: Aggregate results
    print("--------------------------------------------")
    print("Aggregating results")
    aggregate_cmd = aggregate_results_cmd(genomes, output_dir)
    subprocess.run(aggregate_cmd, check=True)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "genomes_glob",
        type=str,
        help="Paths to input genome files containing glob",
    )
    PARSER.add_argument("--output_dir", help="Directory to store the outputs")
    PARSER.add_argument(
        "--no_SSN",
        action="store_true",
        help="Flag to indicate whether to consider SSN for features",
    )
    PARSER.add_argument(
        "--ncpus",
        type=int,
        default=-1,
        help="Number of CPUs to use for parallelization",
    )
    ARGS = PARSER.parse_args()

    genomes_glob = ARGS.genomes_glob
    genome_parent_dir = pathlib.Path(genomes_glob).parent
    genome_glob_pattern = pathlib.Path(genomes_glob).name
    genomes = []
    for genome_path in genome_parent_dir.glob(genome_glob_pattern):
        if not genome_path.is_file():
            continue
        genomes.append(genome_path)

    output_dir = ARGS.output_dir
    no_SSN = "True" if ARGS.no_SSN else "False"
    ncpus = ARGS.ncpus

    main(genomes, output_dir, no_SSN, ncpus)
