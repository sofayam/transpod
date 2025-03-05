#!/bin/zsh
conda activate transpod

for mp3 in content/$1/*.mp3(.); do
  
  json=${mp3%.mp3}.json
  if [[ ! -f $json ]]; then
    python transcribe.py "$mp3" 
  fi
done
