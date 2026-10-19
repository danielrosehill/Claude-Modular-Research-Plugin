#!/usr/bin/env python3
"""Render a two-host podcast script to MP3 with Gemini multi-speaker TTS.

Script format (one turn per paragraph, speaker label then colon):

    ALEX: Welcome back. Today we're looking at ...
    SAM: Right, and the first thing to know is ...

Lines that are blank or start with '#' or '[' are ignored, so a script can carry
a title heading and bracketed production notes without them being read aloud.

The script is split into chunks of whole turns (Gemini TTS degrades and can
truncate on long inputs), each chunk is synthesised separately, and the PCM is
concatenated and encoded to MP3 with ffmpeg.

API key resolution: --api-key, then `op read <--op-ref>`, then $GEMINI_API_KEY.
Standard library only; needs ffmpeg on PATH.
"""
import argparse
import base64
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
TURN_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 _-]{0,30}):\s*(.+)$")


def resolve_key(args):
    # Explicit flags beat the environment: a stale exported GEMINI_API_KEY is
    # common, and silently preferring it over a named 1Password ref is wrong.
    if args.api_key:
        return args.api_key
    if args.op_ref:
        out = subprocess.run(["op", "read", args.op_ref], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
        sys.exit(f"op read failed for {args.op_ref}: {out.stderr.strip()}")
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    sys.exit("No Gemini API key: pass --api-key, set GEMINI_API_KEY, or pass --op-ref")


def parse_turns(text):
    turns = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        m = TURN_RE.match(line)
        if m:
            turns.append([m.group(1).strip().upper(), m.group(2).strip()])
        elif turns:
            # continuation of the previous speaker's paragraph
            turns[-1][1] += " " + line
    return turns


def chunk_turns(turns, max_chars):
    chunks, cur, size = [], [], 0
    for spk, txt in turns:
        n = len(spk) + len(txt) + 3
        if cur and size + n > max_chars:
            chunks.append(cur)
            cur, size = [], 0
        cur.append((spk, txt))
        size += n
    if cur:
        chunks.append(cur)
    return chunks


def legacy_model(model):
    return model.startswith("gemini-2.5")


def build_parts(chunk, style, model):
    """The two model generations want incompatible request shapes (verified 2026-10-19).

    gemini-2.5-*-tts: one text part, speakers named inline as "SPK: text"; a
    per-part speechMetadata is rejected ("Speech metadata is not supported").
    gemini-3.x-tts: one part per turn carrying speechMetadata.speaker; a single
    inline-labelled part is rejected ("must specify speech_metadata.speaker for
    each text part"), and systemInstruction is rejected too, so there is nowhere
    to put a style direction — it is dropped for these models.
    """
    if legacy_model(model):
        lines = [f"{spk}: {txt}" for spk, txt in chunk]
        return [{"text": (f"{style}\n\n" if style else "") + "\n".join(lines)}]
    return [{"text": txt, "speechMetadata": {"speaker": spk}} for spk, txt in chunk]


def synth(chunk, idx, args, key, voices):
    body = {
        "contents": [{"parts": build_parts(chunk, args.style.strip(), args.model)}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "multiSpeakerVoiceConfig": {
                    "speakerVoiceConfigs": [
                        {"speaker": spk, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}}
                        for spk, v in voices.items()
                    ]
                }
            },
        },
    }
    url = API.format(model=args.model, key=key)
    last = None
    for attempt in range(args.retries):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
            parts = data["candidates"][0]["content"]["parts"]
            pcm = b"".join(base64.b64decode(p["inlineData"]["data"]) for p in parts if "inlineData" in p)
            if not pcm:
                raise RuntimeError(f"no audio in response: {json.dumps(data)[:300]}")
            return idx, pcm
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
        except Exception as e:  # noqa: BLE001 - retry anything transient
            last = str(e)
        time.sleep(2 ** attempt * 3)
    raise RuntimeError(f"chunk {idx} failed after {args.retries} attempts: {last}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", help="podcast script (.md/.txt)")
    ap.add_argument("out", help="output .mp3 path")
    ap.add_argument("--model", default="gemini-3.8-flash-tts")
    ap.add_argument("--voices", default="",
                    help="SPEAKER=Voice,SPEAKER=Voice (default: first two speakers -> Kore, Puck)")
    ap.add_argument("--style", default="Read this as a warm, curious, unhurried educational podcast conversation between two hosts.",
                    help="style direction prepended to every chunk (gemini-2.5 models only; 3.x rejects it)")
    ap.add_argument("--max-chars", type=int, default=3000)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--bitrate", default="96k")
    ap.add_argument("--api-key")
    ap.add_argument("--op-ref", help="1Password secret reference for the key, e.g. op://Vault/Item/password")
    args = ap.parse_args()

    turns = parse_turns(open(args.script, encoding="utf-8").read())
    if not turns:
        sys.exit("No 'SPEAKER: text' turns found in script")
    speakers = list(dict.fromkeys(s for s, _ in turns))
    if len(speakers) > 2:
        sys.exit(f"Gemini multi-speaker TTS takes exactly 2 speakers; script has {speakers}")
    voices = {}
    for pair in filter(None, args.voices.split(",")):
        k, v = pair.split("=", 1)
        voices[k.strip().upper()] = v.strip()
    defaults = iter(["Kore", "Puck"])
    for s in speakers:
        voices.setdefault(s, next(defaults))
    voices = {s: voices[s] for s in speakers}
    if len(voices) == 1:  # single-speaker script still needs two configs
        voices["NARRATOR_UNUSED"] = "Puck"

    key = resolve_key(args)
    chunks = chunk_turns(turns, args.max_chars)
    words = sum(len(t.split()) for _, t in turns)
    print(f"{len(turns)} turns, {words} words, {len(chunks)} chunks, model {args.model}, voices {voices}",
          file=sys.stderr)

    results = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(synth, c, i, args, key, voices) for i, c in enumerate(chunks)]
        for f in cf.as_completed(futs):
            i, pcm = f.result()
            results[i] = pcm
            print(f"  chunk {i + 1}/{len(chunks)} ok ({len(pcm) / 48000:.1f}s)", file=sys.stderr)

    with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as tmp:
        silence = b"\x00\x00" * int(24000 * 0.4)
        for i in range(len(chunks)):
            tmp.write(results[i])
            tmp.write(silence)
        pcm_path = tmp.name
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", "24000", "-ac", "1",
                        "-i", pcm_path, "-codec:a", "libmp3lame", "-b:a", args.bitrate, args.out], check=True)
    finally:
        os.unlink(pcm_path)
    dur = sum(len(p) for p in results.values()) / 48000
    print(json.dumps({"out": args.out, "duration_seconds": round(dur, 1), "chunks": len(chunks),
                      "words": words, "model": args.model, "voices": voices}))


if __name__ == "__main__":
    main()
