# This file is simply a collection of commands to be manually executed in a terminal

# Remove text info
conda remove --name text_info --all -y

# Create a text_info environment in anaconda3
conda create -n text_info python=3.7

# Activate text_info
conda activate text_info

# Instll packages
pip install pandas
pip install beautifulsoup4
pip install scipy
pip install numpy
