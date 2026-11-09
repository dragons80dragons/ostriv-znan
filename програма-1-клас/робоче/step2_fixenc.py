# -*- coding: utf-8 -*-
"""Крок 2. txt_raw\ -> txt\ з виправленим шрифтовим кодуванням.
Пастка: наївне перекодування cp1252->cp1251 псує справжню латиницю з
діакритикою (нім. "Ää", угор. "á", ісп. "ñ") — вона теж перетворюється на
кирилицю. Тому рішення ухвалюється ПО ФАЙЛУ і перевіряється СЛОВНИКОМ
українських слів, зібраним із файлів, де текст і так чистий.
Ідемпотентний, атомарний запис."""
import os, io, json, re, collections
B = r"G:\ostriv-znan\програма-1-клас\робоче"
RAW, OUT = os.path.join(B, "txt_raw"), os.path.join(B, "txt")
IDXP, DICTP = os.path.join(B, "index1.json"), os.path.join(B, "_словник.txt")
os.makedirs(OUT, exist_ok=True)
CYR = re.compile(r"[\u0400-\u04ff]")
WORD = re.compile(r"[\u0400-\u04ffA-Za-z\u00c0-\u017f'\u2019-]+")
# таблиця: символ, який дало хибне декодування -> справжня кирилиця cp1251
CMAP = {}
for b in range(0x80, 0x100):
    try:
        src = bytes([b]).decode("cp1252"); dst = bytes([b]).decode("cp1251")
    except Exception: continue
    if CYR.match(dst): CMAP[src] = dst
def convert(tok): return "".join(CMAP.get(c, c) for c in tok)
def ratio(t):
    cy = len(CYR.findall(t)); al = sum(1 for c in t if c.isalpha())
    return cy / al if al else 0.0
def save_json(o, p):
    t = p + ".tmp"; io.open(t, "w", encoding="utf-8").write(json.dumps(o, ensure_ascii=False, indent=1)); os.replace(t, p)
def write_atomic(p, s):
    t = p + ".tmp"; io.open(t, "w", encoding="utf-8").write(s); os.replace(t, p)

idx = json.load(io.open(IDXP, encoding="utf-8"))
live = [r for r in idx if r.get("txt") and r.get("status") not in ("dup", "err")]

# --- словник: слова з файлів, де кирилиця вже чиста ---
if os.path.exists(DICTP):
    voc = set(io.open(DICTP, encoding="utf-8").read().split())
else:
    cnt = collections.Counter()
    for r in live:
        t = io.open(os.path.join(RAW, r["txt"]), encoding="utf-8").read()
        if ratio(t) < 0.95: continue
        for w in WORD.findall(t.lower()):
            if len(w) >= 4 and CYR.match(w): cnt[w] += 1
    voc = {w for w, n in cnt.items() if n >= 3}
    write_atomic(DICTP, "\n".join(sorted(voc)))
print("словник:", len(voc), "слів", flush=True)

for r in live:
    if r.get("enc") is not None and os.path.exists(os.path.join(OUT, r["txt"])): continue
    t = io.open(os.path.join(RAW, r["txt"]), encoding="utf-8").read()
    toks = [w for w in WORD.findall(t) if any(c in CMAP for c in w)]
    hit = mis = 0
    for w in toks[:4000]:
        c = convert(w).lower()
        if len(c) < 4: continue
        if c in voc: hit += 1
        else: mis += 1
    score = hit / (hit + mis) if (hit + mis) else 0.0
    r["enc_cands"], r["enc_score"] = len(toks), round(score, 3)
    if len(toks) >= 30 and score >= 0.35:
        # рішення ухвалене по файлу -> переводимо ВСІ токени-кандидати,
        # зокрема короткі службові слова ("для", "та", "за"), яких у словнику немає
        fixed = "".join(convert(p) if (WORD.fullmatch(p) and any(c in CMAP for c in p)) else p
                        for p in re.split(r"(" + WORD.pattern + r")", t))
        r["enc"] = "fixed"
    else:
        fixed = t; r["enc"] = "asis"
    r["cyr"] = round(ratio(fixed), 2)
    write_atomic(os.path.join(OUT, r["txt"]), fixed)
    save_json(idx, IDXP)
    print(f"{r['enc']:5} score={score:.2f} cand={len(toks):6} cyr={r['cyr']:.2f} {r['path'][:60]}", flush=True)
print("DONE")
