import requests
import json
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm



URL = "https://www.googleapis.com/youtube/v3/"
API_KEY = "api-key"

def extract_video_list(url_list, get_replies = True, to_json = False, path = ""):
    """
    Receives a list of YouTube video URLs and retrieves their comments into a list of dictionaries, one for each video.

    Args:
        url_list (list[str]): list of YouTube video URLs.
        get_replies (bool, optional): If set to True, gets replies from the comments. Defaults to True.
        to_json (bool, optional): If True, outputs the dictionary as JSON files for every video. Defaults to False.
        path (str, optional): The folder path to output the JSON files. Defaults to "".

    Returns:
        list[Dict]: List of dictionaries, with one for each video.
    """
    video_list = []
    for video_url in tqdm(url_list):
        video_id = strip_video_url(video_url)
        video = get_video_metadata(video_id)
        video_comments = get_video_comments_from_url(video_id, get_replies = get_replies)
        video["comments"] = video_comments
        video_list.append(video)

    if to_json:
        for video in video_list:
            filename = "{}/{}_{}".format(path, video["channelTitle"].replace(" ", '_').replace("\"", ""), video["title"].replace(" ", '_').replace("\"", "").replace(":", "_"))
            dict_to_json(video, filename)

    return video_list 


def get_video_comments(video_id, get_replies, 
                       n = 1, next_page_token = None):
    """
    Receives a video and parses through all comment threads, grabbing every top level comment and their replies and inserting them into a dictionary.

    Args:
        video_id (str): Youtube video id.
        get_replies (bool, optional): If True, will get all replies to a comment. Defaults to True.
        n (int, optional): Number of the comment inside its hierarchy. Defaults to 1 for the first comment.
        next_page_token (nextPageToken, optional): If it exists, will request the next page of comments. Defaults to None.

    Returns:
        list[Dict]: List with a dictionary for every top level comment.
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
    
    
    comment_list = []
  
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()


    for comment_info in resource['items']:
        text = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
        like_count = comment_info['snippet']['topLevelComment']['snippet']['likeCount']
        reply_count = comment_info['snippet']['totalReplyCount']
        username = comment_info['snippet']['topLevelComment']['snippet']['authorDisplayName']
        timestamp = comment_info["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
        comment_id = comment_info['snippet']['topLevelComment']['id']
        author_id = comment_info['snippet']['topLevelComment']['snippet']['authorChannelId']['value']


        comment = {"number": n, "comment_id": comment_id, "author_id":author_id, "username":username, "text": text.replace('\n', ' '),  
                   "like_count": like_count, "reply_count": reply_count, "timestamp": timestamp}      
        
        if (reply_count > 0) & (get_replies):
            comment["replies"] = list(reversed(get_comment_replies(video_id, next_page_token, comment_id)))
            
        comment_list.append(comment)
        n = n + 1

    if 'nextPageToken' in resource:
        comment_list.extend(get_video_comments(video_id, get_replies, next_page_token = resource["nextPageToken"], n = n))
    
    return comment_list
    

def get_comment_replies(video_id, next_page_token, parent_id, cn = 1):
    """
    Receives a comment's id and gets all of their replies, inserting them into a list of dictionaries, with one for each reply.

    Args:
        video_id (str): Youtube video id.
        next_page_token (nextPageToken, optional): If it exists, will request the next page of comments. Defaults to None.
        parent_id (str): Parent comment id.
        cn (int, optional): Number of the comment inside its hierarchy. Defaults to 1 for the first comment.

    Returns:
        list[Dict]: List with a dictionary for every reply.
    """
    params = {
    'key': API_KEY,
    'part': 'snippet',
    'videoId': video_id,
    'textFormat': 'plaintext',
    'maxResults': 50,
    'parentId': parent_id,}

    if next_page_token is not None:
        params['pageToken'] = next_page_token

    reply_list = []
    
    response = requests.get(URL + 'comments', params=params)
    resource = response.json()

    for comment_info in (resource['items']):
        text = comment_info['snippet']['textDisplay']
        like_count = comment_info['snippet']['likeCount']
        username = comment_info['snippet']['authorDisplayName']
        author_id = comment_info['snippet']['authorChannelId']['value']
        timestamp = comment_info["snippet"]["publishedAt"]
        comment_id = comment_info["id"]
        parent_id = parent_id

        reply = {"comment_number":cn, "comment_id": comment_id, "parent_id": parent_id, "author_id": author_id, 
                "username": username,"text": text.replace('\n', ' '), "like_count": like_count,  "timestamp":timestamp}
        reply_list.append(reply)
        cn = cn + 1

    if 'nextPageToken' in resource:
        reply_list.extend(get_comment_replies(video_id, resource["nextPageToken"], parent_id, cn = cn))
    
    return reply_list

def strip_video_url(video_url):
    """
    Parses the Youtube video URL to get the video's ID.

    Args:
        video_url (str): YouTube video URL.

    Returns:
        str: The video's id.
    """
    u_parse = urlparse(video_url)
    query_video = parse_qs(u_parse.query).get('v')
    
    if query_video:
        return query_video[0]
    
    path = u_parse.path.split('/')
    if path:
        return path[-1]

def get_video_comments_from_url(video_url, get_replies):
    video_id = strip_video_url(video_url)
    comments = get_video_comments(video_id, get_replies = get_replies)

    return comments
    
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
