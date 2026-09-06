# Conference Demo Script

Target resolution: 1440×900. Target duration: ~6 minutes.

## 0. Setup (before the audience arrives)

```bash
make dev   # starts apps/api on :8000 and apps/web on :3000
```
Open `http://localhost:3000/studio`. Confirm the System Status page
(`/status`) shows `status: ok` and all providers listed as `mock-*`.

## 1. Analyse a code-switched sentence (60s)

- Click the sample chip **"Hindi + English code-switch"** (e.g.
  *"मुझे कल 5 बजे meeting है।"*).
- Click **Analyse Text**.
- Point out: token chips colored by script (Devanagari vs Latin), the
  `en` language label on "meeting" inside an otherwise Hindi sentence,
  and the dashed-underline uncertainty indicator on "meeting".

## 2. Fix a pronunciation (60s)

- Click the "meeting" chip → candidate panel opens with 2–3 ranked
  phoneme strings and confidence scores.
- Select the second candidate, then open the manual phoneme editor and
  tweak one symbol to show hand-editing works.
- Click **Save to Lexicon**. Switch to **Pronunciation Lexicon** tab,
  show the new row, edit its notes field inline, go back to Studio.

## 3. Stream synthesis (90s)

- Set speed to 1.1x, pitch +2, energy 1.0, streaming ON, chunk size
  200ms.
- Click **Start**. Narrate: waveform is filling in left-to-right,
  audio is already playing while the right side of the waveform is
  still blank, the buffer indicator is green.
- Point at **First-audio latency** and **RTF** updating live, and the
  P50/P95/P99 chunk-latency readout.

## 4. Cancel and resume with an edit (60s)

- Mid-stream, click **Cancel** — audio and waveform growth stop
  instantly.
- Edit the *tail* of the text (anything after the current playhead) —
  the UI greys out the already-synthesized prefix as non-editable... in
  Phase 1 this is enforced by convention (edit box) rather than a
  hard-locked prefix range; call this out if asked (see Limitations).
- Click **Resume** — synthesis continues from the edit point under a
  new revision; the previously played waveform prefix is untouched.

## 5. Compare offline vs. streaming (60s)

- Toggle to **Offline**, click **Start** — note there is no partial
  playback; audio and full waveform appear only once the whole
  utterance is ready.
- Contrast the single offline RTF number against the streaming run's
  first-audio latency + percentiles.

## 6. Multi-script tour (60s, optional / time-permitting)

- Load the Gujarati and Marathi sample chips, Analyse each, and note
  the script/language labels change accordingly without touching any
  configuration.

## Fallback talking points if something breaks

- If the WebSocket drops: reload `/studio`, the lexicon and analysis
  are stateless REST calls and recover instantly; only the in-flight
  stream is lost.
- If audio does not play: check the browser tab is focused (autoplay
  policies) and that `AudioContext` was resumed by the **Start** click
  (a user gesture) — this is a browser requirement, not a bug.
- Everything shown is backed by deterministic mock providers — the
  same input always produces the same tokens, candidates, and PCM, so a
  re-run after a glitch reproduces exactly what was shown before.
