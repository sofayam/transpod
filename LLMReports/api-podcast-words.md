# API: `GET /api/wiki/podcast-words`

Returns all wiki word entries that contain lookup context records for a given podcast and episode, enriched with JMdict dictionary data. Multiple lookups for the same word are returned individually — this indicates a difficult word.

## Request

```
GET /api/wiki/podcast-words?podcast={name}&episode={path}
```

### Query parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `podcast` | Yes | Podcast name (e.g. `nihongocontepodo`) |
| `episode` | Yes | Episode path (e.g. `/ep123.mp3`) |

## Response

**200 OK**

```json
{
  "podcast": "nihongocontepodo",
  "episode": "/ep123.mp3",
  "words": [
    {
      "slug": "食べる",
      "seq": 1358280,
      "word": "食べる",
      "reading": "たべる",
      "meanings": ["to eat", "to live on (e.g. a salary)"],
      "lookups": [
        {
          "timestamp": "2026-03-10T14:23:00.000Z",
          "podcastTimestamp": "204"
        }
      ]
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `slug` | string | Wiki page identifier |
| `seq` | integer | JMdict sequence number |
| `word` | string | Primary kanji form from JMdict (`keb`), falls back to slug if no kanji |
| `reading` | string | Primary kana reading from JMdict (`reb`) |
| `meanings` | string[] | All English glosses across all senses, flattened |
| `lookups` | object[] | One entry per context record matching the podcast+episode |

#### `lookups[]`

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 datetime when the user looked up the word |
| `podcastTimestamp` | string | Playback position in seconds when the word was tapped |

## Errors

| Status | Body | Cause |
|--------|------|-------|
| 400 | `{ "error": "Query parameter \"podcast\" is required" }` | Missing `podcast` param |
| 400 | `{ "error": "Query parameter \"episode\" is required" }` | Missing `episode` param |
| 500 | `{ "error": "Failed to get podcast words" }` | Internal DB error |

## Examples

```bash
# Get all words looked up in episode 123 of nihongocontepodo
curl 'http://localhost:8000/api/wiki/podcast-words?podcast=nihongocontepodo&episode=/ep123.mp3'

# Same, with URL encoding for the episode path
curl 'http://localhost:8000/api/wiki/podcast-words?podcast=nihongocontepodo&episode=%2Fep123.mp3'
```

## Implementation

- **`wiki.js`** — `getPodcastWords(podcast, episode, jdictDb)`: queries `wiki_words` using SQLite `json_each()`/`json_extract()` to filter contexts by `$.podcast` and `$.episode`, then batch-enriches matching entries from `jdict.db`.
- **`index.js`** — `GET /api/wiki/podcast-words`: validates params, calls `wiki.getPodcastWords()`.
