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
from igMetadaCollector import getMetaData


########################################
# Helper methods
########################################

user = '' # set user for your own computer
lengthOfScroll = 1

def startBrowser():
    options = webdriver.ChromeOptions()
    userdatadir = f'/Users/{user}/Library/Application Support/Google/Chrome/'
    profile = 'Profile 1'
    options.add_argument(f"--user-data-dir={userdatadir}")
    options.add_argument(f"--profile-directory={profile}")
    browser = webdriver.Chrome(options=options)
    logging.info("Opening browser!")
    time.sleep(1)
    return browser


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

    intermediateFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")}.html'
    finalFilePath = f'./intermediate/{term}_{datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")}.csv'

    browser = startBrowser()
    browser.get(f'https://www.instagram.com/explore/search/keyword/?q={term}')
    time.sleep(10)
    for i in range(0, lengthOfScroll):
        ActionChains(browser)\
            .scroll_by_amount(0, 900)\
            .perform()
        time.sleep(5)
        downloadPage(browser, intermediateFilePath)
        readInstagram(intermediateFilePath, finalFilePath)
    
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
searchTerm = ['unschooling', 'how to unschool your child', 'tradwives']

for search in searchTerm:
    filePath = getInstagram(search)
    getUniquePosts(filePath)
    outFilePath = f'./data/{search}_{datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")}.csv'
    getMetaData(filePath, outFilePath)
