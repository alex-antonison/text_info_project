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
wget https://chromedriver.storage.googleapis.com/index.html?path=76.0.3809.126/

mkdir ../chromedriver_77/
cd ../chromedriver_77/
wget https://chromedriver.storage.googleapis.com/index.html?path=77.0.3865.40/

mkdir ../chromedriver_78/
cd ../chromedriver_78/
wget https://chromedriver.storage.googleapis.com/index.html?path=78.0.3904.11/