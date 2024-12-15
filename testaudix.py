import streamlit as st
import time

from streamlit_advanced_audio import audix
import json

# Load your MP3 and transcription data
audio_file_path = "Teppei1286.mp3"  # Replace with your file
json_file_path = "teppei.json"
whisperjson = json.load(open(json_file_path))

transcription_data = whisperjson["segments"]
# transcription_data = [
#    {"start": 0.5, "end": 2.3, "text": "Hello, welcome to the demo."},
#    {"start": 2.5, "end": 4.0, "text": "This is synchronized audio transcription."}
# ]

    # Play audio in a separate thread
audiores = audix(audio_file_path)

def play_audio_with_sync(transcription):
    # Load audio
   
    start_time = time.time()  # Track playback start time
    
    # Synchronize text
    for segment in transcription:
        # Calculate when to display the text
        while time.time() - start_time < segment["start"]:
            time.sleep(0.1)  # Wait for the right time
        st.markdown(f"### {segment['text']}")

        # Streamlit interface
st.title("Audio Transcription Sync")

if st.button("Play Audio"):
    play_audio_with_sync(transcription_data)