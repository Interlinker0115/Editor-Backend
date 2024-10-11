from selenium import webdriver
from selenium.webdriver.chrome.options import Options

url = 'http://clerk.com'
chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)


