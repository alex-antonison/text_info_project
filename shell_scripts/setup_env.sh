#!/bin/bash
########
# before running script, be in your base env 
# you can activate base with the following command:
# conda activate base
######
conda remove --name text_info --all -y
conda env create -f ../environment.yml