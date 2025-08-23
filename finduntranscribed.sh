#!/usr/bin/env zsh
#
# Script to check for missing JSON files corresponding to MP3 files.
# Traverses all subdirectories and reports MP3 files without matching JSON files.
#

# Function to check for missing JSON files
check_mp3_json_pairs() {
    local directory="$1"
    local -a missing_files
    local mp3_count=0
    local missing_count=0
    
    # Check if directory exists
    if [[ ! -d "$directory" ]]; then
        echo "Error: Directory '$directory' does not exist." >&2
        return 1
    fi
    
    echo "Checking directory: $(realpath "$directory")"
    echo "$(printf '%*s' 50 | tr ' ' '-')"
    
    # Use zsh globbing to find all MP3 files recursively
    # Enable extended globbing and null_glob options
    setopt extended_glob null_glob
    
    # Find all MP3 files recursively
    for mp3_file in "$directory"/**/*.mp3(N); do
        ((mp3_count++))
        
        # Get the corresponding JSON filename
        local json_file="${mp3_file:r}.json"
        
        # Check if JSON file exists
        if [[ ! -f "$json_file" ]]; then
            missing_files+=("$mp3_file")
            ((missing_count++))
        fi
    done
    
    # Report results
    if (( missing_count > 0 )); then
        echo "Found $missing_count MP3 file(s) without corresponding JSON files:"
        echo
        
        local i=1
        for file in "${missing_files[@]}"; do
            printf "%s\n"  "$file"
            python transcribefast.py "$file"
            ((i++))
        done
    else
        echo "All MP3 files have corresponding JSON files! ✓"
    fi
    
    echo "$(printf '%*s' 50 | tr ' ' '-')"
    echo "Total MP3 files checked: $mp3_count"
    
    # Return the count of missing files for exit status
    return $missing_count
}

# Main execution
main() {
    local directory
    
    # Get directory from command line argument or prompt user
    if [[ $# -gt 0 ]]; then
        directory="$1"
    else
        echo -n "Enter directory path (or press Enter for current directory): "
        read directory
        [[ -z "$directory" ]] && directory="."
    fi
    
    check_mp3_json_pairs "$directory"
}

# Show usage if --help is passed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    cat << EOF
Usage: $(basename "$0") [directory]

Check for MP3 files without corresponding JSON files in a directory tree.

Arguments:
    directory    Directory to check (default: current directory)

Options:
    -h, --help   Show this help message

Examples:
    $(basename "$0")                    # Check current directory
    $(basename "$0") /path/to/music     # Check specific directory
EOF
    exit 0
fi

# Run main function
main "$@"
