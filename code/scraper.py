from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from json import dumps

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

        # preliminary report class
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
        """[summary]
        This function uses the selenium browser to reach out to a web page
        and bring back all of the html text in a soup object
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
        reports = soup.find('ul', {'class': 'fatalities-list'}).find_all('a', href=True)
        for item in reports:
            if str(item).count("/") == 5:
                if str(item).count("class") == 0:
                    # append to report_key
                    self.report_key.append(item['href'])

    def get_report_pages(self):
        print("Getting report pages...")
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
                print(report_url)
                page_number += 1
    
    def get_section_div(self, soup, div_class):
        div_soup = soup.find('div', {'class': div_class})
        return div_soup.find('span', {'class': 'field-content'}).text

    def get_date(self, soup):
        div_soup = soup.find('div', {'class': self.incident_date_div})
        return soup.find('span', {'class': 'date-display-single'})['content']

    def is_invalid_report(self, soup):
        # This class looks for invalid reports
        # Assume report is valid unless it meets an invalid criteria
        invalid_report_flag = False
        
        # If there is a rescission, do not want to include this report
        invalid_soup = soup.find('div', {'class': self.chargeback_div})      
        if invalid_soup != None:
            text = invalid_soup.find('span', {'class': 'field-content'}).text.find('Rescission')
            if text != -1:
                invalid_report_flag = True
                print("Report was a rescission...")

        # No location information provided since invalid report
        if self.get_section_div(soup, self.location_div) == "No Information, No Information":
            invalid_report_flag = True
            print("No location information in report...")

        return invalid_report_flag

    
    def get_preliminary_report(self, url):
        preliminary_report_url = url + '/preliminary-report'
        try:
            soup = self.get_js_soup(preliminary_report_url)
            prelim_report_soup = soup.find('div', {'class': self.preliminary_report_class})
            return prelim_report_soup.find('div', {'class': 'field-item even'}).text
        except:
            return None

    def get_fatality_alert(self, url):
        fatality_alert_url = url + '/fatality-alert'
        fatality_alert = {}
        try:
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
            return None

    def get_final_report(self, url):
        final_report_url = url + '/final-report'
        # some fatalities may not have a final report, if so, return None
        
        soup = self.get_js_soup(final_report_url)
        soup = soup.find('div', {'class', self.final_report_class})
        soup = soup.find('div', {'property': 'content:encoded'})
        
        if soup.text.find('Please check the URL for proper spelling and hyphenation') != -1:
            return None

        # setup for processing final report
        final_report = {}
        # the first content of the report
        # will be header text
        current_header = 'HEADER'
        # initialize current section text
        current_section_text = ''
        # loop through each element to place appropriate
        # content under each header
        for item in soup.contents:
            # some elements do not have text
            # easier to just use a try catch
            # to skip over the errored elements
            try:
                if str(item).find('h2') == -1:
                    current_section_text = current_section_text + item.text
                if str(item).find('h2') != -1:
                    final_report.update({current_header: current_section_text})
                    current_section_text = ''
                    current_header = item.text
            except:
                continue
        return final_report



    def get_public_notice(self, soup):
        public_class_soup = soup.find('section', {'class': self.public_content_class})
        return public_class_soup.find('div', {'class': 'field-content'}).text

    def get_report_info(self, report):
        url = self.base_url + report
        print(url)
        soup = self.get_js_soup(url)
        
        if self.is_invalid_report(soup) == False:
            report_info = {
                report:
                {
                    'report-url': url,
                    'accidnet-classification': self.get_section_div(soup, self.accident_div),
                    'location': self.get_section_div(soup, self.location_div),
                    'mine-type': self.get_section_div(soup, self.mine_type_div),
                    'mine-controller': self.get_section_div(soup, self.mine_controller_div),
                    'mined-mineral': self.get_section_div(soup, self.mined_mineral_div),
                    'incident-date': self.get_date(soup),
                    'public-notice': self.get_public_notice(soup),
                    'preliminary-report': self.get_preliminary_report(url),
                    'fatality-alert': self.get_fatality_alert(url),
                    'final-report': self.get_final_report(url)
                }
            }
            self.report_info.update(report_info)

    def scrape_fatality_reports(self):
        print("Scraping the reports...")
        index = 0
        for item in self.report_key:
            self.get_report_info(item)
            index += 1
            if index%30 == 0:
                print("Scraping report number:", str(index))

    def save_reports(self, file_location):
        print("Saving reports to ", file_location)
        json = dumps(self.report_info)
        f = open(file_location, "w")
        f.write(json)
        f.close()

def main():
    print("Starting web scraping...")
    scraper = Scraper("chromedriver/chromedriver", get_all_flag = True)
    # Get the different report page keys
    scraper.get_report_pages()
    scraper.scrape_fatality_reports()
    scraper.save_reports("data/report_info.json")
    # scraper.get_report_info("/data-reports/fatality-reports/2018/fatality-8")


if __name__ == "__main__":
    main()
    