import sys
import os
from youtube_extractor import youtube_extractor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

video_list = ["https://www.youtube.com/watch?v=RW731a_lwC8&t=5s"]

youtube_extractor.extract_video_list(video_list, to_json = True, path = ".")