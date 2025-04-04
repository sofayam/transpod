# import feedparser # type: ignore
from feedparser import parse, FeedParserDict
import requests
import os
import argparse
import config
import json
import sys
from transcribefast import transcribe
from addDuration import process_mp3



# Function to download the latest podcast
def download(rss_feed_url, download_folder, relative, first, last, transcribeAsWell, sync, dryrun):
    # Parse the RSS feed

    podcatch = False
    feed = parse(rss_feed_url)

    # Check if the feed has entries
    if not feed.entries:
        print("No episodes found in the RSS feed.", file=sys.stderr)
        return
    else:
        print(len(feed.entries), " Entries in total", file=sys.stderr)

    # Get the latest episode

    if relative:
        entries = feed.entries
    else:
        entries = sorted(feed.entries, key=lambda e: e.get("published_parsed"))

    

    for idx in range(first-1, last):    
        latest_episode = entries[idx]
        episode_title = latest_episode.title
        media_url = latest_episode.enclosures[0].href  # Get the media URL from the 'enclosures'

        # Ensure the download folder exists
        os.makedirs(download_folder, exist_ok=True)

        file_base = episode_title.replace(" ", "_").replace("/", "_").replace(":", "_").replace("'", "_").replace('"', "_")
        mp3name = file_base + ".mp3"
        infoname = file_base + ".info"

        mp3path = os.path.join(download_folder, mp3name)
        infopath = os.path.join(download_folder, infoname)

        # check if file already exists
        if os.path.exists(mp3path):
            print(mp3path, "already downloaded", file=sys.stderr)
        else:
            # Download the episode
            headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


            print(f"Downloading: {episode_title}", file=sys.stderr)
            response = requests.get(media_url, headers=headers, stream=True)
            if dryrun:
                print("Dryrun: Not downloading")
                continue
            if response.status_code == 200:
                with open(mp3path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(mp3path)
                json.dump(latest_episode, open(infopath, "w", encoding='utf8'), ensure_ascii=False, indent=4)
                process_mp3(mp3path)
                if transcribe:
                    if transcribeAsWell:
                        transcribe(mp3path)
                        if sync:
                            podcatch = True
                            print ("Marked for syncing to NAS")
                    else:
                        print("Downloaded but did NOT transcribe", mp3path)
               
            else:
                print(f"Failed to download the episode. HTTP Status Code: {response.status_code}", file=sys.stderr)
    if podcatch:
        print("syncing to NAS")
        command = "rsync --exclude='*.meta' -avz --progress " + download_folder + "/ mark@rpm17.local:/volume1/data/languages/japanese/podcasts/" + download_folder
        print(command)  
        os.system(command)

# Example usage

def parse_args():
    parser = argparse.ArgumentParser(description="Choose between 'relative' and 'absolute', each taking one or two integers.")

    # Positional argument: filename (string)
    parser.add_argument("filename", type=str, help="Input filename.")

    # Create mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)

    # "relative" option: takes 1 or 2 int numbers
    group.add_argument("-r", "--relative", nargs="+", type=int, help="Relative mode: provide 1 or 2 integers.")

    # "absolute" option: takes 1 or 2 int numbers
    group.add_argument("-a", "--absolute", nargs="+", type=int, help="Absolute mode: provide 1 or 2 integers.")

    parser.add_argument("-t", "--transcribe", help="Run transcribe on the downloaded files", action="store_true")

    parser.add_argument("-s", "--sync", help="sync to NAS with rsync", action="store_true")

    parser.add_argument("-d", "--dryrun", help="all talk and no action", action="store_true")
    
    args = parser.parse_args()

    # Validate the number of arguments (only 1 or 2 numbers allowed)
    for key in ["relative", "absolute"]:
        values = getattr(args, key)
        if values is not None and not (1 <= len(values) <= 2):
            parser.error(f"--{key} must take 1 or 2 numbers, but got {len(values)}.")

    return args

args = parse_args()
feedfolder =getattr(args,'filename')
relative = False
offs = getattr(args, "relative")
if offs:
    relative = True
else:
    offs = getattr(args, "absolute")

first = offs[0]
if len(offs) > 1:
    last = offs[1]
else:
    last = first

conf = config.getConfig(feedfolder)
rss_feed_url = conf["feed"]

# rss_feed_url = open(feedfile).read()
download_folder = feedfolder
download(rss_feed_url, download_folder, relative, first, last, getattr(args,"transcribe"), getattr(args,"sync"), getattr(args,"dryrun"))
