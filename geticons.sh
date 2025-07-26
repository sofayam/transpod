conda activate transpod
for f in content/*; do
    if [[ -d $f ]]; then
        echo "Getting icon for directory: $f"
        python getpodcasts.py $f -a 1 -d -i
    fi
done