from googleapiclient.discovery import build
import pandas as pd
import datetime
import os

# Replace with your YouTube API key
api_key = "AIzaSyDIRMzgP0qcR75TAv4hIgSovMeaOOeIkcU"

# Dictionary of YouTube channel IDs and their names
channels = {
    "UC62pPLZqx8JIrtW1kT5NPWA": "Geo Entertainment",
    "UC_vt34wimdCzdkrzVejwX9g": "Geo News",
    "UCjf9mzqsb9lH7yd5OcBqzsA": "Samma Entertainment",
    "UCJekW1Vj5fCVEGdye_mBN6Q": "Samma News",
    "UCaxR-D8FjZ-2otbU0_Y2grg": "Dawn news",
    "UCTur7oM6mLL0rM2k0znuZpQ": "Express News",
    "UCMmpLL2ucRHAXbNHiCPyIyg": "ARY News",
    "UC4JCksJF76g_MdzPVBJoC3Q": "ARY Digital",
    "UCnMBV5Iw4WqKILKue1nP6Hg": "Duniya News",
    "UCgBAPAcLsh_MAPvJprIz89w": "Aaj News"
    
}

# Build YouTube Data API client
youtube = build("youtube", "v3", developerKey=api_key)

def fetch_youtube_stats():
    def get_channel_stats(channel_id):
        request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        response = request.execute()
        
        if "items" in response and response["items"]:
            stats = response["items"][0]["statistics"]
            views = int(stats.get("viewCount", 0))
            subscribers = int(stats.get("subscriberCount", 0))
            return views, subscribers
        return None, None
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    data_list = []

    for channel_id, channel_name in channels.items():
        views, subscribers = get_channel_stats(channel_id)
        
        if views is not None and subscribers is not None:
            data_list.append({
                "Date": today,
                "Channel Name": channel_name,
                "Total Views": views,
                "Total Subscribers": subscribers
            })
            print(f" {channel_name} - Views: {views}, Subscribers: {subscribers}")
        else:
            print(f"Failed to fetch data for {channel_name}")

    if data_list:
        df = pd.DataFrame(data_list)
        csv_file = "youtube_stats.csv"

        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)

# Fetch data and exit (No infinite loop)
fetch_youtube_stats()
