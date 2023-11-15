#!/usr/bin/env bash

mkdir -p ~/tmp
cd ~/tmp || exit

# export PATH="/micromambaforge/bin:$PATH"
export MAMBA_ROOT_PREFIX=~/micromamba
eval "$(micromamba shell hook --shell bash)"
micromamba create -n antismash -c conda-forge python=3.9
micromamba activate antismash

# Install deps via conda (https://docs.antismash.secondarymetabolites.org/install/)
micromamba install -c bioconda -c conda-forge hmmer2 hmmer diamond=2.0.14 fasttree prodigal blast muscle glimmerhmm

wget https://dl.secondarymetabolites.org/releases/7.0.1/antismash-7.0.1.tar.gz &&
    tar -zxf antismash-7.0.1.tar.gz

micromamba activate antismash
pip install ./antismash-7.0.1
download-antismash-databases && antismash --prepare-data
