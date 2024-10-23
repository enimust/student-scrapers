"""
Author: Johanna Lee
Purpose: Using Requests to get html pagea and extract metadat information
"""
import browser_cookie3
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import asyncio
import logging
import os
import aiohttp
import asyncio
from datetime import datetime, date

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
logging.FileHandler("instagram_log.log"),
])


headers = {'Accept-Encoding': 'gzip, deflate, sdch',
'Accept-Language': 'en-US,en;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive'}

COLLECTED_DATA = [
    'upload date',
    'id',
    'username',
    'full name',
    'likes',
    'comments',
    'raw title',
    'raw description',
]

def specify_browser(browser='chrome'):
    """
    Specify browser to grab cookies.

    Args:
        browser (str): Browser name (e.g., 'chrome').
    """
    global cookies
    cookies = getattr(browser_cookie3,browser)(domain_name='https://www.instagram.com/')

def read_input_data(csvFile) -> tuple:
    """
    Returns:
        list[tuple[dict, int]]: list of data from input, as well as its original position in the
                                input file.
    """
    with open(csvFile, 'r') as f:
        reader = csv.DictReader(f)
        return [(row, index) for index, row in enumerate(reader)]

async def get_raw_data(post, rank, semaphore):
    time_collected = datetime.now()
    async with (
        semaphore,
        aiohttp.ClientSession() as session,
        session.get(f"https://www.instagram.com/p/{post['id']}/", allow_redirects=True, headers=headers, cookies=cookies) as ig
    ):
        try:
            text = await ig.text()
            soup = BeautifulSoup(text, "html.parser")
            ig_title = soup.find('meta', attrs={'property': 'og:title'})['content']
            ig_image = soup.find('meta', attrs={'property': 'og:image'})['content']
            ig_description = soup.find('meta', attrs={'property': 'og:description'})['content']
            success = True
        except Exception as e:
            logging.error(f"Error processing post {post['id']}: {e}")
            ig_title, ig_image, ig_description = None, None, None

        likes, comments, username, upload_date, caption = getDataFromDesc(ig_description)
        full_name = getFullName(ig_title)
            
        return (
            {
                'upload date': upload_date,
                'id': post['id'],
                'username': username,
                'full name': full_name,
                'likes': likes,
                'comments': comments,
                'raw title': ig_title,
                'raw description': ig_description,
            },
            success
        )

def getDataFromDesc(desc: str) -> tuple[int, int, str, date, str]:
    """
    Gets data from the description provided by Instagram.

    Args:
        desc (str): description from Instagram

    Returns:
        tuple[int, int, str, date, str]: # likes, # comments, username, upload date, caption
    """
    if not desc:
        return None, None, None, None, None
    
    dashIndex = desc.find(' - ')
    if dashIndex != -1:
        likesAndComments = desc[:dashIndex]
        likes, comments = likesAndComments.split(', ')
        likes, comments = likes.split(' ')[0], comments.split(' ')[0]
        likes = getNum(likes)
        comments = getNum(comments)

        username = desc[dashIndex + 3:]
    else:
        likes, comments = '<<could not collect>>', '<<could not collect>>'
        
        username = desc
        

    
    username = username[:username.index(' ')]

    upload_date = desc[desc.index(' on ') + 4:desc.index(': ')]
    upload_date = datetime.strptime(upload_date, "%B %d, %Y")

    caption = desc[desc.index('"') + 1:desc.rfind('"')]

    return likes, comments, username, upload_date, caption

def getFullName(title: str) -> str:
    """
    Gets full name of poster from title provided by Instagram.

    Args:
        title (str): title from Instagram

    Returns:
        str: full name of poster
    """
    if not title:
        return None
    
    return title[:title.index(' on Instagram: "')]

def getNum(num: str) -> int:
    """
    Helper function to get a number from a string, understanding "K" and "M" notation.

    Args:
        num (str): the number as a str

    Returns:
        int: the number as an int
    """
    num = num.replace(',', '').lower()
    if 'k' in num:
        factor = 1_000
        num = num.replace('k', '')
    elif 'm' in num:
        factor = 1_000_000
        num = num.replace('m', '')
    else:
        factor = 1

    return int(float(num) * factor)

def add_to_metadata(raw_data, metadataFile):
    file_exists = os.path.isfile(metadataFile)

    with open(metadataFile, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=COLLECTED_DATA)
        if not file_exists:
            writer.writeheader()
        writer.writerow(raw_data)

async def process_one_video(post, rank, metadataFile, retry, semaphore):
    raw_data, success = await get_raw_data(post, rank, semaphore)
    if not success:
        logging.error(f"Failed to locate video for URL: {id}")
        failedFile = "retry.csv" if not retry else "failed.csv"
        with open(failedFile, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=COLLECTED_DATA)
            writer.writerow({
                'upload date': None,
                'id': post['id'],
                'username': None,
                'full name': None,
                'likes': None,
                'comments': None,
                'raw title': None,
                'raw description': None,
            })
    add_to_metadata(raw_data, metadataFile)
    
async def process_multiple_videos(posts, metadataFile: str, retry):
    specify_browser()

    filename = "failed.csv" if retry else "retry.csv"

    with open(filename, 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["video_url"])

    semaphore = asyncio.Semaphore(3)
    tasks = [asyncio.create_task(process_one_video(post, rank, metadataFile, retry, semaphore)) for post, rank in posts]
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logging.error(f"Task {task} was cancelled")
    finally:
        logging.info(f"Saved {len(posts)} posts and/or lines of metadata")

async def collect(csvFile, metadataFile):
    posts = read_input_data(csvFile)
    await process_multiple_videos(posts, metadataFile, retry = 0)
    
    await asyncio.sleep(300)

    # process failed_to_locate file one more time to catch request errors
    failed_posts = read_input_data('./retry.csv')
    if failed_posts:
        await process_multiple_videos(posts, metadataFile, retry = 1)
    
########
# Body #
########
def getMetaData(inFilepath: str, outFilepath: str):
    """
    Gets data on a csv of collected posts in inFilepath and writes the final data
    to outFilepath.

    Args:
        inFilepath (str): the path to the file to read from
        outFilepath (str): the path to the file to write to
        mainDir (str): the path to the main directory for Instagram
    """
    print("START COLLECTION")
    asyncio.run(collect(inFilepath, outFilepath))
    print("END COLLECTION")

