ffmpeg -i $1 -c:a libmp3lame -b:a 128k tmp.mp3
mv tmp.mp3 $1

