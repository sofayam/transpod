
for pc in "teppeiha" "teppeinoriko" "teppeibegin" "noriko"; do
    python getpodcasts.py content/$pc -r 1 5 -t -s $1
done

