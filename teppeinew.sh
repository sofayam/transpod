conda activate transpod
for pc in "teppeiha" "teppeinoriko" "teppei"; do
    python getlatest.py content/$pc
done

source transcribenewnochunk.sh

