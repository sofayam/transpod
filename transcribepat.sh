#!/bin/zsh

# Enable extended globbing for more pattern matching options
setopt extendedglob

# Check if the user provided a pattern
if [[ -z "$1" ]]; then
  echo "Usage: $0 'pattern'"
  exit 1
fi

# Expand the pattern
files=(${~1})  # The `~` forces globbing on the argument

# Check if any files matched
if (( ${#files} == 0 )); then
  echo "No files matched pattern: $1"
  exit 1
fi

# Process the matched files
for file in "${files[@]}"; do
  time python transcribefast.py $file
done

