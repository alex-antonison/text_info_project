from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from json import dumps
import logging 
import sys

logging.basicConfig(filename="output.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 
logger=logging.getLogger() 
logger.setLevel(logging.INFO) 

class Scraper(object):
    
    def __init__(self, driver_path, get_all_flag):
        self.driver_path = driver_path
        self.get_all_flag = get_all_flag
        
        # initialize list for report links
        self.report_key = []

        # initialize dict for report info
        self.report_info = {}

        # setup links
        self.base_url = "https://www.msha.gov"
        self.reports_url_base = "https://www.msha.gov/data-reports/fatality-reports/search"
        self.reports_url_page = "https://www.msha.gov/data-reports/fatality-reports/search?page={page_num}"

        # div classes
        self.accident_div = "views-field views-field-field-accident-classification"
        self.location_div = "views-field views-field-field-location-at-fatality"
        self.mine_type_div = "views-field views-field-field-mine-category-1"
        self.mine_controller_div = "views-field views-field-field-mine-controller-1"
        self.mined_mineral_div = "views-field views-field-field-primary-sic-1"
        self.incident_date_div = "views-field views-field-field-arep-fatal-date"

        # public context class
        self.public_content_class = "block block-views block-arep-fatal-block-4 block-views-arep-fatal-block-4 even"

        # preliminary report
        self.preliminary_report_class = "field field-name-body field-type-text-with-summary field-label-above"

        # check for chargeback
        self.chargeback_div = "views-field views-field-field-arep-fatal-cb-desc"

        # fatality report items
        self.fatality_report_item_class = "field field-name-field-arep-fatal-fatalgram-bp field-type-text-long field-label-above"
        
        # final report items
        self.final_report_class = "field field-name-body field-type-text-with-summary field-label-hidden"
        
        # initialize browser
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(self.driver_path, options=options)
        
    def get_js_soup(self, url):
        """
        This function uses the selenium browser to reach out to a web page
        and bring back all of the html text in a soup object.
        (Source) This function was taken from the MP2 part1 scraper assignment
        Arguments:
            url {string} --  The url of a website that you want the html returned
        
        Returns:
            soup object -- A beautiful soup
        """
        self.browser.get(url)
        res_html = self.browser.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(res_html,'html.parser')
        return soup

    def get_report_keys(self, soup):
        """
        This method takes in the soup from a report page and iterates through
        to pull all of the report keys out of a given page.
        
        Arguments:
            soup {bs4.object} -- The returned soup for a given report page
        """
        reports = soup.find('ul', {'class': 'fatalities-list'}).find_all('a', href=True)
        for item in reports:
            if str(item).count("/") == 5:
                if str(item).count("class") == 0:
                    # append to report_key
                    self.report_key.append(item['href'])

    def get_report_pages(self):
        """
        This method is used to iterate through all of the report
        pages from the fatalities website and gather all of the report keys.
        If the `get_all_flag` is set to false, only the first page of reports
        will be pulled and then scraped.  This is suggested for demonstration and development
        purposes.
        """
        logger.info("Getting report pages...")
        # Get reports for base url
        report_soup = self.get_js_soup(self.reports_url_base)
        self.get_report_keys(report_soup)

        # Get the different pages 
        if self.get_all_flag == True:
            page_number = 1
            while True:
            
                try:
                    report_url = self.reports_url_page.replace("{page_num}", str(page_number))
                    report_soup = self.get_js_soup(report_url)
                    self.get_report_keys(report_soup)
                    
                except:
                    break
                logger.info(report_url)
                page_number += 1
    
    def get_section_div(self, soup, div_class):
        """
        This is a general method that when provided a class within a div,
        it will return the text contents.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
            div_class {string} -- The desired html element to have its text returned
        
        Returns:
            [string] -- The desired text for a given div + class combination
        """
        div_soup = soup.find('div', {'class': div_class})
        return div_soup.find('span', {'class': 'field-content'}).text

    def get_date(self, soup):
        """
        This gets the date for a given fatality.  This varies slightly from
        the other information being pulled as we wanted the content since the date
        was formatted in a way that lends itself better for processing.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            string -- A date of the fatality report
        """
        div_soup = soup.find('div', {'class': self.incident_date_div})
        return soup.find('span', {'class': 'date-display-single'})['content']

    def is_invalid_report(self, soup):
        """
        There are some reports that are not valid reports that should be
        ignored.  This method starts with setting that flag to false
        and then performs necessary checks and if any of the checks
        succeed, set the flag to True.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            bool -- True/False depending on if the report is valid or not
        """
        # This class looks for invalid reports
        # Assume report is valid unless it meets an invalid criteria
        invalid_report_flag = False
        
        # If there is a rescission, do not want to include this report
        invalid_soup = soup.find('div', {'class': self.chargeback_div})      
        if invalid_soup != None:
            text = invalid_soup.find('span', {'class': 'field-content'}).text.find('Rescission')
            if text != -1:
                invalid_report_flag = True
                logger.info("Report was a rescission...")

        # No location information provided since invalid report
        if self.get_section_div(soup, self.location_div) == "No Information, No Information":
            invalid_report_flag = True
            logger.info("No location information in report...")

        return invalid_report_flag

    
    def get_preliminary_report(self, soup):
        """
        This method gets the preliminary report by processing the fatality report
        page to find the url embedded within it.  Since there is sometimes an inconsistent
        method in how the url is named, it could not be progamatically determined.
        Since not all fatality reports have a preliminary report, a try-catch
        is used to attempt to get it and in the event of a failure, it is assumed
        there is not a preliminary report.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            string -- The text for the preliminary report
        """
        try:
            # get url for preliminary report
            preliminary_report_key = soup.select_one("a[href*=preliminary-report]")['href']
            preliminary_report_url = self.base_url + preliminary_report_key
            soup = self.get_js_soup(preliminary_report_url)
            prelim_report_soup = soup.find('div', {'class': self.preliminary_report_class})
            return prelim_report_soup.find('div', {'class': 'field-item even'}).text
        except:
            logger.info("No preliminary report...")
            return None

    def get_fatality_alert(self, soup):
        """
        This method first finds the fatality alert URL within the fatality report page and then
        pulls the text.  Since this includes a summary, additional_inof, and best practices section,
        each is returned as a dictionary to allow for individual parsing.
        Since not all fatality reports have a fatality alert, a try-catch
        is used to attempt to get it and in the event of a failure, it is assumed
        there is not a fatality alert.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            dictionary -- The three sections of fatality alert
        """
        # Not all reports have a fatality alert
        # if not, just return none
        try:
            fatality_alert_key = soup.select_one("a[href*=fatality-alert]")

            if fatality_alert_key == None:
                # sometimes the URL is slightly different
                fatality_alert_key = soup.select_one("a[href*=fatality\%20alert]")

            fatality_alert_url = self.base_url + fatality_alert_key['href']
        
            fatality_alert = {}
            # get paragraph text
            soup = self.get_js_soup(fatality_alert_url)
            p = soup.find_all('p')
            fatality_alert.update({'summary': p[0].text})
            fatality_alert.update({'additional_info': p[1].text})
            # get best practice text
            best_practice_list = soup.find('div', {'class' : self.fatality_report_item_class})
            best_practice_list_text = [x.text for x in best_practice_list.find_all('li')]
            best_practice_text = ''.join(best_practice_list_text)
            fatality_alert.update({'best-practices': best_practice_text})

            return fatality_alert
        except:
            logger.info("No fatality alert...")
            return None

    def get_final_report(self, soup):
        """
        This method first finds the url for the final report and then pulls
        all of the text for each section and stores it into the appropriate portion
        of the dictionary.  In order to make this flexible, a loop was created that
        simply went through each element in the html and when it encountered
        a header, would change the section that the text was being nested under.
        Since not all fatality reports have a final report, a try-catch
        is used to attempt to get it and in the event of a failure, it is assumed
        there is not a final report.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            dictionary -- A dictionary with all of the sections of a final report
        """
        section_of_interest = ['OVERVIEW', 'GENERAL INFORMATION', 'DESCRIPTION OF ACCIDENT',
                               'DESCRIPTION OF THE ACCIDENT', 'INVESTIGATION OF THE ACCIDENT', 
                               'INVESTIGATION OF ACCIDENT', 'DISCUSSION', 
                               'TRAINING AND EXPERIENCE', 'ROOT CAUSE ANALYSIS', 
                               'CONCLUSION', 'ENFORCEMENT ACTIONS']
        section_of_interest = [x.lower() for x in section_of_interest]

        try:
            final_report_key = soup.select_one("a[href*=final-report]")['href']
            final_report_url = self.base_url + final_report_key

            # some fatalities may not have a final report, if so, return None
            soup = self.get_js_soup(final_report_url)
            soup = soup.find('div', {'class', self.final_report_class})
            soup = soup.find('div', {'property': 'content:encoded'})
            
            if soup.text.find('Please check the URL for proper spelling and hyphenation') != -1:
                logger.info("No final report...")
                return None

            # setup for processing final report
            final_report = {}
            # the first content of the report
            # will be header text
            current_header = 'header'
            # initialize current section text
            current_section_text = ''
            # loop through each element to place appropriate
            # content under each header
            for item in soup.find_all(['p','h2','div']):
                # some elements do not have text
                # easier to just use a try catch
                # to skip over the errored elements
                try:
                    # this is for non-header text
                    if item.text.lower() not in section_of_interest:
                        current_section_text = current_section_text + item.text.lower()
                    # this is to capture headers
                    if item.text.lower() in section_of_interest:
                        final_report.update({current_header: current_section_text})
                        current_section_text = ''
                        current_header = item.text.lower()
                except:
                    continue
            logger.info("Final report key count: %s", len(final_report.keys()))
            return final_report
        except:
            logger.info("No final report...")
            return None

    def get_public_notice(self, soup):
        """
        This method pulls the public notice information from the fatality report page.
        A try-catch is used since some fatality reports do not have a public notice.
        
        Arguments:
            soup {bs4.object} -- The soup for a given fatality report
        
        Returns:
            string -- The text for a public notice of a fatality report
        """
        try:
            public_class_soup = soup.find('section', {'class': self.public_content_class})
            return public_class_soup.find('div', {'class': 'field-content'}).text
        except:
            logger.info("No public notice...")

    def get_report_info(self, report_key):
        """
        This method takes in a report_key and then constructs the report dictionary
        that will later be stored in the json output file.
        It first gets the soup from the report page and then passes that soup
        into all of the other helper methods to construct the dictionary.  Once constructed
        the report info will be appended to the `report_info` dictionary.
        
        Arguments:
            report_key {string} -- The given report_key for a fatality report
        """
        url = self.base_url + report_key
        logger.info(url)
        soup = self.get_js_soup(url)
        
        if self.is_invalid_report(soup) == False:
            report_info = {
                report_key:
                {
                    'report-url': url,
                    'accidnet-classification': self.get_section_div(soup, self.accident_div),
                    'location': self.get_section_div(soup, self.location_div),
                    'mine-type': self.get_section_div(soup, self.mine_type_div),
                    'mine-controller': self.get_section_div(soup, self.mine_controller_div),
                    'mined-mineral': self.get_section_div(soup, self.mined_mineral_div),
                    'incident-date': self.get_date(soup),
                    'public-notice': self.get_public_notice(soup),
                    'preliminary-report': self.get_preliminary_report(soup),
                    'fatality-alert': self.get_fatality_alert(soup),
                    'final-report': self.get_final_report(soup)
                }
            }
            self.report_info.update(report_info)

    def scrape_fatality_reports(self):
        """
        This method loops through all of the report keys to pass into the
        `get_report_info` method that will scrape the fatality reports
        and then add it to the `report_info` dictionary.
        """
        logger.info("Scraping the reports...")
        index = 0
        for item in self.report_key:
            self.get_report_info(item)
            index += 1
            if index%30 == 0:
                logger.info("Scraping report number: " + str(index))

    def save_reports(self, file_location):
        """
        This method takes care of storing the scraped web pages in a json file
        
        Arguments:
            file_location {string} -- where the scraped web pages are stored in json format
        """
        logger.info("Saving reports to " + file_location)
        json = dumps(self.report_info)
        f = open(file_location, "w")
        f.write(json)
        f.close()

def main():
    
    ## Command line arguments
    chrome_driver_path_arg = sys.argv[1]
    get_all_flag_arg = sys.argv[2]

    if get_all_flag_arg == "True":
        get_all_flag_input = True
    if get_all_flag_arg == "False":
        get_all_flag_input = False

    logger.info("Starting web scraping...")

    ## Initialize the scraper object
    scraper = Scraper(driver_path = chrome_driver_path_arg, get_all_flag = get_all_flag_input)

    ## Get the different report page keys
    scraper.get_report_pages()

    ## Scrape the fatality reports
    scraper.scrape_fatality_reports()
    
    ## Once done, save to the data/ folder
    ## This will overwrite an existing report_info.json file
    scraper.save_reports("data/report_info.json")


if __name__ == "__main__":
    main()
    