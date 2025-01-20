source setupconda.sh
conda activate transpod

for mp3 in content/**/*.mp3(.); do
  json=${mp3%.mp3}.json
  if [[ ! -f $json ]]; then
    python transcribe.py "$mp3" 
  fi
done