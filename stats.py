import psycopg2
import os
import datetime
from googleapiclient.discovery import build

# Get database credentials from Render environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# YouTube API key (store in Render's environment variables)
api_key = os.getenv("YOUTUBE_API_KEY")

# YouTube channels
channels = {
    "UC62pPLZqx8JIrtW1kT5NPWA": "Geo Entertainment",
    "UC_vt34wimdCzdkrzVejwX9g": "Geo News",
    "UCjf9mzqsb9lH7yd5OcBqzsA": "Samma Entertainment",
    "UCJekW1Vj5fCVEGdye_mBN6Q": "Samma News",
    "UCaxR-D8FjZ-2otbU0_Y2grg": "Dawn news",
    "UCTur7oM6mLL0rM2k0znuZpQ": "Express News"
}

# Build YouTube API client
youtube = build("youtube", "v3", developerKey=api_key)

def fetch_youtube_stats():
    def get_channel_stats(channel_id):
        request = youtube.channels().list(part="statistics", id=channel_id)
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
            data_list.append((today, channel_name, views, subscribers))
            print(f"{channel_name} - Views: {views}, Subscribers: {subscribers}")
        else:
            print(f"Failed to fetch data for {channel_name}")

    if data_list:
        save_to_database(data_list)

def save_to_database(data):
    """ Saves the YouTube stats to PostgreSQL """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_stats (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                channel_name TEXT NOT NULL,
                total_views BIGINT NOT NULL,
                total_subscribers BIGINT NOT NULL
            );
        """)

        # Insert data
        cursor.executemany(
            "INSERT INTO youtube_stats (date, channel_name, total_views, total_subscribers) VALUES (%s, %s, %s, %s)",
            data
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("Data saved to database successfully.")

    except Exception as e:
        print(f"Database error: {e}")

# Run the script once
fetch_youtube_stats()
