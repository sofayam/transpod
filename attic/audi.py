from streamlit_advanced_audio import audix # type: ignore
import streamlit as st

# Basic playback
# audix("path/to/your/audio.wav")

# With custom styling
from streamlit_advanced_audio import WaveSurferOptions

options = WaveSurferOptions(
    wave_color="#2B88D9",
    progress_color="#b91d47",
    height=100
)

result = audix("Teppei1286.mp3", wavesurfer_options=options)

# Track playback status
if result:
    st.write(f"Current Time: {result['currentTime']}s") # type: ignore
    if result['selectedRegion']:
        st.write(f"Selected Region: {result['selectedRegion']['start']} - {result['selectedRegion']['end']}s") # type: ignore