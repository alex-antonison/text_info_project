import utilities

print("Setting up web driver")
browser = utilities.setup_web_driver()

url = "https://www.msha.gov/data-reports/fatality-reports/search"

get_js_soup(url, browser)

