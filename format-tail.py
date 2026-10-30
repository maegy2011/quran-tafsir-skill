#!/usr/bin/env python3
"""format-tail: تنسيق ذيل الرد (آية + تفسير) — نص عادي RTL، كل عنصر على سطر.

الشكل المطلوب (بأمر محمد):
🕌 ﴿ {verse} ﴾
📖 سورة {name} — الآية {a}
✨ التفسير (ابن كثير):
🌿 {tafsir}
💡 شرح AI: {ai_exp}

- نص عادي بلا <b>/<i>/<hr/> — الفواصل أسطر فقط.
- علامة RTL (U+200F) في أول كل سطر لمحاذاة اليمين.
- الجمل المتعددة: كل جملة على سطر لوحده يبدأ بـ 🌿.
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

RTL = "‏"
header_lines = [
    f"{RTL}🕌 ﴿ {verse} ﴾",
    f"{RTL}📖 سورة {name} — الآية {a}",
    f"{RTL}✨ التفسير (ابن كثير):",
]
tafsir_lines = [f"{RTL}🌿 {sent}" for sent in sentences]
footer_line = f"{RTL}💡 شرح AI: {ai_exp}"

all_lines = header_lines + tafsir_lines + [footer_line]

# تقسيم الرسائل الطويلة على chunks مع الحفاظ على سطر-لكل-عنصر
chunks = []
current = ""
for ln in all_lines:
    piece = ln + "<br/>\n"
    if current and len(current) + len(piece) > LIMIT:
        chunks.append(current.rstrip())
        current = ""
    current += piece
if current.strip():
    chunks.append(current.rstrip())

if not chunks:
    chunks = ["<br/>\n".join(header_lines).rstrip()]

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
