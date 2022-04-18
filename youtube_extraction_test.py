import sys
import os
from youtube_extractor import youtube_extractor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

video_list = ["https://www.youtube.com/watch?v=XnlT3rPNUp0"]

youtube_extractor.extract_video_list(video_list, get_replies = False, to_json = True, path = ".")