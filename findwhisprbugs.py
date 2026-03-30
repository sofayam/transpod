#!/usr/bin/env python3
"""
findwhisprbugs.py — summarise Whisper hallucination/repetition bugs in transcription JSON files.

Output: one line per affected file, showing count of bad segments and the single worst one.
Files sorted worst-first within each podcast. Final section lists the top 20 across all podcasts.

Usage:
    python findwhisprbugs.py                  # scan all podcasts
    python findwhisprbugs.py teppeibegin noriko ...
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Thresholds ---
DENSITY_THRESHOLD = 9   # chars/second; normal JP speech ~5-7, bugs typically 10+
INTRA_MIN_REPS   = 8    # times a unit must repeat inside one segment
INTER_MIN_REPS   = 6    # consecutive identical segments
MIN_DURATION     = 1

CONTENT_DIR = Path(__file__).parent / "content"


@dataclass
class Incident:
    time: str
    density: float        # chars/sec (0 if inter-segment)
    rep_count: int        # max repetition count found (0 if density-only)
    rep_unit: str         # repeated unit ('' if none)
    inter: bool           # True = inter-segment run
    snippet: str          # short text preview

    @property
    def score(self) -> float:
        """Higher = worse. Heavily weight repetition count and density."""
        return max(self.density, 0) + self.rep_count * 2


@dataclass
class FileResult:
    podcast: str
    filename: str
    incidents: list[Incident] = field(default_factory=list)

    @property
    def worst(self) -> Incident:
        return max(self.incidents, key=lambda i: i.score)

    @property
    def score(self) -> float:
        return self.worst.score


def find_intra_repetitions(text: str) -> list[tuple[str, int]]:
    hits, seen = [], set()
    for unit_len in range(1, len(text) // INTRA_MIN_REPS + 1):
        pattern = rf'(.{{{unit_len}}})\1{{{INTRA_MIN_REPS - 1},}}'
        for m in re.finditer(pattern, text):
            unit = m.group(1)
            if unit in seen:
                continue
            hits.append((unit, len(m.group(0)) // unit_len))
            seen.add(unit)
    return hits


def fmt_time(seconds) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def check_file(json_path: Path, podcast: str) -> FileResult | None:
    result = FileResult(podcast=podcast, filename=json_path.name)
    try:
        segments = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(segments, list):
        return None

    # Intra-segment
    for seg in segments:
        text = seg.get("text", "").strip()
        if not text:
            continue
        start = seg.get("start", 0)
        dur   = seg.get("end", start) - start
        density = len(text) / dur if dur >= MIN_DURATION else 0
        reps = find_intra_repetitions(text)
        best_rep = max(reps, key=lambda x: x[1]) if reps else None

        if density > DENSITY_THRESHOLD or reps:
            result.incidents.append(Incident(
                time=fmt_time(start),
                density=density,
                rep_count=best_rep[1] if best_rep else 0,
                rep_unit=best_rep[0] if best_rep else "",
                inter=False,
                snippet=text[:60],
            ))

    # Inter-segment
    run_text, run_start_idx, run_start_time = None, 0, 0

    def flush(end_idx):
        nonlocal run_text, run_start_idx, run_start_time
        n = end_idx - run_start_idx
        if run_text is not None and n >= INTER_MIN_REPS:
            result.incidents.append(Incident(
                time=fmt_time(run_start_time),
                density=0,
                rep_count=n,
                rep_unit=run_text[:30],
                inter=True,
                snippet=run_text[:60],
            ))

    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()
        if text != run_text:
            flush(i)
            run_text, run_start_idx, run_start_time = text, i, seg.get("start", 0)
    flush(len(segments))

    return result if result.incidents else None


def fmt_incident(inc: Incident) -> str:
    tag = "INTER" if inc.inter else f"{inc.density:.0f}c/s"
    rep = f" ×{inc.rep_count} {repr(inc.rep_unit)}" if inc.rep_count else ""
    return f"[{inc.time}] {tag}{rep}  {repr(inc.snippet)}"


def main():
    if len(sys.argv) > 1:
        podcasts = [CONTENT_DIR / p for p in sys.argv[1:]]
    else:
        podcasts = sorted(p for p in CONTENT_DIR.iterdir() if p.is_dir())

    total_files = 0
    all_results: list[FileResult] = []

    for podcast_dir in podcasts:
        json_files = sorted(podcast_dir.glob("*.json"))
        if not json_files:
            continue
        total_files += len(json_files)

        results = [r for jf in json_files if (r := check_file(jf, podcast_dir.name))]
        if not results:
            continue

        results.sort(key=lambda r: r.score, reverse=True)
        all_results.extend(results)

        print(f"\n=== {podcast_dir.name}  ({len(results)}/{len(json_files)} files affected) ===")
        for r in results:
            w = r.worst
            n = len(r.incidents)
            segs = f"{n} seg{'s' if n > 1 else ''}"
            print(f"  {segs:8s}  {fmt_incident(w)}  …{r.filename[:50]}")

    # Top 20 worst overall
    all_results.sort(key=lambda r: r.score, reverse=True)
    top = all_results[:20]
    if top:
        print(f"\n{'='*60}")
        print(f"TOP {len(top)} WORST SEGMENTS (across all podcasts)")
        print(f"{'='*60}")
        for r in top:
            print(f"  {r.podcast}/{r.filename[:40]}")
            print(f"    {fmt_incident(r.worst)}")

    total_affected = len(all_results)
    print(f"\n--- {total_files} files scanned, {total_affected} affected ---")


if __name__ == "__main__":
    main()
