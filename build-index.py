#!/usr/bin/env python3
"""بناء فهارس القرآن والتفسير لتسريع البحث — يعمل محليًا فقط."""
import json, os
QDIR = os.path.dirname(os.path.abspath(__file__))
QTXT = os.path.join(QDIR, "quran-uthmani.txt")
TDIR = os.path.join(QDIR, "tafsir-ibn-kathir")

# 1) فهرس الآيات: "S:A" -> رقم السطر (1-based) + طول النص
verse_index = {}
with open(QTXT, encoding="utf-8") as f:
    for lineno, line in enumerate(f, 1):
        line = line.rstrip("\n")
        if not line or "|" not in line:
            continue
        key = line.split("|", 1)[0]  # S:A
        verse_index[key] = lineno
with open(os.path.join(QDIR, "verse-index.json"), "w", encoding="utf-8") as f:
    json.dump({"count": len(verse_index), "lines": verse_index}, f, ensure_ascii=False)

# 2) فهرس التفسير: لكل سورة قائمة الـ ids التي لها تفسير غير فارغ فقط (لا fallback)
tafsir_index = {}
ready_keys = []
for fn in sorted(os.listdir(TDIR)):
    if not fn.endswith(".json") or fn.startswith("_"):
        continue
    surah = fn[:-5]
    d = json.load(open(os.path.join(TDIR, fn), encoding="utf-8"))
    ayets = d.get("ayets") or d.get("eyats") or []
    with_tafsir = []
    for a in ayets:
        if (a.get("tafsir") or "").strip():
            with_tafsir.append(a["id"])
            key = f"{surah}:{a['id']}"
            if key in verse_index:
                ready_keys.append(key)
    tafsir_index[surah] = {"with_tafsir": sorted(set(with_tafsir)), "fallback": {}}

with open(os.path.join(TDIR, "_index.json"), "w", encoding="utf-8") as f:
    json.dump(tafsir_index, f, ensure_ascii=False)

# 3) مجموعة جاهزة للتدوير: فقط الآيات ذات تفسير مباشر (لا fallback)
with open(os.path.join(QDIR, "tafsir-ready.json"), "w", encoding="utf-8") as f:
    json.dump({"count": len(ready_keys), "keys": sorted(set(ready_keys))}, f, ensure_ascii=False)

# 4) مجموعة «قصيرة»: تفسير ≤ 55 كلمة (للتد워ور المطلوب)
short_keys = []
for key in ready_keys:
    s, a = key.split(":")
    d = json.load(open(os.path.join(TDIR, f"{s}.json"), encoding="utf-8"))
    ayets = d.get("ayets") or d.get("eyats") or []
    for ay in ayets:
        if ay["id"] == int(a):
            wc = len((ay.get("tafsir") or "").split())
            if wc <= 55:
                short_keys.append(key)
            break
with open(os.path.join(QDIR, "tafsir-short.json"), "w", encoding="utf-8") as f:
    json.dump({"count": len(short_keys), "keys": sorted(set(short_keys)), "max_words": 55}, f, ensure_ascii=False)

print(f"verses: {len(verse_index)}, surahs: {len(tafsir_index)}, tafsir_ready: {len(ready_keys)}")
