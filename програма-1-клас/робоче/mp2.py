# -*- coding: utf-8 -*-
import json, io
m = json.load(io.open(r'G:\ostriv-znan\tools\manifest.json', encoding='utf-8'))
o = io.open(r'G:\ostriv-znan\програма-1-клас\робоче\manifest_peek.txt','w',encoding='utf-8')
for sec in ('image','music'):
    o.write('=== %s keys: %s\n' % (sec, list(m[sec].keys())))
    for k, v in m[sec].items():
        s = json.dumps(v, ensure_ascii=False)
        o.write('  %s : %s\n' % (k, s[:1500]))
    o.write('\n')
o.write('voice.items count = %d\n' % len(m['voice']['items']))
o.write('voice ids: %s\n' % ' '.join(sorted(m['voice']['items'])))
o.close(); print('ok')
