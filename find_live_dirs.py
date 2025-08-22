
import os
import json
import glob

def find_live_directories(root_dir):
    live_dirs = []
    for filepath in glob.glob(os.path.join(root_dir, '**', '_config.md'), recursive=True):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data.get('live') == 1:
                    live_dirs.append(os.path.basename(os.path.dirname(filepath)))
        except (json.JSONDecodeError, IOError):
            continue
    return live_dirs

if __name__ == '__main__':
    content_dir = 'content'
    live_directories = find_live_directories(content_dir)
    for directory in live_directories:
        print(directory)
