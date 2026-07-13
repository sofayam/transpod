# Episode Notes Feature Report

**Date:** Sunday, July 13, 2026
**Subject:** Implementation of per-episode notes with frontmatter tags, tag autocomplete, and listening history summary

---

## 1. Feature: Episode Notes

### Objective
Add a notes system at the episode level, accessible and editable from the podcast player, stored as `.note` files with YAML frontmatter for tags. Tags are displayed symbolically in the podcast and episode listings. A listening history summary is shown alongside notes.

### Implementation Details

**Storage format:** `content/<pod>/<episode>.note`

```
---
tags:
  - beginner
  - grammar
---

Freeform markdown notes here...
```

The `.note` suffix was chosen deliberately to avoid collision with `_config.md` (podcast config) and other `.md` files in the content directory.

---

## 2. Backend Changes (`podserver.cjs`)

### Helper Functions

- **`parseNotes(raw)`** — Parses a raw notes string into `{ tags: [...], body: "..." }`. Handles frontmatter via regex extraction. Falls back gracefully if no frontmatter exists.
- **`readNotes(podName, episodeName)`** — Reads `content/<pod>/<ep>.note`, returns parsed tags and body. Returns `{ tags: [], body: "" }` if file doesn't exist.
- **`writeNotes(podName, episodeName, rawContent)`** — Writes raw content (including frontmatter) to the notes file.
- **`getAllTagsForPod(podName)`** — Scans all `.note` files in a podcast directory, aggregates unique tags across all episodes. Used for the podcast listing badges.

### API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/notes/:pod/:ep` | Returns `{ success, tags, body }` for an episode's notes |
| `POST` | `/notes/:pod/:ep` | Saves notes content (raw markdown with frontmatter), returns `{ success, tags }` |
| `GET` | `/listening-stats/:pod/:ep` | Queries `TIMEDATA.db` for per-episode stats: `totalListened`, `firstListened`, `lastListened` |
| `GET` | `/tags` | Returns sorted array of all unique tags across every `.note` file in the repo |

### Modified Routes

- **`GET /`** (podcast listing) — Now calls `getAllTagsForPod()` for each podcast and passes `tags` to the template.
- **`GET /play/:pod/:ep`** (player) — Checks if a `.note` file exists for the episode, passes `hasNotes` to the template.
- **`GET /pod/:id`** (episode list) — Checks if a `.note` file exists for each episode, passes `hasNotes` per entry.

---

## 3. Frontend Changes

### Player (`views/playtranspwa.hbs`)

**Notes modal** — New modal overlay (same pattern as the existing summary modal) with:
- Listening history summary bar (total time listened, first/last listened dates)
- Read-only tag badges displayed above the notes content
- Rendered markdown notes body (uses `marked.js`, already loaded)
- Edit button to switch to editor mode
- Tag editor with input field and autocomplete dropdown
- Textarea for editing notes body
- Save/Cancel buttons

**Notes button** in the control bar:
- Shows 📝 (full opacity) when a note exists, 📄 (dimmed) when none exists
- Clicking when no note exists opens the editor directly (no empty display step)
- After first save, icon flips to 📝

**Tag autocomplete:**
- Fetches all existing tags from `GET /tags` on modal open
- Filters as user types, excludes already-applied tags
- Keyboard navigation (Arrow Up/Down, Enter to select, Escape to dismiss)
- Mouse click to select

**Tag management:**
- Existing tags shown as removable badges (click ✕ to remove)
- New tags added via input field (Enter, comma, or click suggestion)
- Tags rebuilt into frontmatter on save
- Cancel re-fetches from server to restore last saved state

### Episode List (`views/episodes.hbs`)

- Episodes with a notes file show a 📝 icon at the front of the row, before the finished/unfinished status icon

### Podcast Listing (`views/podcasts.hbs`)

- Each podcast row shows aggregated tags from all episode notes as small gray badges next to the podcast name

### CSS (`public/css/podcasts.css`)

- `.tag-badges` and `.badge` styles for the podcast listing badges

### Player CSS (inline in `playtranspwa.hbs`)

- Notes modal styles (mirrors summary modal pattern)
- Tag editor badge styles with remove button
- Autocomplete dropdown styles with active state highlighting

---

## 4. Files Changed

| File | Changes |
|------|---------|
| `podserver.cjs` | `parseNotes()`, `readNotes()`, `writeNotes()`, `getAllTagsForPod()`; `GET/POST /notes/:pod/:ep`, `GET /listening-stats/:pod/:ep`, `GET /tags`; modified `GET /`, `GET /play/:pod/:ep`, `GET /pod/:id` to pass `hasNotes`/`tags` |
| `views/playtranspwa.hbs` | Notes modal HTML, notes button in control bar, modal CSS, full JS for modal/tags/autocomplete/save |
| `views/episodes.hbs` | 📝 icon before finished/unfinished icon |
| `views/podcasts.hbs` | Tag badges after podcast name |
| `public/css/podcasts.css` | `.badge` and `.tag-badges` styles |

---

## 5. Design Decisions

- **`.note` suffix** — Avoids collision with `_config.md` (JSON-in-markdown podcast config) and transcript `.json` files.
- **Episode-level notes** — Notes are per-episode, not per-podcast. Tags roll up to the podcast listing via `getAllTagsForPod()`.
- **Frontmatter is the source of truth** — The textarea contains the full file content including frontmatter. On save, tags from the tag editor are merged with the textarea body via `buildFrontmatter()`.
- **No layout wrapper** — Matches existing pattern: all templates are standalone HTML documents with `layout: false`.
- **Cancel re-fetches** — Rather than tracking original state, cancel simply re-fetches from the server to restore the last saved state.
