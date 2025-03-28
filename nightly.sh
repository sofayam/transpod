
for pc in "okkei" "teppeiha" "teppeinoriko" "teppeibegin" "noriko" "hotcast" "trendwatchee" "shun" "miku" "sayuri" "yuyu"; do
    python getpodcasts.py content/$pc -r 1 2 -t -s $1
done

