# Setup

## Python Setup

1. The first step in setting up this project will involve installing a version of python 3.  This can be done either through [python.org](https://www.python.org/) or via [Anaconda](https://www.anaconda.com/distribution/).
2. Install the necessary packages using the `requirements.txt` file with the following code:

```bash
pip install -r requirements.txt
```

It is suggested but not necessary to use a form of environment management such as [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io/en/latest/)

## Web Scraping Setup

1. Once python is setup, If you do not have Chrome installed, you will need to install it.  You can go to Google's support documentation around how to install it. [Install Chrome](https://support.google.com/chrome/answer/95346?co=GENIE.Platform%3DDesktop&hl=en)
2. Once you have chrome installed, you will then need to go to the chrome driver website, [Chrome Drivers](https://chromedriver.chromium.org/downloads), and download an appropriate chrome driver for your system and unzip it to the `chromedriver/` directory.
3. With python and a chrome driver setup, you will be ready to run the web scraping python script.  The [run_scraper.sh](run_scraper.sh) script is an example of how to run it with a `text_info` virutalenv environment.  The script requires two arguments.  The first argument is the path to the chrome driver and the second argument is a True or False value to indicate if you want to scrape all of the pages or just the first page.  It is recommended for development or demonstration purposes to set this to False as it takes a bit over an hour to scrape all reports.

**Note** Unable to get this web crawler working in a Windows environment.  Suggested running in Linux.

## Text Processing Setup

The [text_processing.py](text_processing.py) script only requires pandas to be installed. This would have been taken care of during the python setup.

## Text Analysis Setup

## Dashboard Usage

To demo the dashboard, all you need to do is go to [Mining Fatality Report Dashboard](https://public.tableau.com/profile/alexander.d.antonison#!/vizhome/MiningFatalityReportsDashboard/MiningFatalityReportDashboard).  From there, you can select any of the states in the heat map to filter the dashboard to that state.
