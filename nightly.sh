
for pc in "okkei" "teppeiha" "teppeinoriko" "teppeibegin" "noriko" "hotcast" "trendwatchee" "shun" "miku" "haru" "sayuri" "yuyu" "moeko" "italamor" "easyital" "russmax" "portleo" "orestehist" "espconjuan"; do
    python getpodcasts.py content/$pc -l -t -s $1
done

