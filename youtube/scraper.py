from seleniumbase import BaseCase
import time
from datetime import datetime
from csv import DictReader
import os
from seleniumbase.common.exceptions import NoSuchElementException

class TestYoutube(BaseCase):
    def test_save_html_page(self):
        """
        2. traverse through the vids in the vid_list
        3. where we scroll down once to get comments
        4. save html file fo each vid
        """
        target_folder = "results"

        self.open('https://www.youtube.com/')
        print("log in")
        time.sleep(60)

        vid_list = []
        vid_path = f"./queries.csv"
        with open(vid_path,"r") as file:
            reader = DictReader(file)          
            for row in reader:
                link = f"https://www.youtube.com/results?search_query={row['query']}"
                vid_list.append((link, row['query']))

        print(f"we have {len(vid_list)} queries")
        
        for i, (link, query) in enumerate(vid_list):
            time.sleep(5)
            self.open(link)
            try: 
                # self.scroll_to_bottom()
                soup = self.get_beautiful_soup(source=None)
                print(soup)

                with open(f"./results/vid_{i}_{query}.html", "w", encoding="utf-8") as file:
                    file.write(soup.prettify())
            except Exception as e:
                print(f"retry failed, {e}")