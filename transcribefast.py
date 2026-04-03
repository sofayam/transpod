import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


import json
import os
import re
import config
import os.path
import argparse
import datetime

with open(os.path.join(os.path.dirname(__file__), 'transpod.config.json')) as f:
    appConfig = json.load(f)

def isYapLocale(locale: str) -> bool:
    return locale in appConfig["YAP_LOCALES"]


def transcribe(infile: str, lang: str, locale: str):
    
    outfile = infile

    if infile[-4:] != ".mp3":
        infile += ".mp3"

    if outfile[-4:] == ".mp3":
        outfile = outfile[:-4]

    if outfile[:-5] != ".json":
        outfile += ".json"

    # make choice of transcriber based on locale. If locale is in YAP_LOCALES, use YAP, otherwise use Whisper. 
    
    transcriber = "YAP" if isYapLocale(locale) else "WHS"
    flagfile = outfile + "." + transcriber

    # check for existence of flag file and exit if found
    if os.path.exists(flagfile):
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
    stripped = []
    text = ""

    # make choice of transcriber based on locale. If locale is in YAP_LOCALES, use YAP, otherwise use Whisper. 
    
    transcriber = "YAP" if isYapLocale(locale) else "WHS"
    flagfile = outfile + "." + transcriber

    if transcriber == "YAP":

        print (f" YAP transcribing {infile} to {outfile}")
    
        import subprocess
        result = subprocess.run(["yap", infile, "--json", f"--locale={locale}"], capture_output=True, 
                                text=True)
        
        result = json.loads(result.stdout)

        segs = result["segments"] # type: ignore

        for seg in segs: # type: ignore
            stripped.append({"start": seg["start"], "end": seg["end"], "text": seg["text"]}) # type: ignore
            text += seg["text"] # type: ignore  

    else:
        # give preexisting WHS transcripts a flag file if they dont have one, and then exit. 
        

        if os.path.exists(outfile):
            print("transcript already exists for", infile)
            if not os.path.exists(flagfile):
                f = open(flagfile, "w", encoding="utf8")
                dateandtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(dateandtime + " " + transcriber + "\n")
                f.close()
                print("created flag file: ", flagfile)
            exit()
        
        import mlx_whisper
        optionsmlx = {
            "language": lang,
            "path_or_hf_repo": appConfig["WHISPER_MODEL"],
            "initial_prompt": ".,?!",
        } 
        print (f" Whisper transcribing {infile} to {outfile}")

        result = mlx_whisper.transcribe(infile, **optionsmlx) # type: ignore

        segs = result["segments"] # type: ignore
        text = result["text"] # type: ignore

        for seg in segs: # type: ignore
            stripped.append({"start": seg["start"], "end": seg["end"], "text": seg["text"]}) # type: ignore



    f = open(outfile, "w", encoding="utf8")

    json.dump(stripped, f, ensure_ascii=False, indent=4)

    f = open(outfile + ".txt", "w", encoding="utf8")

    # json.dump(result, f, ensure_ascii=False, indent=4)

    f.write(text) # type: ignore

    f = open(flagfile, "w", encoding="utf8")
    dateandtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(dateandtime + " " + transcriber + "\n")
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an mp3 file to JSON and TXT using mlx_whisper.")
    parser.add_argument("mp3file", help="The mp3 file to transcribe (with or without .mp3 extension)")
    parser.add_argument("--lang", default="ja", help="Language code (default: ja)")
    parser.add_argument("--locale", default="ja_JP", help="Locale code for YAP (default: ja_JP)")

    args = parser.parse_args()

    infile = args.mp3file
    lang = args.lang
    locale = args.locale


    transcribe(infile, lang, locale)
