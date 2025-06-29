import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import mlx_whisper
import json
import os
import re
import config
import os.path
import argparse


def transcribe(infile: str, lang: str):

    outfile = infile

    if infile[-4:] != ".mp3":
        infile += ".mp3"

    if outfile[-4:] == ".mp3":
        outfile = outfile[:-4]

    if outfile[:-5] != ".json":
        outfile += ".json"

    optionsmlx = {
            "language": "ja",
            "path_or_hf_repo": "mlx-community/whisper-large-v3-mlx",
            "initial_prompt": "。、？！",
    } 

    if lang != "ja":
        optionsmlx["language"] = lang
        optionsmlx["initial_prompt"] = ".,?!"

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
                if index <= maxtrans: # type: ignore
                    print("found a patreon transcript for ", infile)
                    exit()

    # otherwise transcribe

    print (f" Whisper transcribing {infile} to {outfile}")

    result = mlx_whisper.transcribe(infile, **optionsmlx) # type: ignore

    segs = result["segments"] # type: ignore
    text = result["text"] # type: ignore
    stripped = []

    for seg in segs: # type: ignore
        stripped.append({"start": seg["start"], "end": seg["end"], "text": seg["text"]}) # type: ignore



    f = open(outfile, "w", encoding="utf8")

    json.dump(stripped, f, ensure_ascii=False, indent=4)

    f = open(outfile + ".txt", "w", encoding="utf8")

    # json.dump(result, f, ensure_ascii=False, indent=4)

    f.write(text) # type: ignore


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an mp3 file to JSON and TXT using mlx_whisper.")
    parser.add_argument("mp3file", help="The mp3 file to transcribe (with or without .mp3 extension)")
    parser.add_argument("--lang", default="ja", help="Language code (default: ja)")
    args = parser.parse_args()

    infile = args.mp3file
    lang = args.lang

    transcribe(infile, lang)