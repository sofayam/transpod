import feedparser # type: ignore
import requests
import os
import argparse
import config
import json


# Function to download the latest podcast
def download(rss_feed_url, download_folder, relative, first, last, savefeed):
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)

    # Check if the feed has entries
    if not feed.entries:
        print("No episodes found in the RSS feed.")
        return
    else:
        print(len(feed.entries), " Entries in total")
        if savefeed:
            latestfeedpath = open(download_folder + ".latestfeed", "w", encoding='utf8')
            json.dump(feed.entries, latestfeedpath, ensure_ascii=False, indent=4)

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
savefeed =  "savefeed" in list(conf.keys())
# rss_feed_url = open(feedfile).read()
download_folder = feedfolder
download(rss_feed_url, download_folder, relative, first, last, savefeed)