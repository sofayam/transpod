import os
import json
import re
from collections import Counter, defaultdict
import argparse
import html
import urllib.parse
import pymorphy3

def create_concordance(subfolder, n, lang, limit_files=None, top_n=None):
    """
    Reads all transcripts from *.json files in a subfolder,
    normalizes Russian words to their base form, creates a concordance,
    and generates a static HTML page to display the results.
    """
    morph = pymorphy3.MorphAnalyzer()
    content_dir = 'content'
    podcast_dir = os.path.join(content_dir, subfolder)

    if not os.path.isdir(podcast_dir):
        print(f"Error: Subfolder '{subfolder}' not found in '{content_dir}'.")
        return

    all_segments = []
    json_files = [f for f in os.listdir(podcast_dir) if f.endswith('.json')]

    if limit_files:
        json_files = json_files[:limit_files]
        print(f"--- Limiting to first {len(json_files)} files for testing. ---")


    for file_name in json_files:
        file_path = os.path.join(podcast_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                segments = json.load(f)
                for segment in segments:
                    segment['source_file'] = file_name
                all_segments.extend(segments)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {file_name}")
            except TypeError:
                print(f"Warning: Unexpected data type in {file_name}, skipping.")

    root_word_counts = Counter()
    root_to_original_words = defaultdict(set)
    all_original_words = []

    for segment in all_segments:
        words = re.findall(r'\b[а-яА-ЯёЁ]+\b', segment.get('text', '').lower())
        for word in words:
            normal_form = morph.parse(word)[0].normal_form
            root_word_counts[normal_form] += 1
            root_to_original_words[normal_form].add(word)
            all_original_words.append(word)

    if not root_word_counts:
        print("No Russian words found in the JSON files.")
        return

    sorted_root_words = root_word_counts.most_common()
    if top_n:
        sorted_root_words = sorted_root_words[:top_n]

    concordance = {root_word: [] for root_word, count in sorted_root_words}
    for segment in all_segments:
        words_in_segment = set(re.findall(r'\b[а-яА-ЯёЁ]+\b', segment.get('text', '').lower()))
        processed_roots_in_segment = set()

        for word in words_in_segment:
            root_word = morph.parse(word)[0].normal_form
            if root_word in concordance and root_word not in processed_roots_in_segment:
                if len(concordance[root_word]) < n:
                    concordance[root_word].append(segment)
                processed_roots_in_segment.add(root_word)


    total_unique_root_words = len(root_word_counts)
    root_words_once = sum(1 for count in root_word_counts.values() if count == 1)

    lang_map = {
        'ru': 'Russian',
        'sv': 'Swedish',
        'en': 'English',
        'ja': 'Japanese',
    }
    full_lang_name = lang_map.get(lang.lower(), lang.capitalize())

    html_file_name = f"concordance_{subfolder}.html"
    with open(html_file_name, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang=\"en\">\n")
        f.write("<head>\n")
        f.write("    <meta charset=\"UTF-8\">\n")
        f.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
        f.write(f"    <title>Concordance for {subfolder} (Russian)</title>\n")
        f.write("\n    <style>\n        body { font-family: sans-serif; line-height: 1.4; margin: 10px; background-color: #f8f9fa; color: #212529; }\n        h1 { color: #005a9c; text-align: center; margin-bottom: 10px; }\n        .stats { background-color: #e7f3fe; border-left: 5px solid #2196F3; margin: 10px 0; padding: 10px; border-radius: 5px; }\n        .stats p { margin: 2px 0; }\n        .word-container { column-gap: 10px; }\n        .word-entry { margin-bottom: 5px; background-color: #fff; padding: 5px 10px; border-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); break-inside: avoid; }\n        summary { font-size: 1.1em; font-weight: bold; color: #005a9c; cursor: pointer; padding: 2px 5px; display: flex; justify-content: space-between; align-items: center; }\n        .word-text { flex-grow: 1; }\n        .original-forms { font-size: 0.8em; color: #6c757d; margin-left: 10px; }\n        .dict-link { font-size: 0.8em; margin-left: 10px; text-decoration: none; color: #007bff; }\n        details[open] summary { margin-bottom: 5px; }\n        ul { list-style-type: none; padding-left: 15px; }\n        li { margin-bottom: 5px; border-left: 2px solid #005a9c; padding-left: 8px; }\n        .timestamp { font-weight: bold; color: #d9534f; }\n        .context { font-style: italic; }\n        .source { font-size: 0.8em; color: #777; }\n        @media (min-width: 600px) { .word-container { column-count: 2; } }\n        @media (min-width: 900px) { .word-container { column-count: 3; } }\n        @media (min-width: 1200px) { .word-container { column-count: 4; } }\n    </style>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write('<a href="/">Back to Podcasts</a>\n')
        f.write(f"<h1>Concordance for '{subfolder}' (Russian Root Forms)</h1>\n")

        f.write("<div class=\"stats\">\n")
        f.write(f"    <p><strong>Total Unique Root Words:</strong> {total_unique_root_words}</p>\n")
        f.write(f"    <p><strong>Root Words Occurring Only Once:</strong> {root_words_once}</p>\n")
        f.write("</div>\n")

        f.write(f"<h2>All Words (Up to {n} Occurrences Each)</h2>\n")
        f.write("<div class=\"word-container\">\n")

        for root_word, count in sorted_root_words:
            f.write("<div class=\"word-entry\">\n")
            f.write("    <details>\n")
            dict_url = f"https://en.wiktionary.org/wiki/{urllib.parse.quote(root_word)}#{full_lang_name}"
            original_forms_str = ", ".join(sorted(list(root_to_original_words[root_word])))
            f.write(f'        <summary><span class=\"word-text\">{html.escape(root_word)} ({count})</span><span class=\"original-forms\">({html.escape(original_forms_str)})</span><a class=\"dict-link\" href=\"{dict_url}\" target=\"_blank\">Lookup</a></summary>\n')
            f.write("        <ul>\n")
            
            sorted_occurrences = sorted(concordance[root_word], key=lambda x: (x['source_file'], x.get('start', 0)))
            for occ in sorted_occurrences:
                start_time = occ.get('start', 0)
                if isinstance(start_time, (int, float)):
                    minutes, seconds = divmod(start_time, 60)
                    start_time_str = f"{int(minutes):02d}:{int(seconds):02d}"
                else:
                    start_time_str = "N/A"

                episode_name = os.path.splitext(occ['source_file'])[0]
                play_url = f"/play/{subfolder}/{urllib.parse.quote(episode_name)}?t={start_time}"

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
    parser = argparse.ArgumentParser(description='Generate a concordance from Russian podcast transcripts using root word forms.')
    parser.add_argument('subfolder', type=str, help='The subfolder in the "content" directory containing the podcast episodes.')
    parser.add_argument('-n', type=int, default=50, help='The maximum number of occurrences to display for each word (default: 50).')
    parser.add_argument('--top-n', type=int, help='Limit the output to the top N most frequent root words.')
    parser.add_argument('--lang', type=str, default='ru', help='The language of the podcast (default: ru).')
    parser.add_argument('--limit-files', type=int, help='Limit the number of files to process for testing.')
    args = parser.parse_args()

    create_concordance(args.subfolder, args.n, args.lang, args.limit_files, args.top_n)
