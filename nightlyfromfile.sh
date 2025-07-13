#!/bin/bash

# Check if a filename is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_podcast_list_file> [optional_argument_for_getpodcasts.py]"
    exit 1
fi

PODCAST_LIST_FILE="$1"
GETPODCASTS_ARG="$2" # This will capture the optional argument for getpodcasts.py

if [ ! -f "$PODCAST_LIST_FILE" ]; then
    echo "Error: Podcast list file '$PODCAST_LIST_FILE' not found."
    exit 1
fi

while IFS= read -r pc; do
    # Skip empty lines or lines that are just whitespace
    if [[ -z "$pc" || "$pc" =~ ^[[:space:]]*$ ]]; then
        continue
    fi
    echo "Processing podcast: $pc"
    python getpodcasts.py "content/$pc" -l -t -s "$GETPODCASTS_ARG"
done < "$PODCAST_LIST_FILE"
