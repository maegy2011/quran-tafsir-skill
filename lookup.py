#!/usr/bin/env python3
"""بحث سريع في القرآن والتفسير عبر الفهارس — استعمال: lookup.py 112:3"""
import json, os, sys
QDIR = os.path.dirname(os.path.abspath(__file__))
def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)
def get_verse(key):
    idx = load_json(os.path.join(QDIR, "verse-index.json"))["lines"]
    lineno = idx.get(key)
    if not lineno:
        return None
    with open(os.path.join(QDIR, "quran-uthmani.txt"), encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if i == lineno:
                return line.rstrip("\n").split("|", 1)[1]
    return None
def get_tafsir(surah, ayah):
    tdir = os.path.join(QDIR, "tafsir-ibn-kathir")
    d = load_json(os.path.join(tdir, f"{surah}.json"))
    ayets = d.get("ayets") or d.get("eyats") or []
    by_id = {a["id"]: a for a in ayets}
    a = by_id.get(ayah)
    if a and (a.get("tafsir") or "").strip():
        return (a["tafsir"], f"{surah}:{ayah}")
    return (None, None)
if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "112:3"
    s, a = key.split(":"); s, a = int(s), int(a)
    print("VERSE:", get_verse(key))
    t, src = get_tafsir(s, a)
    print("SRC:", src, "| LEN:", len(t) if t else 0)
