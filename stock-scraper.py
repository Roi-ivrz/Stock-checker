from selenium import webdriver
from time import sleep

PATH = 'C:\Program Files (x86)\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(PATH, options=options)
def getPrice(name):
    driver.get('https://finance.yahoo.com/quote/' + str(name) + '?')
    price = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div/div/span[1]')
    price = price.text
    return price

priceList = []
for i in range (3):
    priceList.append(str(getPrice('NVDA')))
    sleep(3)
driver.close()
print(priceList)