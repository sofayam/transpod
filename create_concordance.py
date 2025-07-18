import os
import json
import re
from collections import Counter
import argparse
import html
import urllib.parse

def create_concordance(subfolder, n, base_url, lang):
    """
    Reads all transcripts from *.json files in a subfolder,
    creates a concordance of all words, and generates a static
    HTML page to display the results, with a limit on the number
    of occurrences shown per word.
    """
    content_dir = 'content'
    podcast_dir = os.path.join(content_dir, subfolder)

    if not os.path.isdir(podcast_dir):
        print(f"Error: Subfolder '{subfolder}' not found in '{content_dir}'.")
        return

    # 1. Find all JSON files and read their content
    all_segments = []
    json_files = [f for f in os.listdir(podcast_dir) if f.endswith('.json')]

    for file_name in json_files:
        file_path = os.path.join(podcast_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                segments = json.load(f)
                # Add filename to each segment for context
                for segment in segments:
                    segment['source_file'] = file_name
                all_segments.extend(segments)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {file_name}")
            except TypeError:
                print(f"Warning: Unexpected data type in {file_name}, skipping.")


    # 2. Tokenize words and calculate frequency
    all_words = []
    for segment in all_segments:
        # Normalize text to lowercase and find all word-like tokens
        words = re.findall(r'\b\w+\b', segment.get('text', '').lower())
        all_words.extend(words)

    if not all_words:
        print("No words found in the JSON files.")
        return

    word_counts = Counter(all_words)
    # Sort words by frequency
    sorted_words = word_counts.most_common()

    # 3. Find occurrences for each word, respecting the n limit
    concordance = {word: [] for word, count in sorted_words}
    for segment in all_segments:
        # Find unique words in this segment to avoid duplicate appends for the same segment
        words_in_segment = set(re.findall(r'\b\w+\b', segment.get('text', '').lower()))
        for word in words_in_segment:
            # Check if the word is in our list and if we still need to find occurrences
            if word in concordance and len(concordance[word]) < n:
                concordance[word].append(segment)

    # Calculate statistics
    total_unique_words = len(word_counts)
    words_once = sum(1 for count in word_counts.values() if count == 1)

    # Calculate statistics
    total_unique_words = len(word_counts)
    words_once = sum(1 for count in word_counts.values() if count == 1)

    lang_map = {
        'sv': 'Swedish',
        'en': 'English',
        'ja': 'Japanese',
        # Add more language mappings as needed
    }
    # Get the full language name, default to the capitalized code if not found
    full_lang_name = lang_map.get(lang.lower(), lang.capitalize())

    # 4. Generate the HTML page
    html_file_name = f"concordance_{subfolder}.html"
    with open(html_file_name, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("<head>\n")
        f.write("    <meta charset=\"UTF-8\">\n")
        f.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
        f.write(f"    <title>Concordance for {subfolder}</title>\n")
        f.write("""
    <style>
        body { font-family: sans-serif; line-height: 1.4; margin: 10px; background-color: #f8f9fa; color: #212529; }
        h1 { color: #005a9c; text-align: center; margin-bottom: 10px; }
        .stats { background-color: #e7f3fe; border-left: 5px solid #2196F3; margin: 10px 0; padding: 10px; border-radius: 5px; }
        .stats p { margin: 2px 0; }
        .word-container { column-gap: 10px; }
        .word-entry { margin-bottom: 5px; background-color: #fff; padding: 5px 10px; border-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); break-inside: avoid; }
        summary { font-size: 1.1em; font-weight: bold; color: #005a9c; cursor: pointer; padding: 2px 5px; display: flex; justify-content: space-between; align-items: center; }
        .word-text { flex-grow: 1; }
        .dict-link { font-size: 0.8em; margin-left: 10px; text-decoration: none; color: #007bff; }
        details[open] summary { margin-bottom: 5px; }
        ul { list-style-type: none; padding-left: 15px; }
        li { margin-bottom: 5px; border-left: 2px solid #005a9c; padding-left: 8px; }
        .timestamp { font-weight: bold; color: #d9534f; }
        .context { font-style: italic; }
        .source { font-size: 0.8em; color: #777; }
        @media (min-width: 600px) { .word-container { column-count: 2; } }
        @media (min-width: 900px) { .word-container { column-count: 3; } }
        @media (min-width: 1200px) { .word-container { column-count: 4; } }
    </style>
""")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(f"<h1>Concordance for '{subfolder}'</h1>\n")

        # Add statistics section
        f.write("<div class=\"stats\">\n")
        f.write(f"    <p><strong>Total Unique Words:</strong> {total_unique_words}</p>\n")
        f.write(f"    <p><strong>Words Occurring Only Once:</strong> {words_once}</p>\n")
        f.write("</div>\n")

        f.write(f"<h2>All Words (Up to {n} Occurrences Each)</h2>\n")
        f.write("<div class=\"word-container\">\n")

        for word, count in sorted_words:
            f.write("<div class=\"word-entry\">\n")
            f.write("    <details>\n")
            dict_url = f"https://en.wiktionary.org/wiki/{urllib.parse.quote(word)}#{full_lang_name}"
            f.write(f'        <summary><span class=\"word-text\">\'{html.escape(word)}\' ({count})</span><a class=\"dict-link\" href=\"{dict_url}\" target=\"_blank\">Lookup</a></summary>\n')
            f.write("        <ul>\n")
            # Sort occurrences by file name and then by start time
            sorted_occurrences = sorted(concordance[word], key=lambda x: (x['source_file'], x.get('start', 0)))
            for occ in sorted_occurrences:
                start_time = occ.get('start', 0)
                # format time to be more readable
                if isinstance(start_time, (int, float)):
                    minutes, seconds = divmod(start_time, 60)
                    start_time_str = f"{int(minutes):02d}:{int(seconds):02d}"
                else:
                    start_time_str = "N/A"

                episode_name = os.path.splitext(occ['source_file'])[0]
                play_url = f"{base_url}/play/{subfolder}/{urllib.parse.quote(episode_name)}?t={start_time}"

                context_text = html.escape(occ.get('text', 'No context available.'))
                source_file = html.escape(occ.get('source_file', 'Unknown file'))
                f.write(f"            <li><span class=\"timestamp\"><a href=\"{play_url}\" target=\"_blank\">[{start_time_str}]</a></span> <span class=\"context\">...{context_text}...</span> <span class=\"source\">({source_file})</span></li>\n")
            f.write("        </ul>\n")
            f.write("    </details>\n")
            f.write("</div>\n")

        f.write("</div>\n")
        f.write("</body>\n")
        f.write("</html>\n")

    print(f"Successfully generated HTML report: {html_file_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a concordance from podcast transcripts.')
    parser.add_argument('subfolder', type=str, help='The subfolder in the "content" directory containing the podcast episodes.')
    parser.add_argument('-n', type=int, default=50, help='The maximum number of occurrences to display for each word (default: 50).')
    parser.add_argument('--base-url', type=str, default='http://localhost:8014', help='The base URL for the play links.')
    parser.add_argument('--lang', type=str, default='sv', help='The language of the podcast (default: sv).')
    args = parser.parse_args()

    create_concordance(args.subfolder, args.n, args.base_url, args.lang)
