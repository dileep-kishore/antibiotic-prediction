#!/usr/bin/env python

import argparse
import pathlib

import pandas as pd
from Bio import Align


def parse_rgi(rgi_file: str) -> pd.Series:
    """
    Parse the rgi file and return a pandas Series with id and protein sequences.

    Parameters
    ---------
    rgi_file : str
        The rgi file to be parsed.

    Returns
    ------
    pd.Series
        The pandas Series with id and protein sequences.
    """
    rgi_data_path = pathlib.Path(rgi_file)
    if not rgi_data_path.exists():
        raise FileNotFoundError(f"{rgi_data_path} does not exist")
    rgi_data = pd.read_csv(rgi_file, sep="\t")
    return rgi_data["Predicted_Protein"]


def get_best_alignment(query_protein: str, target_proteins: pd.Series) -> tuple:
    """
    Get the best alignment for a query protein among target proteins

    Parameters
    ---------
    query_protein : str
        The query protein to be aligned
        This is the resistance marker extracted from the antibiotic BGC
    target_proteins : pd.Series
        The target protein to be aligned against
        These are resistance markers extracted from the target genome

    Returns
    ------
    tuple
        Tuple containing alignment object and alignment score
    """
    best_score = 0
    best_alignment = tuple()
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -15.00  # -10
    aligner.extend_gap_score = -6.67  # -0.5
    for ind, target_protein in target_proteins.items():
        alignments = aligner.align(query_protein, target_protein)
        alignment = max(alignments, key=lambda a: a.score)  # type: ignore
        score = alignment.score  # type: ignore
        if score > best_score:
            best_score = score
            best_alignment = alignment
    return best_alignment, best_score


def main(query_file: str, target_file: str) -> float:
    # Parse the RGI file using pandas and get the prediction proteins for each
    query_proteins = parse_rgi(query_file)
    target_proteins = parse_rgi(target_file)
    # For each query protein do global alignment with every target protein
    scores = []
    for ind, query_protein in query_proteins.items():
        # Get the best alignment score for each query protein
        print(f"{ind}: Aligning {query_protein}")
        alignment, score = get_best_alignment(query_protein, target_proteins)
        scores.append(score)
    # Get the average score for all query proteins => metric
    scores_avg = sum(scores) / len(scores)
    print(scores_avg)
    return scores_avg


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "query_rgi_file",
        type=str,
        help="Path to the query rgi file from the antibiotic BGC",
    )
    PARSER.add_argument(
        "target_rgi_file",
        type=str,
        help="Path to the target rgi file from the target genome",
    )
    ARGS = PARSER.parse_args()
    query_rgi_file = ARGS.query_rgi_file
    target_rg_file = ARGS.target_rgi_file

    main(query_rgi_file, target_rg_file)
