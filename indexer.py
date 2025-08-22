

import os
import json
import re
import sqlite3
import argparse
from collections import Counter
from janome.tokenizer import Tokenizer

# Initialize the tokenizer for Japanese
t = Tokenizer()

# Load configuration
with open('indexer.config.json', 'r') as f:
    config = json.load(f)

INDEXLANGUAGES = config['INDEXLANGUAGES']
REFMAX = config['REFMAX']
REPMAX = config['REPMAX']

def get_podcast_language(podcast_dir):
    """Reads the language from the _config.md file in the podcast directory."""
    config_path = os.path.join(podcast_dir, '_config.md')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config_data = json.load(f)
                return config_data.get('lang', 'ja') # Use 'lang' and default to 'ja'
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {config_path}")
    return 'ja' # Default to 'ja' if the file doesn't exist



def has_consecutive_repetitions(words, max_repetitions):
    """Checks for consecutive repetitions of the same word."""
    if not words:
        return False
    
    repetition_count = 1
    for i in range(1, len(words)):
        if words[i] == words[i-1]:
            repetition_count += 1
        else:
            repetition_count = 1
        
        if repetition_count > max_repetitions:
            return True
            
    return False

def create_database_schema(cursor):
    """Creates the database schema."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY,
            word TEXT UNIQUE,
            occurrences INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            word_id INTEGER,
            language TEXT,
            podcast_name TEXT,
            episode_name TEXT,
            start_time REAL,
            end_time REAL,
            full_text TEXT,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    ''')

def index_podcasts(content_dir, db_path, log_path, limit_files=None):
    """Indexes all podcasts in the content directory."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_database_schema(cursor)

    with open(log_path, 'w', encoding='utf-8') as log_file:
        for podcast_name in os.listdir(content_dir):
            podcast_dir = os.path.join(content_dir, podcast_name)
            if not os.path.isdir(podcast_dir):
                continue

            lang = get_podcast_language(podcast_dir)
            if not lang or lang not in INDEXLANGUAGES:
                continue

            print(f"Indexing podcast: {podcast_name} ({lang})")

            files_to_process = [f for f in os.listdir(podcast_dir) if f.endswith('.json')]
            if limit_files:
                files_to_process = files_to_process[:limit_files]
                print(f"--- Limiting to first {len(files_to_process)} files for testing. ---")

            for file_name in files_to_process:
                base_name = os.path.splitext(file_name)[0]
                mp3_path = os.path.join(podcast_dir, base_name + ".mp3")

                if not os.path.exists(mp3_path):
                    continue

                episode_name = base_name
                file_path = os.path.join(podcast_dir, file_name)

                # Check if the episode has already been indexed
                cursor.execute("SELECT id FROM entries WHERE podcast_name = ? AND episode_name = ? LIMIT 1", (podcast_name, episode_name))
                if cursor.fetchone():
                    print(f"Skipping already indexed episode: {podcast_name}/{episode_name}")
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        segments = json.load(f)
                        #for segment in segments:
                        #    print(f"------> Found {len(segments)} segments.")
                        for segment in segments:
                            text = segment.get('text', '')
                            
                            if lang == 'ja':
                                words = [token.surface for token in t.tokenize(text)]
                            else:
                                words = re.findall(r'\b\w+\b', text)

                            # Check for junk segments
                            if has_consecutive_repetitions(words, REPMAX):
                                log_file.write(f"Rejected segment in {file_path}: {text}\n")
                                continue

                            for word in words:
                                normalized_word = word.lower()

                                # Get word_id, creating the word if it doesn't exist
                                cursor.execute("SELECT id, occurrences FROM words WHERE word = ?", (normalized_word,))
                                result = cursor.fetchone()
                                if result:
                                    word_id, occurrences = result
                                else:
                                    cursor.execute("INSERT INTO words (word, occurrences) VALUES (?, 0)", (normalized_word,))
                                    word_id = cursor.lastrowid
                                    occurrences = 0

                                # Check REFMAX
                                if occurrences >= REFMAX:
                                    continue

                                # Add the entry
                                cursor.execute('''
                                    INSERT INTO entries (word_id, language, podcast_name, episode_name, start_time, end_time, full_text)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (word_id, lang, podcast_name, episode_name, segment.get('start'), segment.get('end'), text))

                                # Update word occurrences
                                cursor.execute("UPDATE words SET occurrences = occurrences + 1 WHERE id = ?", (word_id,))

                    except (json.JSONDecodeError, TypeError) as e:
                        log_file.write(f"Error processing {file_path}: {e}\n")

    conn.commit()
    conn.close()
    print(f"Indexing complete. Database saved to {db_path}")
    print(f"Rejected segments logged to {log_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Index podcast transcripts into an SQLite database.')
    parser.add_argument('--content_dir', type=str, default='content', help='The directory containing the podcast content.')
    parser.add_argument('--db_path', type=str, default='concordance.db', help='The path to the SQLite database file.')
    parser.add_argument('--log_path', type=str, default='rejected_segments.log', help='The path to the log file for rejected segments.')
    parser.add_argument('--limit-files', type=int, help='Limit the number of files to process for testing.')
    args = parser.parse_args()

    index_podcasts(args.content_dir, args.db_path, args.log_path, args.limit_files)
