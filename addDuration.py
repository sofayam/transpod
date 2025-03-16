import json
import os
import sys
from mutagen.mp3 import MP3

def format_duration(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_mp3_duration(mp3_path):
    """Calculate duration of an MP3 file and return it as HH:MM:SS."""
    try:
        audio = MP3(mp3_path)
        duration_seconds = int(audio.info.length)  # Round to whole seconds
        return format_duration(duration_seconds)
    except Exception as e:
        print(f"Error reading {mp3_path}: {e}")
        return None

def process_mp3(mp3_path):
    """Ensure the .info file exists and contains the duration in HH:MM:SS format."""
    if not os.path.exists(mp3_path):
        print(f"MP3 file not found: {mp3_path}")
        return

    info_path = os.path.splitext(mp3_path)[0] + ".info"
    duration = get_mp3_duration(mp3_path)

    if duration is None:
        print(f"Failed to get duration for {mp3_path}")
        return

    if os.path.exists(info_path):
        # Update existing .info file
        try:
            with open(info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {}

    #    if "itunes_duration" not in data:
        if True:
            data["itunes_duration"] = duration
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Updated {info_path} with duration: {duration}")
        else:
            print(f"{info_path} already has duration ({data['itunes_duration']})")
    else:
        # Create new .info file
        data = {"itunes_duration": duration}
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Created {info_path} with duration: {duration}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py file.mp3")
        sys.exit(1)

    mp3_file = sys.argv[1]

    if not mp3_file.endswith(".mp3"):
        print("Error: Please provide an .mp3 file.")
        sys.exit(1)

    process_mp3(mp3_file)
