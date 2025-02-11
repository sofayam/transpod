for mp3 in $(find content -type f -name "*.mp3" -newerct "00:00"); do
  json=${mp3%.mp3}.json
  if [[ ! -f $json ]]; then
    python transcribe.py "$mp3" 
  fi
done