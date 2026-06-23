# Request Statistics Feature

## Overview

A `/stats` page showing request counts as a **bar chart** with switchable resolution (last N minutes/hours/days/months). Users can click a bar to drill down into the most popular URLs for that time window. Uses a separate SQLite database (`REQUESTS.db`) for storage, keeping it independent from the existing `TIMEDATA.db`, `WORDS.db`, and `concordance.db`.

## Files Changed

### `podserver.cjs`

- **DB init** (line 1244): Opens `content/REQUESTS.db`, creates `request_log` table with columns: `id`, `method`, `path`, `status`, `timestamp` (ISO 8601 text), `duration_ms`.
- **Data retention** (line 1266): Deletes rows older than 90 days on startup.
- **Middleware** (line 64): Logs every request after it finishes — method, path, status code, timestamp, duration in ms. Uses a `Set` (`skippedPaths`) to skip `/stats`, `/css/stats.css`, and `/stats/drilldown` and avoid self-tracking.
- **Route** `GET /stats` (line 1275): Accepts `?resolution=minutes|hours|days|months&count=N` (defaults: hours/24, max 200). Uses a single SQL query with `SUBSTR`-based bucketing, gap-fills empty buckets, computes avg duration per bucket. Injects JSON data into the template for client-side chart rendering.
- **Route** `GET /stats/drilldown` (line 1378): Accepts `?since=ISO&until=ISO`. Returns top 20 paths as JSON with method, count, 2xx/4xx/5xx breakdown, and avg duration.

### `views/stats.hbs`

Handlebars template (no layout). Renders:
- Resolution selector buttons (Minutes/Hours/Days/Months)
- Count dropdown (populated dynamically per resolution — e.g., hours shows 6/12/24/48)
- Auto-refresh checkbox (polls every 15s)
- Summary stats bar (total requests + avg duration)
- Chart.js bar chart with click-to-drill-down
- Drill-down panel showing top URLs in a table with status color-coding

### `public/css/stats.css`

Complete stylesheet: controls bar, pill-style resolution buttons, summary stat cards, 400px chart container, drill-down panel with table styling, status colors (green/amber/red for 2xx/4xx/5xx), hidden utility class.

### `views/podcasts.hbs`

Added a **Stats** link next to the existing **Chart** link on the home page (line 63).

## Schema

```sql
CREATE TABLE request_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    duration_ms INTEGER NOT NULL DEFAULT 0
);
```

## API

### `GET /stats`

| Param | Default | Description |
|-------|---------|-------------|
| `resolution` | `hours` | One of: `minutes`, `hours`, `days`, `months` |
| `count` | 30/24/30/12 (per resolution) | Number of buckets to show (capped at 200) |

Renders HTML page with embedded JSON.

### `GET /stats/drilldown`

| Param | Required | Description |
|-------|----------|-------------|
| `since` | yes | ISO timestamp — start of the window |
| `until` | yes | ISO timestamp — end of the window |

Returns JSON array of `{ path, method, count, status2xx, status4xx, status5xx, avg_duration }`.

## Resolution Details

| Resolution | Bucket size | Count defaults | Label format |
|------------|-------------|----------------|--------------|
| minutes | 1 minute | 15, 30, 60 | `10:30` |
| hours | 1 hour | 6, 12, 24, 48 | `06-23 10:00` |
| days | 1 day | 7, 14, 30 | `2026-06-23` |
| months | 1 calendar month | 3, 6, 12 | `2026-06` |

Buckets are aligned to UTC boundaries. Gaps (buckets with zero requests) are filled by the server — every response has exactly `count` entries.

## Things Still To Refine

### Data
- Path filtering could exclude static asset noise (`.css`, `.js`, `.mp3`, images) to focus on API/page routes.
- Could add breakdown by status code directly on the chart (stacked bars).
- The drill-down is scoped to paths — could also group by status code or method.

### Query
- Timestamps are ISO text, not INTEGER (Unix epoch ms). Works for `SUBSTR`-based bucketing but doesn't benefit from an index. If the table grows large despite the 90-day purge, consider switching types.
- The single SQL query is efficient but uses `SUBSTR` on every row — no index can help the GROUP BY.

### UI
- No link from the Stats page to the Chart page (or vice versa).
- Drill-down panel doesn't auto-refresh; user must close and re-click.
- No date range picker (the resolution/count selectors are the only navigation).
- The resolution buttons always reset to the first count option — switching from hours/24 to days doesn't preserve 24.

### Middleware
- Logs ALL requests except the stats pages. Could add whitelisting or sampling for high-traffic deployments.
- Could exclude common bot/crawler user-agents.

### Error handling
- DB write failures in the middleware are logged but the request succeeds silently. Could surface via a health-check metric.
- Drill-down endpoint returns a 500 with a JSON error object if the query fails.

### Data retention
- 90-day purge runs once at startup. For long-running servers, consider a periodic timer or a cron job.
