conda activate transpod
for pc in "teppeiha" "teppeinoriko" "teppei"; do
    python getpodcasts.py content/$pc -r 1 3
done

source transcribenewnochunk.sh

