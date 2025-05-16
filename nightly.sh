
for pc in "okkei" "teppeiha" "teppeinoriko" "teppeibegin" "noriko" "hotcast" "trendwatchee" "shun" "miku" "sayuri" "yuyu" "nhkworldreport" "moeko"; do
    python getpodcasts.py content/$pc -l -t -s $1
done

