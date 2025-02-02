conda activate transpod
for pc in "teppeiha" "teppeinoriko" "teppei"; do
    python getpodcasts content/$pc -r 1
done

source transcribenewnochunk.sh

