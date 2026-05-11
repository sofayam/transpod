#!/bin/bash
# summarise.sh
MODEL=qwen3.5:9b
echo "Summarising $1 using $MODEL..."

# derive the name of the output file by replacing the extension with .summary.txt
output_file="${1%.*}.summary"

# if the output file already exists, skip the summarisation
if [ -f "$output_file" ]; then
    echo "Output file $output_file already exists. Skipping summarisation."
    exit 0
fi

cat "$1" | ollama run "$MODEL" --think=false "Please summarise this transcript of a Japanese Podcast, into English. Include: main topics discussed, and any significant opinions." > "$output_file"


