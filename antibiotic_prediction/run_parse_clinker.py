#!/usr/bin/env python

import argparse
import pathlib

import pandas as pd
from clinker.align import Globaligner
from clinker.main import clinker

# TODO: Check notes for details
# Metric 2: The number of genes in the antibiotic BGC that are aligned (gives you # of genes with similarity > 0.3)
# Metric 3 & 4: Average identity and similarity of the genes in the alignments file


def run_clinker(files: list[pathlib.Path]) -> Globaligner:
    """
    Runs the CLINKER algorithm on a list of input files.

    Parameters
    ----------
    file : list[pathlib.Path]
        A list of input files to be processed by CLINKER.

    Returns
    -------
    Globaligner
        The CLINKER object containing the results of the alignment.
    """
    return clinker(files)


def parse_cluster_similarity(ga: Globaligner) -> float:
    """
    Parse cluster similarity information from the alignment file.

    Parameters
    ---------
    ga : Globaligner
        The clinker object containing the results of the alignment.

    Returns
    ------
    float
        The cluster similarity of the alignment

    NOTE
    ----
    Here was assume that the Globaligner object contains only one alignment
    """
    cluster_names = [ga.clusters[uid].name for uid in ga.clusters]
    if not len(cluster_names) == 2:
        raise ValueError("More than two clusters in the alignment")
    matrix = ga.matrix()
    return matrix[0, 1]


def main(source_bgc: str, target_bgcs: list[str]) -> None:
    source_bgc_path = pathlib.Path(source_bgc)
    if not source_bgc_path.exists():
        raise FileNotFoundError("{source_bgc_path} does not exist")
    target_bgc_paths = []
    data = []
    for target_bgc in target_bgcs:
        target_bgc_path = pathlib.Path(target_bgc)
        if not pathlib.Path(target_bgc_path).exists():
            raise FileNotFoundError(f"{target_bgc_path} does not exist")
        target_bgc_paths.append(target_bgc_path)
        ga = run_clinker([source_bgc_path, target_bgc_path])
        cluster_similarity = parse_cluster_similarity(ga)
        data_item = {
            "source_bgc": source_bgc_path.stem,
            "target_bgc": target_bgc_path.stem,
            "cluster_similarity": cluster_similarity,
        }
        data.append(data_item)
    df = pd.DataFrame(data)
    df.to_csv(f"{source_bgc_path.stem}_cluster_similarity.csv")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "source_bgc",
        type=str,
        help="Path to .gbk file containing the source BGC from the first genome",
    )
    PARSER.add_argument(
        "target_bgcs",
        nargs="+",
        help="Path to .gbk files containing the target BGCs from the second genome",
    )
    ARGS = PARSER.parse_args()

    source_bgc = ARGS.source_bgc
    target_bgcs = ARGS.target_bgcs
    main(source_bgc, target_bgcs)
