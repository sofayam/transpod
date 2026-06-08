# iOS Lock Screen Audio Control Report

## Summary

Lock screen audio controls are now functional for pause, seek, and skip. Resume (play) from the lock screen is partially working — the position counter advances — but audio output is silent. This is a hard iOS PWA platform limitation, not a fixable code bug.

---

## What Was Implemented

### MediaSession API (`playtranspwa.hbs`)

- Registered `play`, `pause`, `seekbackward`, `seekforward`, `seekto`, `previoustrack`, `nexttrack` action handlers wired to the `<audio>` element
- Set `MediaMetadata` (episode title, podcast name, artwork via `/geticon`) when audio loads
- Updated `navigator.mediaSession.playbackState` to `'playing'`/`'paused'`/`'none'` in audio event handlers
- Called `setPositionState()` on every `timeupdate` so the lock screen scrubber tracks position
- Registered handlers immediately at `DOMContentLoaded` — not waiting for `canplaythrough`, which on iOS never fires until after the first user tap

### Other fixes

- Replaced `pptoggle` boolean with direct `audio.paused` reads — eliminates a class of state divergence bugs
- Added `waiting`/`stalled`/`playing`/`error` event handlers with visual feedback on the play button (orange = buffering, green = fully downloaded, red = error)
- Re-registers MediaSession on `visibilitychange` to visible, in case iOS cleared the session while backgrounded
- `previoustrack`/`nexttrack` handlers registered (iOS requires these to classify the session as fully controllable)

---

## The Resume Problem

### Symptom

When audio is paused and the screen is locked, tapping play on the lock screen causes the position counter to advance but produces no sound.

### Root cause

iOS suspends its hardware audio output session when a PWA has no actively playing audio. The `<audio>` element continues to advance `currentTime` internally (it's just incrementing a number) but the output pipeline to the hardware is disconnected. There is no web API that can reactivate the hardware audio session without a user gesture in the foreground.

This is distinct from a paused-while-foregrounded case: if the user pauses in-app and immediately taps play from the lock screen (before iOS has a chance to suspend the session), it works. The failure happens after the session has been suspended — typically after the audio has been paused for more than a few seconds while the screen is locked.

### What was tried and why it failed

**Web Audio `AudioContext`** (`audioCtx.createMediaElementSource(audio)`): Once an audio element is routed through an AudioContext, the context's output is the only path to the hardware. If iOS suspends the context (which it does when the session goes idle), all audio is silenced — not just rerouted. This caused a serious regression: locking the screen stopped playback entirely and the in-app play button also stopped working. **Reverted.**

### What would actually fix it

The hardware audio session can only be reactivated by a foreground user gesture. On the web platform, there is no equivalent to iOS's `AVAudioSession.setActive(true)`. The options are:

1. **Capacitor or Cordova wrapper** — wraps the PWA in a native WKWebView shell with access to `AVAudioSession`, allowing the native layer to reactivate the session on MediaSession events. This is the only complete fix.
2. **Accept the limitation** — the current implementation is at the ceiling of what a PWA can do on iOS. Everything works except resuming after the audio session has been suspended.

---

## Current State

| Scenario | Works |
|----------|-------|
| Pause from lock screen | ✓ |
| Skip forward/backward from lock screen | ✓ |
| Seek via lock screen scrubber | ✓ |
| Lock screen shows title and artwork | ✓ |
| Resume from lock screen (session still active) | ✓ |
| Resume from lock screen (session suspended) | ✗ — counter advances, no sound |
| All in-app controls | ✓ |

---

## Files Changed

| File | Changes |
|------|---------|
| `views/playtranspwa.hbs` | MediaSession API, `pptoggle` removal, stall/error handlers |
