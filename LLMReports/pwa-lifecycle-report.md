# PWA Lifecycle & Zombie Interval Fix

## Problem

On iOS, swiping a PWA away from the app switcher does not reliably terminate the JavaScript context. Two `setInterval` timers — `saveMeta()` (15s) and `addListeningTime()` (10s) — continued making `fetch()` calls to the server indefinitely, creating "zombie" requests that only stopped when the user cleared Safari data.

The original `window.onbeforeunload` hook was unreliable on iOS and often didn't fire at all.

## Fix

Replaced the fire-and-forget pattern with lifecycle-aware interval management:

1. **Track interval IDs** — Both `setInterval` return values stored in variables (`saveMetaTimer`, `listenTimeTimer`).

2. **`clearAllIntervals()` / `restartAllIntervals()`** — Clean start/stop helpers that destroy and recreate both timers.

3. **Audio event-driven lifecycle** — Intervals stop when audio pauses/ends and restart when audio plays:
   - `pause` → `clearAllIntervals()`
   - `ended` → `clearAllIntervals()`
   - `play` → `restartAllIntervals()`

4. **`pagehide` + `sendBeacon`** — Replaced `onbeforeunload` with `pagehide` + `navigator.sendBeacon()` for a reliable final metadata save during page teardown (no blocking `fetch` needed).

## File Changed

### `views/playtranspwa.hbs`

- `playtranspwa.hbs:705` — Both `setInterval` calls assigned to tracked variables.
- `playtranspwa.hbs:716` — `clearAllIntervals()` / `restartAllIntervals()` helpers.
- `playtranspwa.hbs:528` — `pause` listener: clears intervals.
- `playtranspwa.hbs:536` — `ended` listener: clears intervals.
- `playtranspwa.hbs:541` — `play` listener: restarts intervals.
- `playtranspwa.hbs:735` — `pagehide` listener: `sendBeacon` for final save, clears intervals.

## Scenario Matrix

| Scenario | Outcome |
|---|---|
| Walking with headphones, phone locked, audio playing | Intervals keep running — time tracks correctly |
| Switching to another app, audio still playing | Intervals keep running — no data gap |
| Quick interruption (Bluetooth dropout, phone call) | `pause` → clear, `play` → restart — intervals recreated on resume |
| Podcast finishes in pocket | `ended` → intervals stop — no zombie requests |
| User pauses manually, locks phone | `pause` → intervals stop |
| App swiped away in app switcher | `pause` fires (iOS pauses audio) → intervals stop; `pagehide` fires `sendBeacon` for final metadata write |
| App swiped away while already paused | `pagehide` fires `sendBeacon`; intervals already cleared from prior `pause` |

## Things to Note

- The `saveMeta()` interval guard (`if (!audio.paused)`) was retained as a safety net.
- `addListeningTime()` calls `/update-time` with a fixed `seconds` parameter per call — there is no catch-up logic for missed intervals during a pause/resume cycle. If precise per-second tracking is needed, the server could instead be sent the audio element's `currentTime` delta, but the current approach is adequate for daily listening totals.
