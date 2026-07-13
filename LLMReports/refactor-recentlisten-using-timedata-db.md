# Refactor `/recentListen` to use TIMEDATA.db

## Current problem

`listenData()` (called by `/recentListen`) reads **every `.meta` and `.info` file** across all podcast directories — O(n) filesystem operations on every request. Most of that data is discarded: the handler filters to episodes with `timeLastOpened !== 0`, sorts by recency, and keeps only the top 100.

## Plan

### 1. Add a `listened_at` column to `podcast_time`

The existing table has `date` (YYYY-MM-DD), but `timeLastOpened` is a full ISO timestamp. Add a column to preserve that precision:

```sql
ALTER TABLE podcast_time ADD COLUMN listened_at TEXT;
```

The desired end state for the table:

| date | podcast_name | episode_name | total_seconds | language | listened_at |
|---|---|---|---|---|---|
| 2026-06-28 | nihongo_con | ep42 | 1800 | ja | 2026-06-28T12:34:56Z |

### 2. Populate `listened_at` in `/update-time`

The beacon from the player already calls `GET /update-time` with `date`, `podcastName`, `episodeName`, `seconds`, `language`. Add `listenedAt` as another query param. The upsert logic becomes:

```sql
INSERT INTO podcast_time (date, podcast_name, episode_name, total_seconds, language, listened_at)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(date, podcast_name, episode_name) DO UPDATE SET
    total_seconds = total_seconds + excluded.total_seconds,
    listened_at = excluded.listened_at;
```

This mirrors the current `.meta` file behaviour: `timeLastOpened` always reflects the most recent open.

### 3. Rewrite `listenData()` / `/recentListen` to query the DB

Replace the filesystem crawl with a single SQL query:

```sql
SELECT podcast_name, episode_name,
       MAX(listened_at) AS last_listened_at,
       SUM(total_seconds) AS total_seconds_listened
FROM podcast_time
WHERE listened_at IS NOT NULL
GROUP BY podcast_name, episode_name
ORDER BY last_listened_at DESC
LIMIT 100;
```

This returns exactly the 100 most-recently-listened episodes without touching `.meta` or `.info` files at all.

### 4. Lazy-load episode metadata (optional)

If the template needs `finished` status or `itunes_duration`, read `.meta`/`.info` only for the 100 returned rows (max 100 file reads instead of thousands). Or go further:

### 5. Fold `finished` into the database

Add a `finished` INTEGER column (default 0) to `podcast_time`, or create a separate `episode_state` table:

```sql
CREATE TABLE IF NOT EXISTS episode_state (
    podcast_name TEXT NOT NULL,
    episode_name TEXT NOT NULL,
    finished INTEGER NOT NULL DEFAULT 0,
    time_in_pod REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (podcast_name, episode_name)
);
```

Write to it from `/update-meta-ep` and `/toggle-finished`. This eliminates `.meta` file reads entirely for `/recentListen`.

### 6. Compute `totalTime` from actual listening seconds

Currently the handler sums `itunes_duration` of finished episodes. With the DB, use actual accumulated seconds:

```sql
SELECT SUM(total_seconds) AS total_listened FROM podcast_time;
```

This is more accurate (measures what was actually played, not episode length).

## Result

| Before | After |
|---|---|
| Reads **all** `.meta` + `.info` files across every podcast | One SQL query → 100 rows |
| Numbers of file reads = total episodes in all podcasts | File reads: 0 (or at most 100 for optional metadata) |
| `totalTime` uses `itunes_duration` (episode length) | `totalTime` uses actual listening seconds |
| All state in files, no schema change needed | One `ALTER TABLE` migration |

The `/play` endpoint would still need `.meta` files for `timeInPod` (resume position) unless that is also migrated, but that's a separate concern.
