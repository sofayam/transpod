conda activate transpod
for f in content/*; do
    if [[ -d $f ]]; then
        echo "Getting metadata for directory: $f"
        python getpodcasts.py $f -a 1 -d -m
    fi
done
