#!/usr/bin/env python3
"""
summarise.py - Summarise a transcript using a local Ollama model.

Usage:
    python3 summarise.py transcript.txt
    python3 summarise.py transcript.txt --model llama3.1:8b
    python3 summarise.py transcript.txt --model llama3.2 --ctx 32768
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import os




PROMPT_SUMMARY_CONTENTS = "In the summary, list the main topics discussed and any significant opinions."

PROMPT_TEMPLATE_SIMPLE = """以下のトランスクリプトをNHKウェブやさしいニュースのスタイルで要約してください。

条件：
・短い文を使ってください
・難しい漢字にはふりがなをつけてください（例：食べる（たべる））
・敬語や難しい表現は使わないでください
・中学生にわかるような言葉を使ってください
・200文字から500文字でまとめてください

マークダウン形式で書いてください。

"""

PROMPT_TEMPLATE_JAPANESE = "Please summarise this transcript of a Japanese Podcast,  in N3 Japanese" + PROMPT_SUMMARY_CONTENTS

PROMPT_TEMPLATE_ENGLISH = "Please summarise this transcript of a Japanese Podcast, in English." + PROMPT_SUMMARY_CONTENTS

PROMPT_TEMPLATE_VOCABULARY = """Please give a list of a maximum of 20 Japanese words that were used in the podcast, and
are worth noting for an intermediate Japanese learner, along with their English translation and explanations. 
Please include the kana pronunciation. Do not include loan words or カタカナ日本語, and focus on native Japanese vocabulary that is relevant for 
someone studying Japanese at an intermediate level.
Output only the final markdown table. Do not output any intermediate results or drafts.
"""

PROMPT_TEMPLATE_IDIOMS = """Please give a list of any idiomatic expressions 
that were mentioned in this podcast transcript, along with explanations first in Japanese and then in English."""

PROMPT_TEMPLATE_CULTURE = """Please give a list of at most 10 main cultural references 
that were mentioned in this podcast transcript, along with explanations first in Japanese and then in English."""

PROMPT_EPILOGUE = """All output must be in vanilla markdown. Feel free to use tables where appropriate. """

prompts = {
    "japanese": PROMPT_TEMPLATE_JAPANESE,
    "english": PROMPT_TEMPLATE_ENGLISH,
    "vocabulary": PROMPT_TEMPLATE_VOCABULARY,
    "idioms": PROMPT_TEMPLATE_IDIOMS,
    "culture": PROMPT_TEMPLATE_CULTURE,
    "simple": PROMPT_TEMPLATE_SIMPLE,
}

def summarise(transcript: str, model: str, ctx_size: int, host: str, section: str) -> str:

    OLLAMA_URL = f"http://{host}:11434/api/chat"

    prompt = prompts.get(section, PROMPT_TEMPLATE_JAPANESE) + "\n\n" + PROMPT_EPILOGUE

    payload = json.dumps({
        "model": model,

        "stream": False,
        "think": False,
        "messages": [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": transcript
        }
    ],
        "options": {
            "num_ctx": ctx_size,
            "temperature": 0.3,
            "repeat_penalty": 1.2,
            "repeat_last_n": 128,
        }
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
      
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=180,) as response:
            result = json.load(response)

            return result["message"]["content"].strip()
    except urllib.error.URLError:
        sys.exit("Error: Could not connect to Ollama. Is it running? Try: ollama serve")
    except KeyError:
        sys.exit("Error: Unexpected response from Ollama.")
    except TimeoutError:
        sys.exit("Error: ****************** Request to Ollama timed out.")


def main():
    parser = argparse.ArgumentParser(description="Summarise a transcript using a local Ollama model.")
    parser.add_argument("transcript", help="Path to the transcript file")
    parser.add_argument("--model", default="qwen3.5:9b", help="Ollama model to use (default: qwen3.5:9b)")
    parser.add_argument("--ctx", type=int, default=32768, help="Context window size (default: 32768)")
    parser.add_argument("--save", action="store_true", help="Save the summary to a .summary file")
    parser.add_argument("--host", default="localhost", help="Host for the Ollama API (default: localhost)")
    parser.add_argument("--section", choices=["japanese", "english", "vocabulary", "idioms", "culture", "simple"], help="Only output a specific section of the summary")
    parser.add_argument("--dryrun", action="store_true", help="just print some diagnostics")
    parser.add_argument("--force", action="store_true", help="force action even if file already exists")
    args = parser.parse_args()
  


    try:
        with open(args.transcript, "r") as f:
            transcript = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: File not found: {args.transcript}")

    word_count = len(transcript.split())
    estimated_tokens = int(word_count / 0.75)
    if estimated_tokens > args.ctx:
        print(f"Warning: Transcript is ~{estimated_tokens} tokens, which exceeds --ctx {args.ctx}.", file=sys.stderr)
        print(f"Consider using --ctx {estimated_tokens + 1000} or a model with a larger context window.\n", file=sys.stderr)

    print(f"Summarising with {args.model} (ctx: {args.ctx})...\n", file=sys.stderr)
    output_file = args.transcript.replace(".txt", ".summary." + args.section)

    if (not args.force) and args.save and os.path.exists(output_file):
        print(f"Info: Output file already exists: {output_file}.", file=sys.stderr)
        sys.exit(1)

    summary = summarise(transcript, args.model, args.ctx, args.host, args.section)


    if args.save:
        with open(output_file, "w") as f:
            f.write(summary)
    else:
        print(summary)

if __name__ == "__main__":
    main()
