# -*- coding: utf-8 -*-
import json, io
m = json.load(io.open(r'G:\ostriv-znan\tools\manifest.json', encoding='utf-8'))
o = io.open(r'G:\ostriv-znan\програма-1-клас\робоче\manifest_peek.txt', 'w', encoding='utf-8')
for k, v in m.items():
    if isinstance(v, str):
        o.write('%s (str): %s\n\n' % (k, v))
        continue
    o.write('=== %s (%d) ===\n' % (k, len(v)))
    for i, (kk, vv) in enumerate(v.items()):
        o.write('  %s -> %s\n' % (kk, json.dumps(vv, ensure_ascii=False)[:420]))
        if i > 5:
            o.write('  ... ще %d\n' % (len(v) - i - 1))
            break
    o.write('\n')
o.close()
print('ok')
