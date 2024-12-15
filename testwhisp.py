
import whisper
import json

model = whisper.load_model("base")


result = model.transcribe("Teppei1286.mp3", word_timestamps=False)

# result = model.transcribe("Teppei1286.mp3", word_timestamps=True)

f = open("teppei.json", "w", encoding="utf8")

json.dump(result, f,ensure_ascii=False)

