
import whisper
import json
import sys

# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)

# Arguments passed
print("\nName of Python script:", sys.argv[0])

print("\nArguments passed:", end = " ")
for i in range(1, n):
    print(sys.argv[i], end = " ")
print(" ")

if n == 1:
    print (sys.argv[0], "Usage: ")
    print ("<name(.mp3)> -> transcribes name.mp3 to name.json")
    print ("<infile(.mp3) outfile(.json)> -> transcribes infile.mp3 to outfile.json")

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

f = open(outfile, "w", encoding="utf8")

json.dump(result, f, ensure_ascii=False)

