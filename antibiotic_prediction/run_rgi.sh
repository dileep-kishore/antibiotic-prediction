#!/usr/bin/env bash

GENOME=$1
OUTPUT_DIR=$2
GENOME_NAME=$3

micromamba deactive &>/dev/null
micromamba activate rgi

rgi main -i "$GENOME" -o "$OUTPUT_DIR/$GENOME_NAME" --include_loose --clean
