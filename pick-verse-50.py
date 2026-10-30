#!/usr/bin/env python3
"""اختيار آية بتفسير ≤50 كلمة لتوفير التوكنز — الاستعمال: pick-verse-50.py [--count N]
- يعد كلمات التفسير (split على المسافات)
- لو >50 يتخطى ويعيد المحاولة حتى يطبق الشرط
- يخرج JSON صغير فقط (الآية + التفسير) لإرساله للذكاء الاصطناعي
- يسجل في used-verses.json لمنع التكرار
"""
import json, os, random, sys

QDIR = os.path.dirname(os.path.abspath(__file__))

def load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def word_count(s: str) -> int:
    return len(s.strip().split())

def get_verse_text(key: str):
    idx = load(os.path.join(QDIR, "verse-index.json"), {}).get("lines", {})
    lineno = idx.get(key)
    if not lineno:
        return None
    with open(os.path.join(QDIR, "quran-uthmani.txt"), encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if i == lineno:
                return line.rstrip("\n").split("|", 1)[1]
    return None

def get_tafsir(surah: int, ayah: int):
    with open(os.path.join(QDIR, f"tafsir-ibn-kathir/{surah}.json"), encoding="utf-8") as f:
        d = json.load(f)
    for e in d.get("ayets", []):
        if e.get("id") == ayah and (e.get("tafsir") or "").strip():
            return e["tafsir"].strip(), e.get("eya", "").strip(), d.get("name", "")
    return None, None, None

def main():
    n = 1
    if len(sys.argv) > 2 and sys.argv[1] == "--count":
        n = int(sys.argv[2])
    ready = load(os.path.join(QDIR, "tafsir-short.json"), {}).get("keys") \
        or load(os.path.join(QDIR, "tafsir-ready.json"), {}).get("keys", [])
    raw = load(os.path.join(QDIR, "used-verses.json"), [])
    used = set(raw.get("used", []) if isinstance(raw, dict) else raw)
    rng = random.SystemRandom()
    out = []
    attempts = 0
    while len(out) < n and attempts < 5000:
        attempts += 1
        key = rng.choice(ready)
        if key in used:
            continue
        s, a = key.split(":")
        tafsir, eya, surah_name = get_tafsir(int(s), int(a))
        if not tafsir:
            continue
        wc = word_count(tafsir)
        if wc > 50:  # تخطي + إعادة المحاولة
            continue
        verse = get_verse_text(key)
        if not verse:
            continue
        used.add(key)
        out.append({"key": key, "surah": surah_name, "verse": verse,
                    "tafsir": tafsir, "words": wc})
    # حفظ الاستخدام (يقبل الصيغتين list / dict)
    try:
        old = load(os.path.join(QDIR, "used-verses.json"), [])
        if isinstance(old, dict):
            old["used"] = sorted(used)
            with open(os.path.join(QDIR, "used-verses.json"), "w", encoding="utf-8") as f:
                json.dump(old, f, ensure_ascii=False)
        else:
            with open(os.path.join(QDIR, "used-verses.json"), "w", encoding="utf-8") as f:
                json.dump(sorted(used), f, ensure_ascii=False)
    except Exception:
        pass
    # إخراج مصغر للـ AI: الآية + التفسير فقط = أقل توكنز
    print(json.dumps(out if n > 1 else (out[0] if out else {}), ensure_ascii=False))

if __name__ == "__main__":
    main()
