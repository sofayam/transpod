# get an mp3 from an avi (or maybe even an mkv?)
ffmpeg -i "$1"  -q:a 0 -map a "$1".mp3
