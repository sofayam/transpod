
setopt null_glob

for mp3 in **/*.mp3; do
  txt="${mp3%.mp3}.json.txt"
  [[ -e "$txt" ]] || print "$mp3"
done
