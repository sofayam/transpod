#!/bin/sh
#  the command we want to run 

# inotifywait -mrq -e moved_to /volume1/data/languages/japanese/podcasts/content/

# ===== Parameters =====
WATCH_DIR="volume2/transpodcontent/content"
FILE_EXT="info"
HANDLER_SCRIPT="newinfoadder.sh"

# ===== Sanity checks =====
if [ -z "$WATCH_DIR" ] || [ -z "$FILE_EXT" ] || [ -z "$HANDLER_SCRIPT" ]; then
  echo "Usage: $0 <directory> <file extension> <handler script>"
  echo "Example: $0 /foo .info /path/to/handle_new_file.sh"
  exit 1
fi

if [ ! -d "$WATCH_DIR" ]; then
  echo "Error: '$WATCH_DIR' is not a directory"
  exit 1
fi

if [ ! -x "$HANDLER_SCRIPT" ]; then
  echo "Error: handler script '$HANDLER_SCRIPT' is not executable"
  exit 1
fi

# ===== Watcher Loop =====
echo "Watching '$WATCH_DIR' for new *$FILE_EXT files..."
inotifywait -mr -e moved_to --format '%w%f' "$WATCH_DIR" | while read NEWFILE; do
  case "$NEWFILE" in
    *"$FILE_EXT")
      echo "[$(date)] Detected new file: $NEWFILE"
      "$HANDLER_SCRIPT" "$NEWFILE"
      ;;
  esac
done