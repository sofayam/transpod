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

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_TEMPLATE = """"Please summarise this transcript of a Japanese Podcast, into English. 
Include: main topics discussed, and any significant opinions. Output as vanilla markdown.

TRANSCRIPT:
{transcript}"""


def summarise(transcript: str, model: str, ctx_size: int) -> str:
    payload = json.dumps({
        "model": model,
        "prompt": PROMPT_TEMPLATE.format(transcript=transcript),
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
    summary = summarise(transcript, args.model, args.ctx)


    if args.save:
        output_file = args.transcript.replace(".txt", ".summary")
        with open(output_file, "w") as f:
            f.write(summary)
    else:
        print(summary)

if __name__ == "__main__":
    main()