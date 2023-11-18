#!/usr/bin/env python

import argparse
import pathlib
import threading
import urllib.request


def download_file(url, filename):
    with urllib.request.urlopen(url) as response:
        with open(filename, "wb") as file:
            file.write(response.read())
    print(f"Downloaded: {filename}")


def main(genomes_file: pathlib.Path, num_threads: int):
    # List of file URLs to download
    with open(genomes_file, "r") as fid:
        file_urls = [
            f"http://www.at-sphere.com/download/assemblies/{l.strip()}.fna.gz"
            for l in fid.readlines()
            if l
        ]

    # Create a list to hold thread objects
    threads = []
    # Divide the list of URLs into chunks based on the number of threads
    chunks = [
        file_urls[i : i + num_threads] for i in range(0, len(file_urls), num_threads)
    ]

    for i, chunk in enumerate(chunks):
        percentage_completed = (i + 1) / len(chunks) * 100
        for url in chunk:
            # Extract the file name from the URL
            filename = url.split("/")[-1]
            # Create a thread for each file download
            thread = threading.Thread(target=download_file, args=(url, filename))
            # Add the thread to the list
            threads.append(thread)
            # Start the thread
            thread.start()

        # Wait for all threads to finish before moving to the next chunk
        for thread in threads:
            thread.join()
        print(f"Finished downloading {percentage_completed}% of the data")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Download genomes from AT-SPHERE")
    PARSER.add_argument(
        "genomes_file",
        type=str,
        help="Path to the file containing the list of genomes to download",
    )
    PARSER.add_argument(
        "--num_threads",
        type=int,
        default=20,
        help="Number of threads to use for downloading the genomes",
    )
    ARGS = PARSER.parse_args()

    genomes_file = pathlib.Path(ARGS.genomes_file)
    if not genomes_file.exists():
        raise FileNotFoundError(f"{genomes_file} does not exist")
    num_threads = ARGS.num_threads

    main(genomes_file, num_threads)
