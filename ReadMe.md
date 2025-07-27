# find who is using the port

❯ lsof -i :8014

# adding icons to new feeds 


use the -i argument on getpodcasts, then use shrinkicons.sh to make them smaller (Needs to be better automated)


# where to find new feeds

listennotes.com


# fugashi parser

go here
https://github.com/polm/fugashi?tab=readme-ov-file

specifically:

pip install 'fugashi[unidic-lite]'

# The full version of UniDic requires a separate download step
pip install 'fugashi[unidic]'
python -m unidic download



# stretch goals 
Record user progress
Organize into groups
Integrate teppeis own transcripts 



# New Goals

All singing all dancing podcast downloader/transcriber/player

Podcast Download features

- get latest (cron job)


Transcription features

- punctuation (paragraphs for extra credit)
- diarization (currently pointless without GPU)
- use patreon transcript when available, (and avoid repeating the same with whisper)

Playback features

- variable speed
- easy to control on phone (big buttons)
- show what has already been played
- sort by latest over all podcasts

History Database
- unplayed/finished/played till
- tags
- notes?
- 
# hugging face token
is in kypass


# Old Goal

Transcibe podcasts using python whisper api 

Play them in synch with scrolling display of transcribed text reusing javascript "player" code

Web based

Whisper


# Run

## transcribe

> source setupconda.sh

> source activate transpod

> python transcribe <mp3file>



## sync transcriptions

use script rsyncontent* to rsync to rpm17/hako rather than clogging up git with everything. (maybe move to another directory altogether)

some fuss involved in asking extra permissions to rsync the stuff over there in the first place

## run podserver

node podserver.cjs



# Installation

## Python
Needs 3.12 because whisper wont work with 3.13 (12/2024). Use anaconda to manage python version and libraries

### conda setup

> brew install conda

problems with init solved by sourcing setupconda.sh (stolen from .bash_profile)

> source ./setupconda.sh

create env 

> conda create --name transpod python=3.12
> conda env list
> source activate transpod # How the f*ck does this work?

### install packages

> pip install ffmpeg
> pip install -U openai-whisper




# Links

## Magic incantation source

https://medium.com/@kharatmoljagdish/using-openai-whisper-python-library-for-speech-to-text-dda4f558fccc

import whisper
model = whisper.load_model("base")
result = model.transcribe("test.mp3")
print(f' The text in video: \n {result["text"]}')

