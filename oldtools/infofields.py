import sys
import json
import os
import unicodedata
from collections import defaultdict

def normalize_filename(filename):
    """Normalize the filename to handle weird Unicode characters."""
    return unicodedata.normalize('NFC', filename)

def analyze_json_files(json_files):
    """Analyze the fields in the JSON files and provide statistics."""
    field_counts = defaultdict(int)
    total_files = len(json_files)

    for json_file in json_files:
        normalized_file = normalize_filename(json_file)
        with open(normalized_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for field in data.keys():
                field_counts[field] += 1

    always_present = [field for field, count in field_counts.items() if count == total_files]
    most_frequently_present = max(field_counts, key=field_counts.get)

    print(f"Total JSON files analyzed: {total_files}")
    print("\nField occurrence counts:")
    for field, count in field_counts.items():
        print(f"{field}: {count} files")

    print("\nFields always present:")
    for field in always_present:
        print(field)

    print(f"\nMost frequently present field: {most_frequently_present} ({field_counts[most_frequently_present]} files)")

if __name__ == "__main__":
    json_files = [line.strip() for line in sys.stdin]
    analyze_json_files(json_files)