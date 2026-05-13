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




PROMPT_SUMMARY_CONTENTS = "In the summary, list the main topics discussed, the main arguments, and any significant opinions."

PROMPT_TEMPLATE_JAPANESE = "Please summarise this transcript of a Japanese Podcast,  in N3 Japanese" + PROMPT_SUMMARY_CONTENTS

PROMPT_TEMPLATE_ENGLISH = "Please summarise this transcript of a Japanese Podcast, in English." + PROMPT_SUMMARY_CONTENTS

PROMPT_TEMPLATE_VOCABULARY = """Please give a list of any advanced Japanese vocabulary that was used in the podcast, 
along with the kana and a simple explanation of each term in Japanese. 
Exclude loan words and common words, and focus on more advanced vocabulary that might be useful for 
someone studying Japanese at an intermediate level."""

PROMPT_TEMPLATE_IDIOMS = """Please give a list of any interesting cultural references or idiomatic expressions 
that were mentioned in the podcast, along with explanations in Japanese."""

PROMPT_EPILOGUE = """All output must be in vanilla markdown. 

TRANSCRIPT:
{transcript}"""

prompts = {
    "japanese": PROMPT_TEMPLATE_JAPANESE,
    "english": PROMPT_TEMPLATE_ENGLISH,
    "vocabulary": PROMPT_TEMPLATE_VOCABULARY,
    "idioms": PROMPT_TEMPLATE_IDIOMS
}

def summarise(transcript: str, model: str, ctx_size: int, host: str, section: str) -> str:

    OLLAMA_URL = f"http://{host}:11434/api/generate"

    prompt = prompts.get(section, PROMPT_TEMPLATE_JAPANESE) + "\n\n" + PROMPT_EPILOGUE

    payload = json.dumps({
        "model": model,
        "prompt": prompt.format(transcript=transcript),
        "stream": False,
        "think": False,
        "options": {
            "num_ctx": ctx_size,
            "temperature": 0,
        }
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            return result["response"].strip()
    except urllib.error.URLError:
        sys.exit("Error: Could not connect to Ollama. Is it running? Try: ollama serve")
    except KeyError:
        sys.exit("Error: Unexpected response from Ollama.")


def main():
    parser = argparse.ArgumentParser(description="Summarise a transcript using a local Ollama model.")
    parser.add_argument("transcript", help="Path to the transcript file")
    parser.add_argument("--model", default="qwen3.5:9b", help="Ollama model to use (default: qwen3.5:9b)")
    parser.add_argument("--ctx", type=int, default=32768, help="Context window size (default: 32768)")
    parser.add_argument("--save", action="store_true", help="Save the summary to a .summary file")
    parser.add_argument("--host", default="localhost", help="Host for the Ollama API (default: localhost)")
    parser.add_argument("--section", choices=["japanese", "english", "vocabulary", "idioms"], help="Only output a specific section of the summary")
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
        print(f"Error: Output file already exists: {output_file}. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    summary = summarise(transcript, args.model, args.ctx, args.host, args.section)


    if args.save:
        with open(output_file, "w") as f:
            f.write(summary)
    else:
        print(summary)

if __name__ == "__main__":
    main()
