conda activate transpod

for mp3 in content/**/*.mp3(.); do
    python splitlong.py $mp3
done