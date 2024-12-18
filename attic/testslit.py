import streamlit as st
import time
from pydub import AudioSegment
from pydub.playback import play
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

def play_audio_with_sync(audio_path, transcription):
    # Load audio
    audio = AudioSegment.from_mp3(audio_path)
    start_time = time.time()  # Track playback start time
    
    # Play audio in a separate thread
    st.audio(audio_path, format='audio/mp3', autoplay=True)
    
    # Synchronize text
    for segment in transcription:
        # Calculate when to display the text
        while time.time() - start_time < segment["start"]:
            time.sleep(0.1)  # Wait for the right time
        st.markdown(f"### {segment['text']}")

        # Streamlit interface
st.title("Audio Transcription Sync")

if st.button("Play Audio"):
    play_audio_with_sync(audio_file_path, transcription_data)