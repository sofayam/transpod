#!/bin/zsh
conda activate transpod


for mp3 in content/**/*.mp3(.); do
  
  json=${mp3%.mp3}.json
  if [[ ! -f $json ]]; then
    dir=$(dirname "$mp3")
    if [[ -f "$dir/nochunk.md" ]]; then
      python transcribe.py "$mp3" 
    fi
  fi
done
