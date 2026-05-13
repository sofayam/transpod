#!/bin/zsh

# Enable extended globbing for more pattern matching options
setopt extendedglob


# Parameters
# $1 base directory
# $2 starting number
# $3 host (default: localhost)  

# Check if the user provided a base directory and a number
if [[ -z "$1" ]] || [[ -z "$2" ]]; then
  echo "Usage: $0 'base_directory' 'starting_number'"
  exit 1
fi

if [[ -n "$3" ]]; then
  host="$3"
else
  host="localhost"
fi


# start a loop on the number supplied as $2, defaulting to 1 if not provided
for ((i = $2;; i++)); do
  # construct a pattern in the form of "base_directory/#<number>*.txt" 
  #  whereby the first character in * is not a number (to avoid matching files that have already been processed)
  # this has to work for unicode numbers, so we can't just use [^0-9], we have to use a negative lookahead for any unicode digit

  pattern="$1/\#${i}(*~[[:digit:]]*).json.txt"

  # Expand the pattern
  files=(${~pattern})  # The `~` forces globbing on the argument
  # Check if any files matched
  if (( ${#files} == 0 )); then
    echo "No files matched pattern: $pattern. Assuming no more files to process. Exiting."
    exit 0
  fi
  # check that only one file matches the pattern, if more than one file matches, print an error and exit
  if (( ${#files} > 1 )); then
    echo "Error: More than one file matched pattern: $pattern. Please check the files in the directory and ensure they are named correctly. Exiting."
    exit 1
  fi

  # process the matched file
  file="${files[1]}"
  echo "Processing file: $file"
  # iterate over the section types and call summarise.py for each section type
  for section in japanese english vocabulary idioms culture; do   
    echo "Processing file $file section: $section"
    python summarise.py $file --save --section $section --host $host
  done
done

