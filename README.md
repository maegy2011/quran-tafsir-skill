# Quran Tafsir Skill — Final (30 Oct 2026)

مهارة القرآن الكريم وتفسير ابن كثير — مصدر حقيقة محلي، تنسيق تيليجرام HTML احترافي.

## المميزات النهائية
- **فلترة مسبقة ≤50 كلمة:** `tafsir-short.json` (1614 آية) — `pick-verse-50.py` يعد الكلمات بـ split ويتخطى الأطول.
- **عدم تكرار per-user:** `used-verses-users.json` حسب `chat_id` + سجل عالمي، مع `auto-reset` لدورة جديدة عند النفاد.
- **شرح AI ≤20 كلمة:** تكثيف أمين لنص ابن كثير فقط — بلا هلوسة، بلا مقدمات، بنبرة إيمانية هادئة (`max_tokens 40-50`). يرفض الأطول بخطأ `AI_EXPLANATION_TOO_LONG`.
- **تنسيق HTML + Expandable:** `format-tail.py --html` يخرج قالب `parse_mode=HTML` مع `<blockquote expandable>` وفواصل `━━━━━━━━━━━━━━━━━━━`.

## الاستخدام
```bash
python3 pick-verse-50.py --user <chat_id>
# → {"key":"47:7","surah":"...","verse":"...","tafsir":"...","words":45}

python3 format-tail.py --html "47:7" "شرح ≤20 كلمة"
# → {"html":"...<blockquote expandable>...","chunks":[...]}
```

### القالب الموحد
```
━━━━━━━━━━━━━━━━━━━
✨ <b>﴿ {verse} ﴾</b>
📖 <i>سورة {name} (الآية {a})</i>
<blockquote expandable>
📖 <b>التفسير (ابن كثير):</b>
{tafsir}

💡 <b>إضاءة تدبرية:</b>
{ai_exp}
</blockquote>
━━━━━━━━━━━━━━━━━━━
```

## قواعد مصدر الحقيقة
- نص الآية من `quran-uthmani.txt` (6236 آية، رسم عثماني) — ممنوع كتابته من الذاكرة.
- التفسير من `tafsir-ibn-kathir/<surah>.json` فقط — لا fallback ولا تفسير من النموذج.
- التفاصيل الكاملة في `SKILL.md`.

## الفروع
- `main` — الكود النهائي المستقر.
- `master` — مرآة التوافق.
