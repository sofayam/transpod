
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import mlx_whisper
import json
import sys
import os
import re
import config
import os.path

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

match = re.search(r'chunk', infile)
if match:
    print(infile, " is a chunk, will not be transcribed")

if infile[-4:] != ".mp3":
    infile += ".mp3"

if outfile[-4:] == ".mp3":
    outfile = outfile[:-4]

if outfile[:-5] != ".json":
    outfile += ".json"

optionsold = {
    "task": "transcribe",
    "language": "en",  # or other language code
    "fp16": False,
    "no_speech_threshold": 0.6,
    "word_timestamps": True,
    "initial_prompt": None,
    "suppress_tokens": [-1],  # Don't suppress any tokens
    "condition_on_previous_text": True,
    "temperature": 0,
    "best_of": 5,
    "without_timestamps": True,
    "max_initial_timestamp": 1.0,
    "patience": 1.0
}


optionsx = {
    "task": "transcribe",
    "language": "ja",  # Japanese language code
    "fp16": False,
    "no_speech_threshold": 0.6,
    "word_timestamps": True,
    "initial_prompt": "。、？！",  # Add common Japanese punctuation marks
    "suppress_tokens": [-1],  # Don't suppress any tokens
    "condition_on_previous_text": True,
    "temperature": 0,
    "best_of": 5,
    "without_timestamps": True,
    "max_initial_timestamp": 1.0,
    "patience": 1.0
}

optionsz = {
    "task": "transcribe",
    "language": "ja",  # Japanese language code
    "fp16": False,
    "no_speech_threshold": 0.6,
    "word_timestamps": True,
    "initial_prompt": "。、？！",  # Add common Japanese punctuation marks
    "suppress_tokens": [-1],  # Don't suppress any tokens
    "condition_on_previous_text": True,
    "temperature": 0,
    "best_of": 5,
    "beam_size": 5,    # Add beam_size parameter
    "patience": 1.0,   # Now patience will work with beam_size specified
    # "without_timestamps": True,
    "max_initial_timestamp": 1.0
}

options = {
    "task": "transcribe",
    "language": "ja",
    "fp16": False,      # Enable half-precision for faster processing
    "beam_size": 1,    # Reduce beam size for faster processing
    "best_of": 1,      # Reduce candidates for faster processing
    "temperature": 0,  # Keep deterministic output
    "initial_prompt": "。、？！",  # Restored Japanese punctuation marks
    "condition_on_previous_text": False,  # Disable for speed
    "word_timestamps": False  # Disable if you don't need word-level timing
}

optionsmlx = {
    "language": "ja",
#    "path_or_hf_repo": "mlx-community/whisper-medium-mlx-fp32",
    "path_or_hf_repo": "mlx-community/whisper-large-v3-mlx",
      "initial_prompt": "。、？！",

}

# check for existence of transcipt and exit if found

if os.path.exists(outfile):
    print("transcript already exists for", infile)
    exit()

# get directory of file

dirname = os.path.dirname(infile)
conf = config.getConfig(dirname)
match = re.search(r'#(\d+)', infile)
if match:
    index = int(match.group(1))
    if "lasttranscript" in conf:
        maxtrans = conf["lasttranscript"]
        if maxtrans:
            if index <= maxtrans:
                print("found a patreon transcript for ", infile)
                exit()

# otherwise transcribe

print (f" Whisper transcribing {infile} to {outfile}")

result = mlx_whisper.transcribe(infile, **optionsmlx)

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


