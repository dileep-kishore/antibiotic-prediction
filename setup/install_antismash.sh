#!/usr/bin/env bash

mkdir -p /tmp
cd /tmp || exit

# Install deps via Debian/Ubuntu (https://docs.antismash.secondarymetabolites.org/install/)
# wget http://dl.secondarymetabolites.org/antismash-stretch.list -O /etc/apt/sources.list.d/antismash.list &&
#     wget -q -O- http://dl.secondarymetabolites.org/antismash.asc | apt-key add -
# apt-get update &&
#     apt-get -y install hmmer2 hmmer diamond-aligner fasttree prodigal ncbi-blast+ muscle glimmerhmm

# export PATH="/micromambaforge/bin:$PATH"
micromamba create -n antismash python=3.9
micromamba activate antismash

# Install deps via conda (https://docs.antismash.secondarymetabolites.org/install/)
micromamba install -c bioconda hmmer2 hmmer diamond=2.0.14 fasttree prodigal blast muscle glimmerhmm

wget https://dl.secondarymetabolites.org/releases/7.0.1/antismash-7.0.1.tar.gz &&
    tar -zxf antismash-7.0.0.tar.gz

pip install ./antismash-7.0.1
download-antismash-databases && antismash --prepare-data
