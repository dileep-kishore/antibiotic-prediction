#!/usr/bin/env bash

INPUT_FILE=$1
OUTPUT_DIR=$2

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir "$OUTPUT_DIR"
fi

echo "Running antismash on $1"

antismash "$INPUT_FILE" \
    --fullhmmer \
    --cpus 1 \
    --genefinding-tool prodigal \
    --output-dir "$OUTPUT_DIR"
