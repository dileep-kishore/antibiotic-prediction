#!/usr/bin/env python

import argparse
import pathlib
import subprocess

import pandas as pd
from Bio import Align, SearchIO, SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def parse_rgi(rgi_file: str) -> pd.DataFrame:
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
    rgi_data.Contig = rgi_data.Contig.str.replace(" ", "")
    return rgi_data


def create_fasta(
    proteins: pd.Series | pd.DataFrame, file_path: pathlib.Path, multiple: bool
) -> None:
    """
    Create a fasta file from the proteins

    Parameters
    ---------
    proteins : pd.Series | pd.DataFrame
        The proteins to be written to the fasta file
    file_path : pathlib.Path
        The path to the fasta file
    multiple : bool
        Whether to write multiple proteins to the fasta file
    """
    seq_records = []
    if multiple and isinstance(proteins, pd.DataFrame):
        for _, data in proteins.iterrows():
            record = SeqRecord(
                Seq(data.Predicted_Protein), id=data.Contig, description=data.ID
            )
            seq_records.append(record)
    elif not multiple and isinstance(proteins, pd.Series):
        record = SeqRecord(
            Seq(proteins.Predicted_Protein),
            id=proteins.Contig,
            description=proteins.ID,
        )
        seq_records.append(record)
    else:
        raise ValueError("Incorrect format of proteins or multiple option")
    with open(file_path, "w") as fasta_file:
        SeqIO.write(seq_records, fasta_file, "fasta")


def parse_blast(blast_results: pathlib.Path) -> pd.DataFrame:
    """
    Parse the blast results and return a pandas DataFrame

    Parameters
    ---------
    blast_results : pathlib.Path
        The blast results to be parsed

    Returns
    ------
    pd.DataFrame
        The pandas DataFrame with the blast results
    """
    blast_qresult = SearchIO.parse(blast_results, "blast-tab")
    blast_data = []
    for qresult in blast_qresult:
        for hit in qresult.hits:
            for hsp in hit.hsps:
                if hsp.evalue >= 0.01:
                    continue
                blast_data.append(
                    {
                        "query_id": qresult.id,
                        "query_start": hsp.query_start,
                        "query_end": hsp.query_end,
                        "hit_id": hit.id,
                        "hit_start": hsp.hit_start,
                        "hit_end": hsp.hit_end,
                        "evalue": hsp.evalue,
                        "bitscore": hsp.bitscore,
                    }
                )
    sorted_blast_data = sorted(blast_data, key=lambda d: d["bitscore"], reverse=True)
    if not sorted_blast_data:
        return pd.DataFrame(
            columns=[
                "query_id",
                "query_start",
                "query_end",
                "hit_id",
                "hit_start",
                "hit_end",
                "evalue",
                "bitscore",
            ]
        )
    else:
        return pd.DataFrame(sorted_blast_data)


# TODO: Change blast output to XML format
def perform_blast(
    query_protein: pd.Series,
    target_proteins: pd.DataFrame,
    output_path: pathlib.Path,
    n_hits: int,
) -> pd.DataFrame:
    """
    Perform blastp on the query protein against the target proteins and return the top n_hits

    Parameters
    ---------
    query_protein : pd.Series
        The query protein to be aligned along with RGI information
    target_proteins : pd.DataFrame
        The target proteins to be aligned against (along with RGI information)
        These are resistance markers extracted from the target genome
    output_path : pathlib.Path
        The path to the output directory
    n_hits : int
        The number of top blast hits to use for global alignment

    Returns
    ------
    pd.DataFrame
        The top n_hits target proteins to be aligned against (along with RGI information)
    """
    folder = output_path / query_protein.Contig
    folder.mkdir(parents=True, exist_ok=True)
    query_fasta = folder / "query.faa"
    target_fasta = folder / "target.faa"
    create_fasta(query_protein, query_fasta, multiple=False)
    create_fasta(target_proteins, target_fasta, multiple=True)
    blast_results = folder / "blast_results.txt"
    blast_cmd = [
        "blastp",
        "-query",
        str(query_fasta),
        "-subject",
        str(target_fasta),
        "-out",
        str(blast_results),
        "-outfmt",
        "6",
    ]
    subprocess.run(blast_cmd, check=True)
    blast_df = parse_blast(blast_results)
    blast_df_nhits = blast_df.iloc[:n_hits, :]
    return target_proteins[target_proteins.Contig.isin(blast_df_nhits.hit_id)]


def get_best_alignment(
    query_protein: pd.Series,
    target_proteins: pd.DataFrame,
    output_path: pathlib.Path,
    n_hits: int = 10,
) -> tuple:
    """
    Get the best alignment for a query protein among target proteins

    Parameters
    ---------
    query_protein : pd.Series
        The query protein to be aligned along with RGI information
        This is the resistance marker extracted from the antibiotic BGC
    target_proteins : pd.DataFrame
        The target proteins to be aligned against (along with RGI information)
        These are resistance markers extracted from the target genome
    output_path : pathlib.Path
        The path to the output directory
    n_hits : int
        The number of top blast hits to use for global alignment
        Default value is 10

    Returns
    ------
    tuple
        Tuple containing alignment object and alignment score
    """
    best_score = 0
    best_alignment = tuple()
    best_id = ""
    blastp_target_proteins = perform_blast(
        query_protein, target_proteins, output_path, n_hits=n_hits
    )
    if blastp_target_proteins.empty:
        return best_alignment, best_score, best_id
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -15.00  # -10
    aligner.extend_gap_score = -6.67  # -0.5
    for ind, target_protein in blastp_target_proteins.iterrows():
        alignments = aligner.align(
            query_protein.Predicted_Protein, target_protein.Predicted_Protein
        )
        alignment = max(alignments, key=lambda a: a.score)  # type: ignore
        score = alignment.score  # type: ignore
        if score > best_score:
            best_score = score
            best_alignment = alignment
            best_id = target_protein.Contig
    return best_alignment, best_score, best_id


# FIXME: Make sure that the top hits are not just subsequences but bigger protein matches
# Also, reconsider evalue thresholds
def main(
    query_file: str, target_file: str, perform_filter: bool, output_dir: str
) -> float:
    output_path = pathlib.Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    # Parse the RGI file using pandas and get the prediction proteins for each
    query_proteins = parse_rgi(query_file)
    target_proteins = parse_rgi(target_file)
    # For each query protein do global alignment with every target protein
    alignment_data = []
    for ind, query_protein in query_proteins.iterrows():
        # Get the best alignment score for each query protein
        print(f"{ind}: Aligning {query_protein.Contig}")
        if perform_filter:
            # Filter target proteins using AMR Gene Family
            filtered_target_proteins = target_proteins.loc[
                target_proteins["AMR Gene Family"] == query_protein["AMR Gene Family"],
                :,
            ]
        else:
            filtered_target_proteins = target_proteins
        alignment, score, best_id = get_best_alignment(
            query_protein, filtered_target_proteins, output_path
        )
        alignment_data.append(
            {
                "query_id": query_protein.Contig,
                "target_id": best_id,
                "alignment": alignment,
                "score": score,
            }
        )
    alignment_df = pd.DataFrame(alignment_data)
    alignment_df.to_csv(output_path / "alignment_scores.csv", index=False)
    # Get the average score for all query proteins => metric
    scores_avg = alignment_df.score.mean()
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
    PARSER.add_argument(
        "--output_dir",
        type=str,
        help="Path to the output directory",
    )
    PARSER.add_argument(
        "--filter",
        action="store_true",
        help="Whether to use AMR Gene Family to filter target proteins",
    )
    ARGS = PARSER.parse_args()
    query_rgi_file = ARGS.query_rgi_file
    target_rg_file = ARGS.target_rgi_file
    perform_filter = ARGS.filter
    output_dir = ARGS.output_dir

    main(query_rgi_file, target_rg_file, perform_filter, output_dir)
