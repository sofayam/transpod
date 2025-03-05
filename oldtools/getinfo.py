# import feedparser # type: ignore
from feedparser import parse, FeedParserDict
import requests
import os
import argparse
import config
import json
import sys


# Function to download the latest podcast
def getInfo(rss_feed_url, download_folder):
    # Parse the RSS feed

    feed = parse(rss_feed_url)

    # Check if the feed has entries
    if not feed.entries:
        print("No episodes found in the RSS feed.", file=sys.stderr)
        return
    else:
        print(len(feed.entries), " Entries in total", file=sys.stderr)
  

    # Get the latest episode

  

    for latest_episode in feed.entries:    
    
        episode_title = latest_episode.title
        media_url = latest_episode.enclosures[0].href  # Get the media URL from the 'enclosures'

        # Ensure the download folder exists
        os.makedirs(download_folder, exist_ok=True)

        # File path for the downloaded episode
        file_base = episode_title.replace(" ", "_").replace("/", "_") 
        mp3name = file_base + ".mp3"
        infoname = file_base + ".info"

        mp3path = os.path.join(download_folder, mp3name)
        infopath = os.path.join(download_folder, infoname)
        # check if file already exists
        if os.path.exists(mp3path):
            print ("about to create info file ", infopath)
            
            json.dump(latest_episode, open(infopath, "w", encoding='utf8'), ensure_ascii=False, indent=4)

            
def parse_args():
    parser = argparse.ArgumentParser(description="Get podcast info files")

    # Positional argument: filename (string)
    parser.add_argument("filename", type=str, help="Input filename.")

    
    args = parser.parse_args()

    return args

args = parse_args()
feedfolder =getattr(args,'filename')


conf = config.getConfig(feedfolder)
rss_feed_url = conf["feed"]

# rss_feed_url = open(feedfile).read()
download_folder = feedfolder
getInfo(rss_feed_url, download_folder)