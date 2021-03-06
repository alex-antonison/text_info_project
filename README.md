# Scraping, Analyzing, and Visualizing Mining Fatality Reports

## Team Members

- Alexander Antonison (ada4) - Team Lead
- Sai Rao (sairao2)
- Amartya Roy Chowdhury (amartya4)

## Presentation Slides

The presentation slides can be viewed here: [Scraping, Analyzing, and Visualizing Mining Fatality Reports Presentation](https://docs.google.com/presentation/d/1ihBSnO-p16Uv5S7562miP8eP0OeEq_xLSv_Jzva0GWY/edit?usp=sharing)

The video of the presentation can be viewed here: [Scraping, Analyzing, and Visualizing Mining Fatality Reports Video](https://drive.google.com/file/d/1HFknuYEFxGMHaN-37iJHVYMWQCG4lvgs/view?usp=sharing)

## Purpose

Our project aims to create a user friendly display of MSHA (Mining Safety and Health Administration) fatality reports in a manner that allows the user to quickly assess information in a manner that does not require them to peruse hundreds of reports spanning dozens of pages to identify if a particular mining area or type of mine sees higher incidence of issues over time.
We scraped data available on the MSHA fatality reports site and use the classification metadata to collate and present on a heat map of the USA, where users can specify time frames that will appropriately display reported fatalities for that time period.

## Targeted Audience

The target audience is expected to be twofold - first, it would appeal to miners who work in surface or underground mines and before they take on any assignments can check if the area that they are planning to work in has higher fatality trends than other areas. This would hopefully encourage them to perform a more detailed analysis of the circumstances surrounding the incident(s) and would help them make informed decisions.
The second target audience set would be the government agency itself, MSHA, as they do not seem to currently have any dashboards for public consumption that would let folks view consolidated data over time. They only have canned reports that run per year and it would require a deep dive into multiple pdfs to truly get a bigger picture or identify any trends that might eventually require additional legislation.

## Technology Overview

This project has four main parts to it.  

1. The first part involves scraping the fatality reports from the [msha.gov](https://www.msha.gov/).
2. The second part involves writing a text processing script that will take the raw web scraped report data and transform it into a tabular format for data visualization.  
3. The third part involves performing text analysis on the report text in order to gain additional insights into the fatalities.
4. The fourth and final part is building data visualizations to allow for an end user to explore the scraped and analyzed data.

## Implementation Details

### Web Scraping

The webscraper, [scrapery.py](scraper.py), part of the project was built using a combination of the python packges [selenium](https://selenium.dev/) and [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [chromedriver](https://chromedriver.chromium.org/downloads) for the WebDriver.

- `selenium` was used with the `chromedriver` in order to navigate to the desired websites and pull down the html to then be processed.
- `beautifulsoup4` was used in order to parse the html and pull out desired information from the fatality reports.

Additionally, `json` and `logging` were used.  

- `json` was used in order to save the results to a json file for later processing.
- `logging` was used in order to log actions and errors for debugging and development purposes.

The web scraper was built by creating a single class, `Scraper` that was initialized by passing in the path to the chromedriver and a flag to indicate if all pages want to be pulled or just the first page for development or demonstration purposes.  Under the `__init__` function, a series of html classes and divs were set in order to support scraping different aspects of the fatality reports.  Additionally the chrome webdriver is initialized based on the passed in driver path with the `headless` option set to true.

The three main methods are the `get_report_pages()`, `scrape_fatality_reports()`, and `save_report()`.  The `get_report_pages()` goes through and finds the different report keys for each fatality report.  This could then be used in combination with the base url, `https://www.msha.gov`, in order to access each individual report page.  Once the report keys were gathered, the `scrape_fatality_reports()` method would extract the information it could from the main website and then use additional support methods to pull in the public notice, preliminary report, fatality alert, and the final report if they existed for this given fatality.  This aspect proved challenging as logic had to be put in place to account for some mining fatalities that did not include all of this information.  Once all of the reports were gathered, the `save_report()` method was used to dump the scraped fatality report information to `data/report_info.json`.  A json format was used in order to allow for easy saving and storing of the raw webscraped data.  The following text pre-processing section will then transform it into a more analysis and visualization tabular format.

### Text Processing

In the text processing script, [text_processing.py](text_processing.py), using the `pandas` library, I read in the `data/report_info.json` file and process the file with two main methods.  The first method, `create_base_report()`, pulls out the following text columns:

- **report-key**: This is a unique key to identify each report.
- **report-url**: The url to the fatality report.
- **accident-classification**: The classification of the accident
- **location**: The unprocessed location text.
- **mine-type**: The type of mine.
- **mine-controller**: The controller over the mine.
- **mined-mineral**: The mineral that is being mined.
- **incident-data**: The date the fatality occurred.
- **locationed-processed**: This is where I took the last value from the location in order to get the state.
- **state**: Using the `reference/state_mapping.csv` file, I mapped the correct state.

The second main method is the `extract_final_report_description()` where I pull out the Description of the Accident from the Final Report.  Since there are multiple sections within the final report and there are two different ways this section is labeled in the Final Report, I loop through each report and pull out whether it is `description of accident` or `description of the accident`.  Once extracted, I only keep the letters and spaces.  

Once the single value columns and the Description of Accident have been extracted, I will merge these together and save them to a pipe delimited csv file at `data/base_fatality_reports.csv`.

### Text Analysis

In the text analysis,[data_extraction.py][test_data_analysis.py], using panda , numpy I craeted the file final_Report.csv.
This file later use for test data analysis where we use wordcloud, sklearn, pyplot and use Wordcloud and CountVectorizer

These are the steps followed while doing the text analysis :
    1. Getting each column for processing
    2. Adding those and creating a word cloud to check the max occurance
    3. Showing a graph and plaotting it based on the 10 most common use words
    4. Performing LDA based on the column with number of words and number of topic

I have performed the above mentioned steps on the following column that we got it from the 
    #   doing text analysis for the location
    doing_data_analysis(candidate_col['location'],'location',5,1)
    #   doing text analysis for the preliminary-report
    doing_data_analysis(candidate_col['preliminary-report'],'report',5,10)
     #   doing text analysis for the mine-type
    doing_data_analysis(candidate_col['mine-type'],'mine-type',5,1)
     #   doing text analysis for the mine-controller
    doing_data_analysis(candidate_col['mine-controller'],'mine-controller',5,10)
     #   doing text analysis for the accidnet-classification
    doing_data_analysis(candidate_col['accidnet-classification'],'accidnet-classification',5,10)
     #   doing text analysis for the fatality-alert
    doing_data_analysis(candidate_col['fatality-alert'],'fatality-alert',5,50)
    
Visual results of the analysis can be seen here: [Text Analysis](https://docs.google.com/presentation/d/1fxkN5NJBxpQoWd3jC5f8moAVshV1y13IscYCLTyZIVE/edit?usp=sharing)

### Data Visualization

Using the `data/base_fatality_reports.csv` file, I imported it into Tableau and created a dashboard and public it to Tableau Public - [Mining Fatality Report Dashboard](https://public.tableau.com/profile/alexander.d.antonison#!/vizhome/MiningFatalityReportsDashboard/MiningFatalityReportDashboard).

In this dashboard, I created the following visuals:

- **Fatality by State** - This is a heat map that shows the states that have the most and least amount of reported fatalities.  If you are interested at looking at the fatality reports for a given state, you can select it in the map it will filter the other visuals as well.
- **Accident Classification** - A bar graph showing the amounts of each type of accident.
- **Mine Controller** - A bar that shows the amount of fatalities by each mine controller.
- **Fatalities over Time** - A line graph that shows the amount of trend of reported fatalities over time.

## Team Contribution

### Alex Antonison (ada4)

- Alex helped write the project proposal by specifying the technologies and methodologies to be used as well as provide a rough timeline.
- Alex wrote the web scraper that pulled all of the fatality reports into a json document.
- Alex developed a text processing script that processed the web-scraped results into a csv file for analysis and data visualization.
- Alex created a tableau dashboard of the scraped data.
- Alex helped write the documentation around the code submission with an emphasis on the web scraping section, text processing, and a dashboard of results.

### Amartya Roy Chowdhury (amartya4)

- Amartya helped write the proposal by researching existing solutions within this space as well as seeing if there were any existing resources we could use in order to gain better insights into mining fatalities.
- Amartya performed text and topic analysis on the description of the accident from the fatality report.
- Amartya helped write the documentation around the code submission with an emphasis on the text and topic analysis section.

### Sai Rao (sairao2)

- Sai helped write the project proposal by writing the function of the tool, who will benefit from the tool, and how we will demonstrate the usefulness of the tool.
- Sai came up with the overall project idea and acted as a subject matter expert as he works in the mining industry.
