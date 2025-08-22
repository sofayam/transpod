

python find_live_dirs.py | while read -r pc; do
    if [ -d "content/$pc" ]; then
        # echo "Processing directory: $directory"
       
        python getpodcasts.py content/$pc  -l -t -s $1
    fi
done


