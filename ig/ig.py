import pandas as pd 
import csv
from bs4 import BeautifulSoup as BS
import logging
import time
import csv
import datetime as datetime
import os
from igMetadaCollector import getMetaData
from seleniumbase import Driver

########################################
# Helper methods
########################################

user = '' # set user for your own computer
lengthOfScroll = 3
searchTerm = ['tradwives', 'wellesley', 'flatearth']


def startBrowser():
    try:
        # Initialize the Chrome browser in Incognito mode
        browser = Driver(browser="chrome", incognito=True, headless=False)
        
        logging.info("Opening browser in Incognito mode!")
        time.sleep(1)
        return browser
    except Exception as e:
        logging.error(f"Error opening browser: {e}")
        return None

def downloadPage(browser, filePath):
    try:
        with open(filePath, "w", encoding='utf-8') as f:
            f.write(browser.page_source)
    except:
        print("Could not download page!")

def readInstagram(intermediateFilePath, finalFilePath):
    with open(intermediateFilePath, 'r') as f:
        contents = f.read()
        soup = BS(contents, "html.parser")
        elements = soup.select('.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x4gyw5p._a6hd')
        links = []
        for el in elements:
            l = el['href']
            final_l = l.replace('/', '')
            links.append(final_l)

        fileExists = os.path.isfile(finalFilePath)
        isEmpty = os.stat(finalFilePath).st_size == 0 if fileExists else True
        header = ['id']
        with open(finalFilePath, "a") as file:
            writer = csv.writer(file)
            if isEmpty:
                writer.writerow(header)
            for item in links:
                    writer.writerow([item])


def getInstagram(term):
    if not os.path.isdir('./intermediate'):
        os.mkdir('./intermediate')

    if not os.path.isdir('./data'):
        os.mkdir('./data')

    intermediateFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H-%M-%S")}.html'
    finalFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H-%M-%S")}.csv'

    browser = startBrowser()
    browser.get(f'https://www.instagram.com/explore/search/keyword/?q={term}')
    time.sleep(25)
    
    for i in range(lengthOfScroll):
        # Use JavaScript to scroll by 900 pixels
        browser.execute_script("window.scrollBy(0, 900);")
        time.sleep(5)
        downloadPage(browser, intermediateFilePath)
        readInstagram(intermediateFilePath, finalFilePath)
    
    browser.quit()
    return finalFilePath

def getUniquePosts(filePath):
    record = pd.read_csv(filePath) 
    unique = record['id'].unique()
    header = ['id']
    with open(filePath, "w") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for item in unique:
                writer.writerow([item])

########################################
# Run unschooling queries
########################################

for search in searchTerm:
    filePath = getInstagram(search)
    getUniquePosts(filePath)
    outFilePath = f'./data/{search}_{datetime.datetime.now().strftime("%m-%d-%y %H-%M-%S")}.csv'
    getMetaData(filePath, outFilePath)
