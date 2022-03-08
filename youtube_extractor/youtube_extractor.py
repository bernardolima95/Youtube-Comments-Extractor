import requests
import json
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm



URL = "https://www.googleapis.com/youtube/v3/"


def get_video_comments(video_id, comment_list = None, 
                       n = 1, next_page_token = None):
    """
    Receives a video 
    """
    
    params = {
    'key': API_KEY,
    'part': 'snippet',
    'videoId': video_id,
    'order': 'relevance',
    'textFormat': 'plaintext',
    'maxResults': 100,}
    
    if next_page_token is not None:
        params['pageToken'] = next_page_token
    
    if comment_list is None:
        comment_list = []
  
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()


    for comment_info in resource['items']:
        text = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
        like_count = comment_info['snippet']['topLevelComment']['snippet']['likeCount']
        reply_count = comment_info['snippet']['totalReplyCount']
        username = comment_info['snippet']['topLevelComment']['snippet']['authorDisplayName']
        parent_id = comment_info['snippet']['topLevelComment']['id']

        comment = {"number": n, "text": text.replace('\n', ' '), "username":username, 
                   "parent_id":parent_id, "like_count": like_count, "reply_count": reply_count}      
        
        if reply_count > 0:
            comment["replies"] = list(reversed(get_comment_replies(video_id, next_page_token, parent_id)))
            
        comment_list.append(comment)
        n = n + 1

    if 'nextPageToken' in resource:
        comment_list.extend(get_video_comments(video_id, next_page_token = resource["nextPageToken"], n = n))
    
    return comment_list
    

def get_comment_replies(video_id, next_page_token, parent_id, reply_list = None, cn = 1):
    params = {
    'key': API_KEY,
    'part': 'snippet',
    'videoId': video_id,
    'textFormat': 'plaintext',
    'maxResults': 50,
    'parentId': parent_id,}

    if next_page_token is not None:
        params['pageToken'] = next_page_token

    if reply_list is None:
        reply_list = []
    
    response = requests.get(URL + 'comments', params=params)
    resource = response.json()

    for comment_info in (resource['items']):
        text = comment_info['snippet']['textDisplay']
        like_count = comment_info['snippet']['likeCount']
        username = comment_info['snippet']['authorDisplayName']

        reply = {"comment_number":cn, "text": text.replace('\n', ' '), "like_count": like_count, "username": username}
        reply_list.append(reply)
        cn = cn + 1

    if 'nextPageToken' in resource:
        reply_list.extend(get_comment_replies(video_id, resource["nextPageToken"], parent_id, cn = cn))
    
    return reply_list

def strip_video_url(video_url):
    u_parse = urlparse(video_url)
    query_video = parse_qs(u_parse.query).get('v')
    
    if query_video:
        return query_video[0]
    
    path = u_parse.path.split('/')
    if path:
        return path[-1]

def get_video_comments_from_url(video_url):
    video_id = strip_video_url(video_url)
    comments = get_video_comments(video_id)

    return comments

def extract_video_list(url_list, to_json = False, path = ""):
    video_list = []
    for video_url in tqdm(url_list):
        video_id = strip_video_url(video_url)
        video = get_video_metadata(video_id)
        video_comments = get_video_comments_from_url(video_id)
        video["comments"] = video_comments
        video_list.append(video)

    if to_json:
        for video in video_list:
            filename = "{}/{}_{}".format(path, video["channelTitle"].replace(" ", '_'), video["title"].replace(" ", '_'))
            dict_to_json(video, filename)

    return video_list     

def get_video_metadata(video_id):
    params = {
    'key': API_KEY,
    'part': 'snippet',
    'id': video_id}

    response = requests.get(URL + 'videos', params=params)
    resource = response.json()

    video_resource = resource["items"][0]

    video_metadata = {}
    video_metadata["title"] = video_resource["snippet"]["title"]
    video_metadata["publishedAt"] = video_resource["snippet"]["publishedAt"]
    video_metadata["tags"] = video_resource["snippet"]["tags"]
    video_metadata["videoId"] = video_resource["id"]
    video_metadata["channelId"] = video_resource["snippet"]["channelId"]
    video_metadata["channelTitle"] = video_resource["snippet"]["channelTitle"]

    return video_metadata

def dict_to_json(dictionary, filename):
    with open("{}.json".format(filename), "w") as outfile:
        json.dump(dictionary, outfile, indent = 4)
