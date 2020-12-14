#!/bin/bash
#SBATCH --time=70:00:00
#SBATCH --mem=128000
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --partition=regular
#SBATCH --job-name=sme_god-components

module load Python/3.6.4-foss-2018a
pip3 install -r requirements.txt --user
python3 find_gcs.py
