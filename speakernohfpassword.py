# After a lot of doxing myself on hugging face this will now run 
# but is pointless without a GPU

from pyannote.audio import Pipeline

# Load the pre-trained diarization pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token="XXXLookinkeypass")

# Perform diarization
audio_file = "content/teppeinoriko/#503「波！波！波！波！波！②」.mp3"
diarization_result = pipeline(audio_file)

# Print diarization results
for segment, track, speaker in diarization_result.itertracks(yield_label=True):
    print(f"{segment.start:.2f} - {segment.end:.2f}: {speaker}")