#!/usr/bin/env bash

mkdir -p ~/tmp
cd ~/tmp || exit

export MAMBA_ROOT_PREFIX=~/micromamba
eval "$(micromamba shell hook --shell bash)"
micromamba create --name rgi --channel conda-forge --channel bioconda --channel defaults rgi
micromamba install --channel conda-forge --channel bioconda --channel defaults rgi

micromamba activate rgi

# # Autoload databases
# rgi auto_load

# Load the latest AMR reference database
wget https://card.mcmaster.ca/latest/data && tar -xvf data ./card.json
rgi load --card_json card.json
