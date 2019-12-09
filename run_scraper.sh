#!/bin/bash

## Activating the virtualenv text_info
source ~/.virtualenvs/text_info/bin/activate

## First argument should point to the desired
## chromedriver to be used

## Second argument is set to false to prevent scraping all
## of the 430+ reports.  For demonstration purposes you can see 
## around the first 30 pages scraped.

python scraper.py chromedriver/chromedriver False