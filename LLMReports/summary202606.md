# Transpod

Transpod is a personal podcast management system for language learners — primarily focused on **Japanese** — that downloads, transcribes, and serves podcasts through a **Progressive Web App** with synchronized, scrolling transcripts, dictionary lookup, and LLM-generated summaries.

## Architecture

The system works in two tiers:

1. **Apple Silicon Mac Mini** — does the heavy lifting: RSS-based podcast downloading via `getpodcasts.py`, GPU-accelerated transcription with **MLX Whisper**, and LLM summarization via **Ollama**. An orchestrator (`getnewserver.cjs`) exposes a control API and runs nightly via cron.

2. **Docker VM** — runs the production web server (`podserver.cjs`, a ~1700-line Express.js app) serving the PWA, transcripts, search, stats, and audio. Content is synced from the Mac Mini via `rsync`.

## Tech Stack

| Component | Technology |
|---|---|
| Web server | Node.js + Express 4 |
| Templates | Handlebars (no JS framework — pure SSR) |
| Audio | HTML5 `<audio>` + Media Session API (lockscreen controls) |
| Transcription | MLX Whisper (Apple Silicon GPU) / YAP (fallback) |
| Summarization | Ollama (`qwen3.5:9b`) |
| Tokenization | SudachiPy (Japanese), regex (others) |
| Databases | SQLite (listening time, lookups, request stats, search index) |
| RSS | `feedparser` (Python) |
| Deployment | Docker (Alpine Node image) + rsync |

## Key Features

- **Automated podcast downloading** — RSS polling with HTTP conditional caching, cron-driven nightly runs
- **GPU-accelerated transcription** — MLX Whisper on Apple Silicon, multi-language support
- **Synchronized transcript player** — time-aligned, scrolling, clickable transcript that seeks audio
- **Word-level dictionary lookup** — click any word, opens a language-appropriate dictionary; lookups are logged
- **LLM summaries in 6 formats** — Japanese (N3 and simple), English, vocabulary, idioms, cultural references
- **Full-text search** — SQLite-powered concordance index across all episodes with SudachiPy tokenization
- **Static concordance HTML pages** — per-podcast word frequency lists linked back to the player
- **Listening stats & charts** — daily time tracking, HTTP request analytics with drilldown
- **Multi-language** — handles Japanese, Arabic, Spanish, Swedish, Russian, Italian, English, French, Korean, Portuguese, German, Chinese
- **PWA with no build step** — server-rendered HTML + vanilla JS, `manifest.json` for standalone mobile mode

## Deployment

- The Docker server runs on a Proxmox VM, serving on port 8014
- Content syncs from the Mac Mini via rsync scripts
- Per-podcast config: JSON-in-markdown `_config.md` files (feed URL, language, live flag)
- Server-wide config: `transpod.config.json` (ports, IPs, model names)

The project is a personal tool — single-file backend, build-less frontend, plenty of ops shell scripts — that packs a surprising amount of functionality for language learners working with spoken content.
