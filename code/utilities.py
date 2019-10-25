from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options


def setup_web_driver():
    options = Options()
    options.headless = True
    
    print("Establishing chromedriver 76")
    browser = webdriver.Chrome('../chromedriver_76/chromedriver',options=options)

    return browser


def get_js_soup(url,browser):
    browser.get(url)
    res_html = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    return soup
