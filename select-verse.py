#!/usr/bin/env python3
"""select-verse"""
import json, os, random

QDIR = os.path.dirname(os.path.abspath(__file__))
READY = os.path.join(QDIR, "tafsir-short.json")
FALLBACK_READY = os.path.join(QDIR, "tafsir-ready.json")
USED = os.path.join(QDIR, "used-verses.json")
LAST = os.path.join(QDIR, "last-verse.json")

def load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

ready = load(READY, {}).get("keys") or load(FALLBACK_READY, {"keys": []})["keys"]
raw = load(USED, []); used = set(raw.get("used", []) if isinstance(raw, dict) else raw)

candidates = [k for k in ready if k not in used]
if not candidates:
    used = set()
    candidates = list(ready)
    with open(USED, "w", encoding="utf-8") as f:
        json.dump({"used": []}, f, ensure_ascii=False)

key = random.SystemRandom().choice(candidates)
used.add(key)
with open(USED, "w", encoding="utf-8") as f:
    json.dump(sorted(used), f, ensure_ascii=False)
with open(LAST, "w", encoding="utf-8") as f:
    json.dump({"last": key}, f, ensure_ascii=False)

print(key)
