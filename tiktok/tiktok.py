import pandas as pd 
import csv
import selenium 
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time
import csv
import datetime as datetime
import os

########################################
# Helper methods
########################################

user = 'belle' # set user for your own computer
login = False
searchTerm = ['unschooling']
lengthOfScroll = 1

def startBrowser():
    options = webdriver.ChromeOptions()
    userdatadir = f'/Users/{user}/Library/Application Support/Google/Chrome/'
    profile = 'Profile 1'
    options.add_argument(f"--user-data-dir={userdatadir}")
    options.add_argument(f"--profile-directory={profile}")
    browser = webdriver.Chrome(options=options)
    logging.info("Opening browser!")
    browser.get("https://www.tiktok.com")
    if (login):
        time.sleep(100)
    else:
        time.sleep(1)
    return browser


def downloadPage(browser, filePath):
    try:
        with open(filePath, "w", encoding='utf-8') as f:
            f.write(browser.page_source)
    except:
        print("Could not download page!")

def readTikTok(intermediateFilePath, finalFilePath):
    with open(intermediateFilePath, 'r') as f:
        contents = f.read()
        soup = BS(contents, "html.parser")
        elements = soup.select('.css-1g95xhm-AVideoContainer.e19c29qe13')
        viewCount = soup.select('.css-ws4x78-StrongVideoCount.etrd4pu10')
        links = []

        for index, el in enumerate(elements):
            e = []
            l = el['href']
            e.append(l)

            img_tag = el.find('img') 
            if img_tag and 'alt' in img_tag.attrs: 
                alt_text = img_tag['alt'] 
                e.append(alt_text)

            if index < len(viewCount):
                e.append(viewCount[index].contents)

            links.append(e)

        

            

        fileExists = os.path.isfile(finalFilePath)
        isEmpty = os.stat(finalFilePath).st_size == 0 if fileExists else True
        header = ['link', 'text', 'views']
        with open(finalFilePath, "a") as file:
            writer = csv.writer(file)
            if isEmpty:
                writer.writerow(header)
            for item in links:
                    writer.writerow(item)


def getTikTok(term, browser):
    if not os.path.isdir('./intermediate'):
        os.mkdir('./intermediate')

    if not os.path.isdir('./data'):
        os.mkdir('./data')

    intermediateFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")}.html'
    finalFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")}.csv'

    browser.get(f'https://www.tiktok.com/search?q={term}')
    time.sleep(10)
    for i in range(0, lengthOfScroll):
        ActionChains(browser)\
            .scroll_by_amount(0, 900)\
            .perform()
        time.sleep(5)
        downloadPage(browser, intermediateFilePath)
        readTikTok(intermediateFilePath, finalFilePath)
    
    return finalFilePath

########################################
# Run unschooling queries
########################################
browser = startBrowser()

if login == False:
    for search in searchTerm:
        filePath = getTikTok(search, browser)