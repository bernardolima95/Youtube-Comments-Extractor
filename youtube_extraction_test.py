import sys
import os
from youtube_extractor import youtube_extractor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

video_list = ["https://www.youtube.com/watch?v=PXKy_DNQ7Ts", "https://www.youtube.com/watch?v=ZQW10xzM8xI"]

youtube_extractor.extract_video_list(video_list, get_replies = True, to_json = True, path = ".")