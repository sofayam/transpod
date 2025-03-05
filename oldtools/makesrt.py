import json
import sys

def whisper_to_srt(whisper_output, srt_file_path):
    """
    Converts Whisper's transcription output to SRT format.

    Parameters:
        whisper_output (dict): Whisper's JSON transcription output.
        srt_file_path (str): Path to save the resulting SRT file.
    """
    def format_timestamp(seconds):
        """Formats seconds into SRT timestamp (HH:MM:SS,ms)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

    # Open the SRT file for writing
    with open(srt_file_path, "w", encoding="utf-8") as srt_file:
        for idx, segment in enumerate(whisper_output):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text']

            # Write the SRT entry
            srt_file.write(f"{idx}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

if __name__ == "__main__":
    # Example usage
    whisper_output_file = sys.argv[1]
    # whisper_output_file = "content/kinonotabi/Kino_no_Tabi_01.DVD(h264.aac)[KAA][6B00682C].mkv.json"  # Replace with your Whisper JSON file
    srt_output_file = whisper_output_file + ".srt"

    # Load Whisper's JSON output
    with open(whisper_output_file, "r", encoding="utf-8") as file:
        whisper_output = json.load(file)

    # Convert to SRT
    whisper_to_srt(whisper_output, srt_output_file)
    print(f"SRT file created: {srt_output_file}")