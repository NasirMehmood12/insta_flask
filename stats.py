from flask import Flask, jsonify
import psycopg2
import os
import datetime
from googleapiclient.discovery import build

app = Flask(__name__)


# Get database URL and YouTube API key from environment variables
DATABASE_URL = os.getenv("postgresql://news_data_rnj1_user:Riu6PH7TV9B3YeXSmUFgcNMvs2JOr4oa@dpg-cuo46nl2ng1s73e2oo20-a/news_data_rnj1")
api_key = os.getenv("AIzaSyDIRMzgP0qcR75TAv4hIgSovMeaOOeIkcU")
print("AIzaSyDIRMzgP0qcR75TAv4hIgSovMeaOOeIkcU:", api_key)  # <-- Add this line

# Build YouTube API client
youtube = build("youtube", "v3", developerKey=api_key)

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

# API route to fetch stored data
@app.route('/youtube-stats', methods=['GET'])
def get_stats():
    """Fetches YouTube stats from the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM youtube_stats ORDER BY date DESC LIMIT 10;")
        rows = cursor.fetchall()
        conn.close()

        data = [
            {"id": row[0], "date": row[1], "channel": row[2], "views": row[3], "subscribers": row[4]}
            for row in rows
        ]
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# Run the script once to fetch and save data
fetch_youtube_stats()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
