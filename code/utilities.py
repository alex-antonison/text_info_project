from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options


def setup_web_driver():
    options = Options()
    options.headless = True
    
    print("Establishing chromedriver")
    browser = webdriver.Chrome('../chromedriver/chromedriver', options=options)

    return browser


def get_js_soup(url,browser):
    browser.get(url)
    res_html = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser')
    return soup

def get_report(soup):
    return soup.find('ul', {'class': 'fatalities-list'}).find_all('a', href=True)

def extract_href_url(reports, reports_list):
    for item in reports:
        if str(item).count("/") == 5:
            if str(item).count("class") == 0:
                reports_list.append(item['href'])
    return reports_list
