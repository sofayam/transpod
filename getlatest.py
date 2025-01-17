import feedparser
import requests
import os
import sys

# Function to download the latest podcast
def download_latest_podcast(rss_feed_url, download_folder, howmany):
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)

    # Check if the feed has entries
    if not feed.entries:
        print("No episodes found in the RSS feed.")
        return
    else:
        print(len(feed.entries), " Entries in total")
    # Get the latest episode

    for idx in range(howmany):    
        latest_episode = feed.entries[idx]
        episode_title = latest_episode.title
        media_url = latest_episode.enclosures[0].href  # Get the media URL from the 'enclosures'

        # Ensure the download folder exists
        os.makedirs(download_folder, exist_ok=True)

        # File path for the downloaded episode
        file_name = episode_title.replace(" ", "_").replace("/", "_") + ".mp3"
        file_path = os.path.join(download_folder, file_name)

        # check if file already exists
        if os.path.exists(file_path):
            print(file_path, "already downloaded")
        else:
            # Download the episode
            print(f"Downloading: {episode_title}")
            response = requests.get(media_url, stream=True)

            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download the episode. HTTP Status Code: {response.status_code}")

# Example usage
feedfolder = sys.argv[1]
howmany = 1
if len(sys.argv) > 2:
    howmany = int(sys.argv[2])

feedfile = feedfolder + "/feed.md"
rss_feed_url = open(feedfile).read()
download_folder = feedfolder
download_latest_podcast(rss_feed_url, download_folder, howmany)