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
    user = None
    args = sys.argv[1:]
    # --user CHAT_ID لتتبع per-user + --count N
    if "--user" in args:
        i = args.index("--user")
        if i + 1 < len(args):
            user = str(args[i + 1])
    if "--count" in args:
        i = args.index("--count")
        if i + 1 < len(args):
            try:
                n = int(args[i + 1])
            except ValueError:
                n = 1
    ready = load(os.path.join(QDIR, "tafsir-short.json"), {}).get("keys") \
        or load(os.path.join(QDIR, "tafsir-ready.json"), {}).get("keys", [])
    # per-user state: used-verses-users.json {chat_id: [keys]} + auto-reset عند النفاد
    users_path = os.path.join(QDIR, "used-verses-users.json")
    users_map = load(users_path, {})
    if not isinstance(users_map, dict):
        users_map = {}
    used_user = set(users_map.get(str(user), []) if user else [])
    raw = load(os.path.join(QDIR, "used-verses.json"), [])
    used = set(raw.get("used", []) if isinstance(raw, dict) else raw)
    # إن استنفد المستخدم كل القائمة المفلترة → إعادة تدوير تلقائية لدورة جديدة
    if user and len(used_user) >= len(ready) and ready:
        used_user = set()
    rng = random.SystemRandom()
    out = []
    attempts = 0
    while len(out) < n and attempts < 5000:
        attempts += 1
        key = rng.choice(ready)
        if key in used or (user and key in used_user):
            # لو القائمة العالمية غطت كل الجاهز لكن المستخدم لم يستنفد، اسمح بآية خارج العالمية بشرط عدم تكرارها للمستخدم
            if key in used_user:
                continue
            if user and key not in used_user:
                pass  # per-user يتجاوز العالمي لمنع الجمود
            else:
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
        if user:
            used_user.add(key)
        out.append({"key": key, "surah": surah_name, "verse": verse,
                    "tafsir": tafsir, "words": wc})
    # حفظ الاستخدام (يقبل الصيغتين list / dict) + حفظ per-user مع auto-reset
    try:
        if user:
            users_map[str(user)] = sorted(used_user)
            with open(users_path, "w", encoding="utf-8") as f:
                json.dump(users_map, f, ensure_ascii=False)
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
