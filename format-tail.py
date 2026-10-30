#!/usr/bin/env python3
"""format-tail: تنسيق ذيل الرد (آية + تفسير) بتنسيق محدّث — HTML (Telegram).

الاستخدام: python3 quran/format-tail.py S:A
يطبع JSON: {"key","surah","ayah","chunks":[{"aside": "..."}], "footer_placeholder"}
- chunks: قائمة رسائل؛ الأولى تحمل verse+surah+hr+tafsir، والمتبقية continuations.
- لا fallback، لا تفسير من النموذج.
"""
import json, os, re, sys
QDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QDIR)
from lookup import get_verse, get_tafsir

LIMIT = 3500

def surah_name(surah):
    d = json.load(open(os.path.join(QDIR, "tafsir-ibn-kathir", f"{surah}.json"), encoding="utf-8"))
    return d.get("name", str(surah))

def split_sentences(tafsir):
    out = []
    for para in tafsir.split("\n"):
        para = para.strip()
        if not para:
            continue
        for part in re.split(r"(?<=\.)\s+", para):
            part = part.strip()
            if part:
                out.append(part)
    return out

key = sys.argv[1] if len(sys.argv) > 1 else None
ai_exp = sys.argv[2] if len(sys.argv) > 2 else None
if not key or not ai_exp:
    print("usage: format-tail.py S:A AI_EXPLANATION<=20 words (required)", file=sys.stderr); sys.exit(2)
if len(ai_exp.split()) > 20:
    print("AI_EXPLANATION_TOO_LONG: " + str(len(ai_exp.split())) + " words (max 20)", file=sys.stderr); sys.exit(2)
s, a = key.split(":"); s, a = int(s), int(a)
verse = get_verse(key)
tafsir, src = get_tafsir(s, a)
if not verse or not tafsir:
    print("NO_DIRECT_TAFSIR: " + key, file=sys.stderr); sys.exit(1)
name = surah_name(s)
sentences = split_sentences(tafsir)

header = f"🕌 <b>﴿ {verse} ﴾</b>\n📖 سورة {name} — الآية {a}\n✨ التفسير (ابن كثير):\n<hr/>\n"
chunks = []
current = ""
is_first_chunk = True
for sent in sentences:
    line = f"🌿 <i>{sent}</i><br/>\n"
    prefix = header if (current == "" and is_first_chunk) else ""
    if current == "" and not is_first_chunk:
        prefix = ""
    if current and len(current) + len(line) > LIMIT:
        chunks.append(current.rstrip())
        current = ""
        is_first_chunk = False
        prefix = ""
    if current == "":
        current = prefix
    current += line
if current.strip():
    chunks.append(current.rstrip())

if not chunks:
    chunks = [header.rstrip()]

chunks[-1] = chunks[-1].rstrip() + f"\n<hr/>\n💡 <b>شرح AI:</b> {ai_exp}"

out = {
    "key": key,
    "surah": name,
    "ayah": a,
    "src": src,
    "ai_explanation": ai_exp,
    "chunks": [{"aside": c} for c in chunks],
    "footer_placeholder": "🤖 <model> | 🧠 <thinking> | 📥 <in> / 📤 <out> | 📚 <ctx>/<total> (<pct>) | 💾 <cache%>",
}
print(json.dumps(out, ensure_ascii=False))
