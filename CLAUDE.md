# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Transpod is a podcast downloader, transcriber, and web player. It downloads podcasts via RSS, transcribes them using MLX Whisper (Apple Silicon optimized), and serves a web UI with synchronized scrolling transcription, word search, and concordance features. Primarily targets Japanese-language content but supports Spanish, Swedish, Russian, Italian, and English.

## Running the Server

```bash
node podserver.cjs          # Default port 8014
node podserver.cjs 8080     # Custom port
npm start                   # Same as above
```

## Python Toolchain

Requires a conda environment named `transpod`:

```bash
source setupconda.sh
conda activate transpod

python getpodcasts.py content/<podcast_name> [-l] [-t] [-s]   # Download/update a podcast
python transcribefast.py <mp3_file> <language>                  # Transcribe audio
python indexer.py                                               # Rebuild word search index
python create_concordance.py <podcast_name> <num_occurrences> <lang>
```

`nightly.sh` runs `getpodcasts.py` for all configured podcasts via cron.

## Deployment Architecture

Three machines are involved:

- **`mini`** (192.168.68.101) — Apple Silicon Mac. Primary dev machine. Permanently runs `getnewserver.cjs` (podcast downloading + transcription orchestration) and `transcribefast.py` (MLX Whisper) — both require the GPU and will never move to box.
- **`box`** — Proxmox VM. Production deployment target for `podserver.cjs`, the Japanese lookup/dictionary server, and the wiki. Deployed via Docker. Calls back to `mini:8015` to trigger downloads/transcription.

Deployment-specific values (ports, `MINI_IP`) live in `transpod.config.json`, which is read by both Node (`require()`) and Python (`json.load()`). Because `mini` has a stable IP, `transpod.config.json` can ship with the code unchanged — `podserver.cjs` deployed to `box` already knows where to find `mini` with no reconfiguration.

```bash
./dockerbuild.sh
./dockerrunbox.sh     # Deploy to box
```

The rsync scripts (`rsyncontentbox.sh`, etc.) are the transfer layer between the two machines — they push the downloaded MP3s and JSON transcripts produced on `mini` over to `box` where `podserver.cjs` can serve them. Hardcoded `box.local` targets in these scripts are intentional ops tooling, not application config.

## Architecture

**`podserver.cjs`** — The entire backend in one ~1400-line Express.js file (CommonJS despite `"type": "module"` in package.json). Handles all routes, database queries, file I/O, and metadata management.

**`views/`** — Handlebars templates. `playtranspwa.hbs` is the main player UI — the most complex template with audio sync, transcript highlighting, and mobile controls.

**`content/`** — All podcast data lives here. Each podcast has its own subdirectory:
- `*.mp3` — audio files
- `*.json` — transcription segments: `[{start, end, text}, ...]`
- `*.info` — episode metadata (title, published date, duration, listened ranges)
- `_config.md` — podcast config (feed URL, language, live flag, sort order) in JSON inside markdown
- `*.meta` — podcast-level metadata

`content/_global.meta` — server-wide settings (e.g., `coresetOnly`, `language`).

**`content/concordance.db`** — SQLite database for full-text word search. Tables: podcasts, episodes, segments, words. Rebuilt by `indexer.py`.

**`indexer.config.json`** — Controls which languages are indexed (`INDEXLANGUAGES`), max references per word (`REFMAX`), and repetition filtering (`REPMAX`).

## Key Design Patterns

- **Config format:** Podcast configs are JSON embedded in `.md` files — the server reads and parses the JSON block from the markdown.
- **Metadata merging:** Episode `.info` files merge with podcast `.meta` defaults at read time.
- **Language handling:** Japanese uses kuromoji.js (Node) and sudachipy (Python) for morphological tokenization. Other languages use regex word splitting.
- **Listening history:** Stored as time ranges in `.info` files, not in the database.
- **No build step:** Pure server-side rendering with Handlebars. Static assets in `public/`. No bundler or transpilation.
- **MLX Whisper:** `transcribefast.py` uses the MLX variant of Whisper for fast transcription on Apple Silicon. Output JSON segments are time-aligned to audio.
