# -*- coding: utf-8 -*-
"""Крок 7. Витягає з підручників 1 класу їхній ЗМІСТ (перелік тем у порядку).

Підручник майже завжди має сторінку «ЗМІСТ» із рядками «Тема .... 12».
Беремо сторінки, де слово «зміст» стоїть самостійно (не «змістова лінія»),
і збираємо з них рядки, що закінчуються номером сторінки. Якщо змісту немає
(частина книжок його не має або він намальований), пишемо про це прямо,
а не вдаємо, що тем немає.

Ідемпотентний: пише `_зміст_підручників.md`.
"""
import json, io, os, re

B = r'G:\ostriv-znan\програма-1-клас\робоче'
TXT = os.path.join(B, 'txt')
SUBJ = ('\u041c\u0430\u0442\u0435\u043c\u0430\u0442\u0438\u043a\u0430',
        '\u042f \u0434\u043e\u0441\u043b\u0456\u0434\u0436\u0443\u044e \u0441\u0432\u0456\u0442',
        '\u041c\u0438\u0441\u0442\u0435\u0446\u0442\u0432\u043e')
RE_ZMIST = re.compile(r'(?:^|\n)\s*[\u0417\u0437]\s?[\u041c\u043c]\s?[\u0406\u0456]\s?[\u0421\u0441]\s?[\u0422\u0442]\s*(?:\n|$)')
# «Тема ...... 12» або «Тема   12»
RE_ROW = re.compile(r'^\s*(.{4,90}?)[\s.\u2026\u00b7]{2,}(\d{1,3})\s*$')
RE_ROW2 = re.compile(r'^\s*(.{4,90}?)\s+(\d{1,3})\s*$')
BAD = re.compile(r'^[\d\s.\u2026\u00b7\-]+$')


def toc_pages(pages):
    out = []
    for i, p in enumerate(pages):
        if RE_ZMIST.search(p):
            out.extend(range(i, min(i + 4, len(pages))))
    return sorted(set(out))


def rows_from(pages, nums):
    rows, seen = [], set()
    for i in nums:
        for line in pages[i].splitlines():
            line = line.strip()
            if not line or BAD.match(line):
                continue
            m = RE_ROW.match(line) or RE_ROW2.match(line)
            if not m:
                continue
            t = re.sub(r'[\s.\u2026\u00b7]+$', '', m.group(1)).strip()
            if len(t) < 4 or BAD.match(t):
                continue
            key = (t.lower(), m.group(2))
            if key in seen:
                continue
            seen.add(key)
            rows.append((int(m.group(2)), t))
    rows.sort()
    return rows


def main():
    idx = json.load(io.open(os.path.join(B, 'index1.json'), encoding='utf-8'))
    L = []
    a = L.append
    a('# Зміст підручників 1 класу — послідовності тем\n')
    a('Витягнуто `step7_zmist.py` зі сторінок «ЗМІСТ». Порядок — за номерами')
    a('сторінок, тобто такий, у якому автор веде рік. Де змісту немає у')
    a('текстовому шарі, так і написано — щоб не здавалося, ніби тем немає.\n')
    for s in SUBJ:
        a('## %s\n' % s)
        books = [r for r in idx if r.get('subject') == s and r.get('status') == 'raw'
                 and r.get('txt')]
        books.sort(key=lambda r: r['path'])
        for r in books:
            t = io.open(os.path.join(TXT, r['txt']), encoding='utf-8').read()
            pages = t.split('\f')
            nums = toc_pages(pages)
            rows = rows_from(pages, nums) if nums else []
            au = ', '.join(r.get('authors') or []) or '—'
            a('### %s' % au)
            a('')
            a('- `%s` (%s стор.)' % (os.path.basename(r['path']), r.get('pages')))
            if not rows:
                a('- змісту в текстовому шарі не знайдено')
                a('')
                continue
            a('- тем у змісті: %d' % len(rows))
            a('')
            for n, title in rows:
                a('   %3d. %s' % (n, title))
            a('')
    io.open(os.path.join(B, '_зміст_підручників.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('ok')


main()
