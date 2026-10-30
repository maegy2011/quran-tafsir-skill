#!/usr/bin/env python3
"""verify-tail"""
import json, os, sys
QDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QDIR)
from lookup import get_verse, get_tafsir

if len(sys.argv) < 4:
    print("usage: verify-tail.py S:A VERSE TAFSIR", file=sys.stderr); sys.exit(2)
key = sys.argv[1]
verse_in = sys.argv[2]
tafsir_in = sys.argv[3]
s, a = key.split(":"); s, a = int(s), int(a)
v = get_verse(key)
t, src = get_tafsir(s, a)
ok = (v == verse_in) and (t == tafsir_in) and (t is not None)
print("OK" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
