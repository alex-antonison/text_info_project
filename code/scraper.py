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
        
        # initialize browser
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(self.driver_path, options=options)
        
    def get_js_soup(self, url):
        self.browser.get(url)
        res_html = self.browser.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(res_html,'html.parser')
        return soup

    def get_report(self, soup):
        return soup.find('ul', {'class': 'fatalities-list'}).find_all('a', href=True)

    def get_report_keys(self, reports):
        for item in reports:
            if str(item).count("/") == 5:
                if str(item).count("class") == 0:
                    # append to report_key
                    self.report_key.append(item['href'])

    def get_report_pages(self):
        print("Getting report pages...")
        # Get reports for base url
        report_soup = self.get_js_soup(self.reports_url_base)
        reports = self.get_report(report_soup)
        self.get_report_keys(reports)

        # Get the different pages 
        if self.get_all_flag == True:
            page_number = 1
            while True:
            
                try:
                    report_url = self.reports_url_page.replace("{page_num}", str(page_number))
                    report_soup = self.get_js_soup(report_url)
                    reports = self.get_report(report_soup)
                    self.get_report_keys(reports)
                    
                except:
                    break

                page_number += 1
    
    def get_section_div(self, soup, div_class):
        div_soup = soup.find('div', {'class': div_class})
        return div_soup.find('span', {'class': 'field-content'}).text

    def get_date(self, soup):
        div_soup = soup.find('div', {'class': self.incident_date_div})
        return soup.find('span', {'class': 'date-display-single'})['content']

    def is_rescission(self, soup):
        # If there is a rescission, do not want to include this report
        recess_soup = soup.find('div', {'class': self.chargeback_div})
        
        if recess_soup != None:
            text = recess_soup.find('span', {'class': 'field-content'}).text.find('Rescission')

            if text != -1:
                # There is a rescission
                return True
            else:
                # There is not a rescission
                return False
        else:
            # There is not a rescission
            return False
    
    def get_preliminary_report(self, url):
        preliminary_report_url = url + '/preliminary-report'
        try:
            soup = self.get_js_soup(preliminary_report_url)
            prelim_report_soup = soup.find('div', {'class': self.preliminary_report_class})
            return prelim_report_soup.find('div', {'class': 'field-item even'}).text
        except:
            return None

    def get_fatality_report(self, url):
        pass

    def get_final_report(self):
        pass

    def get_public_notice(self, soup):
        public_class_soup = soup.find('section', {'class': self.public_content_class})
        return public_class_soup.find('div', {'class': 'field-content'}).text

    def get_report_info(self, report):
        url = self.base_url + report
        soup = self.get_js_soup(url)
        
        if self.is_rescission(soup) == False:
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
                    'preliminary-report': self.get_preliminary_report(url)
                }
            }
            self.report_info.update(report_info)
        else:
            print("======> Rescission Report:", url)

def main():
    print("Starting web scraping...")
    scraper = Scraper("../chromedriver/chromedriver", get_all_flag = False)
    soup = scraper.get_js_soup("https://www.msha.gov/data-reports/fatality-reports/search")
    scraper.get_report_pages()
    # scraper.get_report_info("/data-reports/fatality-reports/2014/fatality-27-june-14-2014")
    print("Getting page content...")
    for item in scraper.report_key:
        scraper.get_report_info(item)
    
    # Write reports to json file
    print("Writing reports to json file...")

    json = dumps(scraper.report_info)
    f = open("../data/report_info.json","w")
    f.write(json)
    f.close()

if __name__ == "__main__":
    main()
    