
import whisper
import json
import sys

test=False

if test:
    infile = "content/teppei/snippet"
    outfile = infile
else:

    n = len(sys.argv)

    if n == 1:
        print (sys.argv[0], "Usage: ")
        print ("<name(.mp3)> -> transcribes name.mp3 to name.json")
        print ("<infile(.mp3) outfile(.json)> -> transcribes infile.mp3 to outfile.json")
        exit()

    infile = sys.argv[1]

    if n == 2:
        outfile = infile
    else:
        outfile = sys.argv[2]



if infile[-4:] != ".mp3":
    infile += ".mp3"

if outfile[-4:] == ".mp3":
    outfile = outfile[:-4]

if outfile[:-5] != ".json":
    outfile += ".json"



print (f" Transcribing {infile} to {outfile}")


model = whisper.load_model("base")



result = model.transcribe(infile, word_timestamps=False)

segs = result["segments"]
text = result["text"]
stripped = []

for seg in segs:
    stripped.append({"start": seg["start"], "end": seg["end"], "text": seg["text"]})



f = open(outfile, "w", encoding="utf8")

json.dump(stripped, f, ensure_ascii=False, indent=4)

f = open(outfile + ".txt", "w", encoding="utf8")

# json.dump(result, f, ensure_ascii=False, indent=4)

f.write(text)


