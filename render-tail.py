#!/usr/bin/env python3
"""render-tail"""
import json, os, sys
QDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QDIR)
from lookup import get_verse, get_tafsir

key = sys.argv[1] if len(sys.argv) > 1 else None
if not key:
    print("usage: render-tail.py S:A", file=sys.stderr); sys.exit(2)
s, a = key.split(":"); s, a = int(s), int(a)
verse = get_verse(key)
tafsir, src = get_tafsir(s, a)
if not verse or not tafsir or not src:
    print("NO_DIRECT_TAFSIR: " + key, file=sys.stderr); sys.exit(1)
out = {"key": key, "verse": verse, "tafsir": tafsir, "src": src}
print(json.dumps(out, ensure_ascii=False))
