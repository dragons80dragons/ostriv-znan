# -*- coding: utf-8 -*-
"""Службове: показує сторінки буквара, щоб побачити, як підписано нову літеру."""
import json, io, os, sys
B = r'G:\ostriv-znan\програма-1-клас\робоче'
idx = json.load(io.open(os.path.join(B, 'index1.json'), encoding='utf-8'))
needle = sys.argv[1]
lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (10, 22)
out = []
for r in idx:
    if needle.lower() in r['path'].lower() and r.get('txt') and r.get('status') == 'raw':
        t = io.open(os.path.join(B, 'txt', r['txt']), encoding='utf-8').read()
        pages = t.split('\f')
        out.append('### %s  (%d стор.)' % (r['path'], len(pages)))
        for i in range(lo, min(hi, len(pages))):
            body = ' / '.join(x.strip() for x in pages[i].splitlines() if x.strip())
            out.append('[%d] %s' % (i, body[:300]))
        out.append('')
io.open(os.path.join(B, 'peek.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out)[:40])
