#!/usr/bin/env bash

AB_BGC=$1      # Path to BGC gbk file
GENOME_BGCS=$2 # Path to genome (BGC) gbk file

# Step 1: Run clinker
nix develop
echo "Running clinker"
clinker "$AB_BGC" "$GENOME_BGCS" -i 0.0 -o alignments.csv -dl "," -dc 4 -p plot.html -ha -mo matrix.txt

# Step 2: Parse alignments.csv
# TODO: Parse alignments.csv and filter out similar BGCs (e.g. > 90% identity)

# Step 3: Run RGI on antibiotic BGC
BGC=$(basename "$AB_BGC" .gbk)
python gbk2fasta.py "$AB_BGC" "$BGC".fna
# QUESTION: Can you use docker compose with/on KBase?
docker run -v $PWD/outputs:/outputs finlaymaguire/rgi main -i /outputs/"$BGC".fna -o /outputs/rgi/"$BGC" --include_loose --clean

# Step 4: Use biopython.blast to compare resistance markers on antibiotic BGC to full genome (rgi folder)
