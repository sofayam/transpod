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
import datetime

logfile = "podcatch.log"

def logdownload(podcast, episode_title):
    # write an entry to the end of the log file (create if it doesn't exist)
    # showing the date and time, the podcast name, and the episode title   
    with open(logfile, "a", encoding="utf-8") as log:
        log.write(f"download [{podcast}] '{episode_title}' on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.flush()


# Function to download the latest podcast
def download(rss_feed_url, download_folder, latest, relative, first, last, transcribeAsWell, sync, dryrun):
    # Ensure the download folder exists
    os.makedirs(download_folder, exist_ok=True)

    # Get the name of the directory itself
    folder_name = os.path.basename(download_folder)

    # Path to store the last modified time or ETag
    metadata_path = os.path.join(download_folder, "feed_metadata.json")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    podcatch = False  # Flag to track if new episodes are downloaded

    # Perform header check only if the latest flag is set
    if latest:
        # Load previous metadata if it exists
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as meta_file:
                metadata = json.load(meta_file)
                if "Last-Modified" in metadata:
                    headers["If-Modified-Since"] = metadata["Last-Modified"]
                if "ETag" in metadata:
                    headers["If-None-Match"] = metadata["ETag"]
        else:
            metadata = {}

        # Make a HEAD request to check for changes
        try:
            response = requests.head(rss_feed_url, headers=headers, allow_redirects=False)
            while response.status_code in (301, 302):
                # Follow the redirect
                rss_feed_url = response.headers.get("Location")
                print(f"[{folder_name}] Redirected to: {rss_feed_url}", file=sys.stderr)
                response = requests.head(rss_feed_url, headers=headers, allow_redirects=False)

            if response.status_code == 304:
                print(f"[{folder_name}] No changes detected in the RSS feed since the last check.", file=sys.stderr)
                return
            elif response.status_code != 200:
                print(f"[{folder_name}] Failed to fetch the RSS feed. HTTP Status Code: {response.status_code}", file=sys.stderr)
                return

            # Update metadata with the latest headers
            if "Last-Modified" in response.headers:
                metadata["Last-Modified"] = response.headers["Last-Modified"]
            if "ETag" in response.headers:
                metadata["ETag"] = response.headers["ETag"]

            # Save updated metadata
            with open(metadata_path, "w", encoding="utf-8") as meta_file:
                json.dump(metadata, meta_file, ensure_ascii=False, indent=4)

        except requests.exceptions.RequestException as e:
            print(f"[{folder_name}] Error making HEAD request: {e}", file=sys.stderr)
            return

    # Parse the RSS feed
    try:
        feed = parse(rss_feed_url)
    except Exception as e:
        print(f"[{folder_name}] Error parsing RSS feed: {e}", file=sys.stderr)
        return

    # Check if the feed has entries
    if not feed.entries:
        print(f"[{folder_name}] No episodes found in the RSS feed.", file=sys.stderr)
        return
    else:
        print(f"[{folder_name}] {len(feed.entries)} Entries in total", file=sys.stderr)

    # Get the episodes
    if relative:
        entries = feed.entries
    else:
        entries = sorted(feed.entries, key=lambda e: e.get("published_parsed"))

    for idx in range(first - 1, last):
        latest_episode = entries[idx]
        episode_title = latest_episode.title
        media_url = latest_episode.enclosures[0].href  # Get the media URL from the 'enclosures'

        file_base = episode_title.replace(" ", "_").replace("/", "_").replace(":", "_").replace("'", "_").replace('"', "_")
        mp3name = file_base + ".mp3"
        infoname = file_base + ".info"

        mp3path = os.path.join(download_folder, mp3name)
        infopath = os.path.join(download_folder, infoname)

        # Check if file already exists
        if os.path.exists(mp3path):
            print(f"[{folder_name}] {mp3path} already downloaded", file=sys.stderr)
            if latest:
                break
        else:
            # Download the episode
            print(f"[{folder_name}] Downloading: {episode_title}", file=sys.stderr)
            try:
                response = requests.get(media_url, headers=headers, stream=True, allow_redirects=True)
            except requests.exceptions.RequestException as e:
                print(f"[{folder_name}] Error downloading episode: {e}", file=sys.stderr)
                continue

            if dryrun:
                print(f"[{folder_name}] Dryrun: Not downloading")
                continue
            if response.status_code == 200:
                with open(mp3path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"[{folder_name}] {mp3path}")
                json.dump(latest_episode, open(infopath, "w", encoding="utf8"), ensure_ascii=False, indent=4)
                process_mp3(mp3path)
                logdownload(folder_name, episode_title)
                podcatch = True  # Mark that a new episode was downloaded
                if transcribe:
                    if transcribeAsWell:
                        transcribe(mp3path)
                        if sync:
                            print(f"[{folder_name}] Marked for syncing to NAS")
                    else:
                        print(f"[{folder_name}] Downloaded but did NOT transcribe {mp3path}")
            else:
                print(f"[{folder_name}] Failed to download the episode. HTTP Status Code: {response.status_code}", file=sys.stderr)

    # Sync only if new episodes were downloaded
    if sync and podcatch:
        print(f"[{folder_name}] Syncing to NAS")
        command = f"rsync --exclude='*.meta' -avz --progress {download_folder}/ mark@rpm17.local:/volume1/data/languages/japanese/podcasts/content/{folder_name}"
        print(command)
        os.system(command)
    elif sync:
        print(f"[{folder_name}] No new episodes downloaded. Skipping sync.", file=sys.stderr)

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

    group.add_argument("-l", "--latest", help="download the latest episodes", action="store_true")

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
latest = getattr(args, "latest")
if offs or latest:
    relative = True
else:
    offs = getattr(args, "absolute")
if latest:
    offs = [1, 5]
first = offs[0]
if len(offs) > 1:
    last = offs[1]
else:
    last = first

conf = config.getConfig(feedfolder)
rss_feed_url = conf["feed"]

# rss_feed_url = open(feedfile).read()
download_folder = feedfolder
download(rss_feed_url, download_folder, latest, relative, first, last, getattr(args,"transcribe"), getattr(args,"sync"), getattr(args,"dryrun"))
