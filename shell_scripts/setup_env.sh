#!/bin/bash
########
# before running script, be in your base env 
# you can activate base with the following command:
# conda activate base
######
conda remove --name text_info --all -y
conda env create -f ../environment.yml


## downloads chrome driver
mkdir ../chromedriver_76/
cd ../chromedriver_76/
wget https://chromedriver.storage.googleapis.com/76.0.3809.126/chromedriver_linux64.zip
unzip chromedriver_linux64.zip