
# Goal

Transcibe podcasts using python whisper api 

Play them in synch with scrolling display of transcribed text reusing javascript "player" code

Web based

Whisper

# Installation

## Python
Needs 3.12 because whisper wont work with 3.13 (12/2024). Use anaconda to manage python version and libraries

### conda setup

> brew install conda

problems with init solved by sourcing setupconda.sh (stolen from .bash_profile)

> source ./setupconda.sh

create env 

just use base env

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

