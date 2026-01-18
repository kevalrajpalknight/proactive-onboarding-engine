import os
from typing import List

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def search_youtube_videos(query: str, max_results: int = 5) -> List[dict]:
    """Searches for YouTube videos based on a query using the YouTube Data API.
    Args:
        api_key (str): YouTube Data API key.
        query (str): Search query string.
        max_results (int): Maximum number of results to return.
    Returns:
        list: A list of video metadata dictionaries.
    """

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=YOUTUBE_API_KEY,
    )

    request = youtube.search().list(
        q=query, part="id,snippet", maxResults=max_results, type="video,playlist"
    )
    response = request.execute()

    videos = []
    for item in response.get("items", []):
        video_data = {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel_title": item["snippet"]["channelTitle"],
            "publish_time": item["snippet"]["publishTime"],
        }
        videos.append(video_data)

    return videos
