"""طبع نص التفسير كاملًا لآية (للرد الرباعي) — الاستخدام: python3 print-tafsir.py <سورة> <آية>"""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lookup import get_tafsir

s, a = int(sys.argv[1]), int(sys.argv[2])
t, src = get_tafsir(s, a)
print("SRC:", src)
print(t or "(لا تفسير)")
