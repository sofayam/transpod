from pydub import AudioSegment # type: ignore
from pydub.silence import detect_silence

# Parameters for silence detection
min_silence_len = 500  # Minimum silence duration in milliseconds 
chunk_len = 15 # minutes


# Load the MP3 file
audio = AudioSegment.from_file("/Volumes/ex0/repos/transpod/content/trendwatchee/trend_20241216_1.mp3", format="mp3")

# audio = AudioSegment.from_file("/Volumes/ex0/repos/transpod/content/teppei/Teppei1286.mp3", format="mp3")

silence_thresh = audio.dBFS - 14  # Silence threshold in dB (adjust as needed)


# Detect silence segments (returns start and end times in milliseconds)
silences = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
silences = [(start, end) for start, end in silences]

# Split the audio into chunks of approximately 15 minutes (900,000 ms)
chunk_duration = chunk_len * 60 * 1000  # 15 minutes in milliseconds
start_time = 0
chunk_counter = 1

for silence_start, silence_end in silences:
    print("Found a silence at ", silence_start)
    # Check if the current chunk exceeds the desired duration
    if silence_start - start_time >= chunk_duration:
        # Export the current chunk
        chunk = audio[start_time:silence_start]
        chunk.export(f"chunk_{chunk_counter}.mp3", format="mp3")
        chunk_counter += 1
        start_time = silence_start

# Export the last chunk if any audio is left
if start_time < len(audio):
    chunk = audio[start_time:]
    chunk.export(f"chunk_{chunk_counter}.mp3", format="mp3")

print(f"Audio successfully split into {chunk_counter} chunks.")