from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time
import csv
import os
from datetime import datetime
import pandas as pd
import warnings
warnings.filterwarnings('ignore')



def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options = uc.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #############################################################################
    # Create empty profile for Mac OS
    #if os.path.isdir('./chrome_profile'):
    #    shutil.rmtree('./chrome_profile')
    #os.mkdir('./chrome_profile')
    #Path('./chrome_profile/First Run').touch()
    #chrome_options.add_argument('--user-data-dir=./chrome_profile/')
    ##############################################################################
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-impl-side-painting")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-seccomp-filter-sandbox")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-cast")
    chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
    chrome_options.add_argument("--disable-cloud-import")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-session-crashed-bubble")
    chrome_options.add_argument("--disable-ipv6")
    chrome_options.add_argument("--allow-http-screen-capture")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions") 
    chrome_options.add_argument("--disable-notifications") 
    chrome_options.add_argument("--disable-infobars") 
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument('--disable-dev-shm-usaging')
############################################
    chrome_options.page_load_strategy = 'eager'
    driver = uc.Chrome(options=chrome_options)
    driver.set_page_load_timeout(120)

    return driver

def login(driver, name, pwd):

    URL = "https://b2bshop.bataindustrials.com/en-us/"
    # navigating to the website link
    while True:
        try:
            driver.get(URL)
            time.sleep(3)
            break
        except:
            driver.refresh()
            time.sleep(3)

    wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@class='top-hyp font-smaller']"))).click()
    time.sleep(3)
    # signing in 
    username = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@id='UserName' and @type='email']")))
    password = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@id='Password' and @type='password']")))
    username.send_keys(name)
    time.sleep(1)
    password.send_keys(pwd)
    time.sleep(1)
    driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(3)


def scrape_shoes(driver, data):

    URL = "https://b2bshop.bataindustrials.com/en-us/safety-shoes"
    while True:
        try:
            driver.get(URL)
            time.sleep(3)
            break
        except:
            driver.refresh()
            time.sleep(3)

    nprod = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='counter-inside']"))).text.split(' ')[0]
    URL = "https://b2bshop.bataindustrials.com/en-us/safety-shoes" + "/?count={}".format(nprod)
    driver.get(URL)
    time.sleep(3)
    # getting the list of products
    prods = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='l-products-item']")))
    iprod = 0
    for prod in prods:
        #excluding out of stock items
        iprod += 1
        print('Scraping Shoes Product {} of {}'.format(iprod, nprod))
        try:
            prod.find_element_by_css_selector("span.lbl-stock.in-stock")
            prod.find_element_by_css_selector("span.btn-cnt")
        except:
            continue
        art_num = prod.find_element_by_css_selector('a.product-title').text
        item_num = prod.find_element_by_css_selector('span.product-id-value').text
        #print(art_num, item_num)
        
        # getting stock data
        prod.find_element_by_css_selector('button.btn').click()
        time.sleep(2)
        while True:
            try:
                table = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.gvi.gvi-variants.sticky-enabled')))
                time.sleep(2)
                html = table.get_attribute('outerHTML')
                break
            except:
                time.sleep(3)

        
        df = pd.read_html(html, keep_default_na=False)[0]
        if 'unnamed' in str(df.columns[0]).lower():
            cols = df.columns[1:]
            rows = df.iloc[:, 0]
        else:
            cols = df.columns
            rows = df.index
        
        df.index = rows
        for col in cols:
            size = col.split('/')[0]
            for row in rows:
                line = []
                line.append(art_num)
                line.append(size)
                try:
                    int(row)
                    width = '-'
                except:
                    width = row
                stock = str(df.loc[row, col])
                line.append(width)
                if len(stock) == 0 or 'nan' in stock:
                    line.append('-')
                else:
                    line.append(stock)

                data.append(line.copy())

        try:
            wait(driver, 90).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.ui-button.ui-corner-all.ui-widget.ui-dialog-titlebar-close'))).click()
            time.sleep(2)
        except:
            continue

def scrape_socks(driver, data):

    URL = "https://b2bshop.bataindustrials.com/en-us/socks/"
    while True:
        try:
            driver.get(URL)
            time.sleep(3)
            break
        except:
            driver.refresh()
            time.sleep(3)
    nprod = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='counter-inside']"))).text.split(' ')[0]
    URL = "https://b2bshop.bataindustrials.com/en-us/socks/" + "/?count={}".format(nprod)

    driver.get(URL)
    time.sleep(3)
    #data = []
    # getting the list of products
    prods = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='l-products-item']")))
    iprod = 0
    for prod in prods:
        iprod += 1
        print('Scraping Socks Product {} of {}'.format(iprod, nprod))
        #excluding out of stock items
        try:
            prod.find_element_by_css_selector("span.lbl-stock.in-stock")
            prod.find_element_by_css_selector("span.btn-cnt")
        except:
            continue
        art_num = prod.find_element_by_css_selector('a.product-title').text
        item_num = prod.find_element_by_css_selector('span.product-id-value').text
        #print(art_num, item_num)
        
        # getting stock data
        prod.find_element_by_css_selector('button.btn').click()
        time.sleep(2)
        while True:
            try:
                table = wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.gvi.gvi-variants.sticky-enabled')))
                time.sleep(2)
                html = table.get_attribute('outerHTML')
                break
            except:
                time.sleep(3)
       
        df = pd.read_html(html, keep_default_na=False)[0]
        if 'unnamed' in str(df.columns[0]).lower():
            cols = df.columns[1:]
            rows = df.iloc[:, 0]
        else:
            cols = df.columns
            rows = df.index
        
        df.index = rows
        for col in cols:
            size = col.split('/')[0]
            for row in rows:
                line = []
                line.append(art_num)
                line.append(size)
                try:
                    int(row)
                    width = '-'
                except:
                    width = row
                stock = str(df.loc[row, col])
                line.append(width)
                if len(stock) == 0 or 'nan' in stock:
                    line.append('-')
                else:
                    line.append(stock)

                data.append(line.copy())

        try:
            wait(driver, 90).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.ui-button.ui-corner-all.ui-widget.ui-dialog-titlebar-close'))).click()
            time.sleep(2)
        except:
            continue
        
def scrape_accessories(driver, data):

    URL = "https://b2bshop.bataindustrials.com/en-us/accessories/"
    while True:
        try:
            driver.get(URL)
            time.sleep(3)
            break
        except:
            driver.refresh()
            time.sleep(3)
    nprod = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='counter-inside']"))).text.split(' ')[0]
    URL = "https://b2bshop.bataindustrials.com/en-us/accessories/" + "/?count={}".format(nprod)

    driver.get(URL)
    time.sleep(3)
    #data = []
    # getting the list of products
    prods = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='l-products-item']")))
    iprod = 0
    for prod in prods:
        iprod += 1
        print('Scraping Accessories Product {} of {}'.format(iprod, nprod))
        #excluding out of stock items
        try:
            prod.find_element_by_css_selector("span.lbl-stock.in-stock")
        except:
            continue
        art_num = prod.find_element_by_css_selector('a.product-title').text
        item_num = prod.find_element_by_css_selector('span.product-id-value').text
        #print(art_num, item_num)
        line = []
        line.append(art_num)
        line.append('-')
        line.append('-')
        line.append(10)
        data.append(line.copy())
        time.sleep(2)

def output_data(data):

    # removing the previous output file
    path = os.getcwd()
    files = os.listdir(path)
    for file in files:
        if 'Scraped_Data' in file:
            os.remove(file)

    #header = ['EAN', 'Article', 'Size', 'Width', 'On Stock']
    header = ['Article', 'Size', 'Width', 'On Stock']


    filename = 'Scraped_Data_{}.csv'.format(datetime.now().strftime("%d_%m_%Y_%H_%M"))

    if path.find('/') != -1:
        output = path + "/" + filename
    else:
        output = path + "\\" + filename

    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

        
def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

    
# Website login credentials
name1 = ""
pwd1 = ""

if __name__ == '__main__':

    #while True:
    #    interval = input('Please enter the data update time in mins: \n')
    #    try:
    #        interval = int(interval)
    #    except:
    #        print('Invalid input, please try again!')
    #        continue

    #    if interval > 0:
    #        break
    #    else:
    #        print('Invalid input, please try again!')
    #        continue

    start_time = time.time()
    driver = initialize_bot()
    clear_screen()
    signin = False
    print('-'*50)
    print('Logging in....')
    print('-'*50)
    data = []
    try:
        login(driver, name1, pwd1)
        print('Scraping Socks Data....')
        print('-'*50)
        scrape_socks(driver, data)
        print('-'*50)
        print('Scraping Accessories Data....')
        print('-'*50)
        scrape_accessories(driver, data)
        print('-'*50)
        driver.quit()
        driver = initialize_bot()
        login(driver, name1, pwd1)
        print('Scraping Shoes Data....')
        print('-'*50)
        scrape_shoes(driver, data)
        print('-'*50)
        print('Outputting Scraped Data....')
        output_data(data)
    except:
        print('-'*50)
        print('Failure in Scraping the data! Exiting the program ...')
        print('-'*50)
        exit(1)


    print('-'*50)
    print('Data is scraped successfully! Total scraping time is {:.1f} mins'.format((time.time() - start_time)/60))
    print('-'*50)


