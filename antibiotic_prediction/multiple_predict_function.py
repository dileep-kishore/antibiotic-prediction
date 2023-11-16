#!/usr/bin/env python

import argparse
import glob
import pathlib
import subprocess
from typing import List


def predict_function_cmd(genome: pathlib.Path, output_dir: str, no_SSN: str):
    cmd = ["bash", "predict_function.sh", genome, output_dir, no_SSN]
    return cmd


def aggregate_results_cmd(genomes: List[pathlib.Path], output_dir: str):
    cmd = ["python", "aggregate_results.py", *genomes, "--output_dir", output_dir]
    return cmd


def main(genomes: List[pathlib.Path], output_dir: str, no_SSN: str):
    # Step 1: Run BGC function prediction
    for i, genome in enumerate(genomes):
        print(str(i + 1) + ". Running BGC function prediction on " + str(genome))
        predict_cmd = predict_function_cmd(genome, output_dir, no_SSN)
        subprocess.run(predict_cmd, check=True)
        print("--------------------------------------------")
    # Step 2: Aggregate results
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
    ARGS = PARSER.parse_args()

    genomes_glob = ARGS.genomes_glob
    genomes = []
    for genome in glob.glob(genomes_glob):
        genome_path = pathlib.Path(genome)
        if not genome_path.is_file():
            continue
        genomes.append(genome_path)
    output_dir = ARGS.output_dir
    no_SSN = "True" if ARGS.no_SSN else "False"
    main(genomes, output_dir, no_SSN)
