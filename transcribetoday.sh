for file in $(find content -type f -name "*.mp3" -newerct "00:00"); do
    python3 transcribe.py "$file"
done