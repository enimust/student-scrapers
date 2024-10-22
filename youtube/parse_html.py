from bs4 import BeautifulSoup as BS
import pandas as pd
import os
import re
import json
import sys


def extract_vid_info(video_file):
    """
    param: .html video_file
    return: extracted username, nickname, description, counts (like,share,comment,play,collect), comments in one video file
    """
    def safe_find(soup, tag, attrs):
        element = soup.find(tag, attrs)
        if element:
            return element.text
        else:
            return None
    def safe_dict_find(data, key):
        try:
            val = data[key]
            return val
        except:
            return None

    with open(video_file, 'r') as f:
        print(video_file)
        vid_num = video_file.split(".")[0].split("_")[-1]
        data = None
        contents = f.read()
        soup = BS(contents, "html.parser")
        url, username, nickname, description, location_created, suggested_words, video_duration, is_ad, music, like_count, share_count, comment_count, play_count, collect_count, comments = None,None,None,None,None,None,None,None,None,None,None,None,None,None,None
        try:
            url = soup.find("meta", property="og:url")['content']
        except:
            pass
        username = safe_find(soup, "span", {"class": "css-1c7urt-SpanUniqueId evv7pft1"})
        nickname = safe_find(soup,"span", {"class": "css-1xccqfx-SpanNickName e17fzhrb1"})
        #description = safe_find(soup, "span", {"class": "css-j2a19r-SpanText efbd9f0"})
        music = safe_find(soup, "div", {"class": "css-pvx3oa-DivMusicText epjbyn3"})
        #print("username:", username,"\nnickname:", nickname, "\ndescription:", description,"\nmusic:",music)
        try:
            script_tag = soup.find('script', text=re.compile('stats'))
            script_content = script_tag.string 
            data = json.loads(script_content)["__DEFAULT_SCOPE__"]['webapp.video-detail']['itemInfo']['itemStruct'] #json to python dict, and keep looking
        except:
            pass
        if data:
            description = safe_dict_find(data,'desc')
            location_created = safe_dict_find(data,'locationCreated')
            suggested_words = safe_dict_find(data,'suggestedWords')
            video_duration = safe_dict_find(data['video'],'duration')
            is_ad = safe_dict_find(data,'isAd')
            like_count = safe_dict_find(data["stats"],'diggCount')
            share_count = safe_dict_find(data["stats"],'shareCount')
            comment_count = safe_dict_find(data["stats"],'commentCount')
            play_count = safe_dict_find(data["stats"],'playCount')
            collect_count = safe_dict_find(data["stats"],'collectCount')
        
        #print("\nlike:",like_count, "\nshare:",share_count, "\ncomment:", comment_count, "\nplay:", play_count, "\ncollect:", collect_count)

        comment_div = soup.find_all("p", {"class": "css-xm2h10-PCommentText e1g2efjf6"})
        comments = []
        for comment in comment_div:
            comments.append(comment.text)
        f.close()

    return vid_num, url, username, nickname, description, location_created, suggested_words, video_duration, is_ad, music, like_count, share_count, comment_count, play_count, collect_count, comments
    


def all_videos_info(video_files,data_folder):
    """
    param: list of video_files saved by TikTokScraper.py
    return: dataframe with all video_info
    """
    infos = {'vid_num':[], 'url':[],'username':[],'nickname':[],'description':[], 'location_created':[],'suggested_words':[],'video_duration':[],'is_add':[],'music':[], 'like_count':[], 'share_count':[], 'comment_count':[], 'play_count':[], 'collect_count':[], 'comments':[]}
    for vid in video_files:
        vid_num, url, username, nickname, description, location_created, suggested_words, video_duration, is_ad, music, like_count, share_count, comment_count, play_count, collect_count, comments = extract_vid_info(vid)
        infos['vid_num'].append(vid_num)
        infos['url'].append(url)
        infos['username'].append(username)
        infos['nickname'].append(nickname)
        infos['description'].append(description)
        infos['location_created'].append(location_created)
        infos['suggested_words'].append(suggested_words)
        infos['video_duration'].append(video_duration)
        infos['is_add'].append(is_ad)
        infos['music'].append(music)
        infos['like_count'].append(like_count)
        infos['share_count'].append(share_count)
        infos['comment_count'].append(comment_count)
        infos['play_count'].append(play_count)
        infos['collect_count'].append(collect_count)
        infos['comments'].append(comments)
    df = pd.DataFrame(infos)
    df.to_csv(f'./{data_folder}/videos_info.csv')
    return df

def get_html_list(pathName):
    """
    gets all .html files scraped and saved by TikTokScraper.py
    """
    all_vid_files = []
    for dirpath, _, filenames in os.walk(pathName):
        for fN in filenames: 
            if fN.endswith('.html') and fN.startswith('vid'):
                filePath = os.path.join(dirpath, fN) # create the whole path of a file
                all_vid_files.append(filePath)
    return all_vid_files


def main():
    data_folder = sys.argv[1]
    all_vid_files = get_html_list(data_folder)
    all_videos_info(all_vid_files,data_folder)

if __name__ == "__main__":
    main()