# -*- coding: utf-8 -*-
"""Крок 1. Витягає СИРИЙ текст з усіх PDF 1 класу в txt_raw\.
Ідемпотентний: уже витягнуте пропускає. Безпечний при вимкненні світла:
кожен файл пишеться в .tmp і атомарно перейменовується."""
import os, io, json, hashlib, pymupdf
SRC = r"G:\Острів Знань — Матеріали\1 клас"
B   = r"G:\ostriv-znan\програма-1-клас\робоче"
RAW = os.path.join(B, "txt_raw")
os.makedirs(RAW, exist_ok=True)
IDXP = os.path.join(B, "index1.json")
def save_json(obj, path):
    t = path + ".tmp"; io.open(t, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1)); os.replace(t, path)
def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b: break
            h.update(b)
    return h.hexdigest()
idx = json.load(io.open(IDXP, encoding="utf-8")) if os.path.exists(IDXP) else []
done = {r["path"]: r for r in idx}
files = sorted(os.path.join(r, f) for r, _, fs in os.walk(SRC) for f in fs if f.lower().endswith(".pdf"))
seen = {r["sha1"]: r["path"] for r in idx if r.get("sha1") and r.get("status") != "dup"}
for i, p in enumerate(files):
    rel = os.path.relpath(p, SRC)
    if rel in done and done[rel].get("raw_ok"): continue
    rec = done.get(rel) or {"path": rel, "subject": rel.split(os.sep)[0]}
    try:
        rec["mb"] = round(os.stat(p).st_size / 1048576, 1)
        dig = sha1(p); rec["sha1"] = dig[:12]
        if dig[:12] in seen and seen[dig[:12]] != rel:
            rec.update(status="dup", dup_of=seen[dig[:12]], raw_ok=True)
        else:
            seen[dig[:12]] = rel
            d = pymupdf.open(p); rec["pages"] = d.page_count
            t = "\n\f\n".join(d[j].get_text() for j in range(d.page_count)); d.close()
            rec["chars"] = len(t); rec["txt"] = dig[:12] + ".txt"
            dst = os.path.join(RAW, rec["txt"]); tmp = dst + ".tmp"
            io.open(tmp, "w", encoding="utf-8").write(t); os.replace(tmp, dst)
            rec.update(status="scan" if len(t) < 2000 else "raw", raw_ok=True)
    except Exception as e:
        rec.update(status="err", err=str(e)[:200], raw_ok=False)
    if rel not in done: idx.append(rec); done[rel] = rec
    save_json(idx, IDXP)
    print(f"{i+1}/{len(files)} {rec['status']} {rel[:70]}", flush=True)
print("DONE", len(idx))
