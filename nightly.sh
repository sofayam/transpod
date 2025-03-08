
for pc in "teppeiha" "teppeinoriko" "teppeibegin"; do
    python getpodcasts.py content/$pc -r 1 3 -t -s
done

