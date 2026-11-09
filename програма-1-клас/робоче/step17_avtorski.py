# -*- coding: utf-8 -*-
"""Крок 17. Витягає тексти авторських і експериментальних програм.

Навіщо: у грі всі 52 острови влаштовані однаково — питання й варіанти.
Авторські системи (Росток, Інтелект України, вальдорфська, ДРіМ,
розвивальне навчання, «Світ чекає крилатих») саме й відрізняються
ФОРМАТАМИ роботи, а не темами. Шукаємо там те, чого в грі немає.

Експертні висновки беремо теж: у них коротко сказано, чим саме система
відрізняється від типової — це стисліше за саму програму.
Ідемпотентний: уже витягнуте пропускає.
"""
import io, json, os, pymupdf

SRC = ('G:\\' + '\u041e\u0441\u0442\u0440\u0456\u0432 \u0417\u043d\u0430\u043d\u044c \u2014 \u041c\u0430\u0442\u0435\u0440\u0456\u0430\u043b\u0438'
       + '\\00_\u041f\u0440\u043e\u0433\u0440\u0430\u043c\u0438\\\u0410\u0432\u0442\u043e\u0440\u0441\u044c\u043a\u0456 \u0442\u0430 \u0435\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u0456')
OUT = r'G:\ostriv-znan\програма-1-клас\робоче\txt_avtorski'
os.makedirs(OUT, exist_ok=True)

idx = []
files = sorted(os.path.join(r, f) for r, _, fs in os.walk(SRC) for f in fs
               if f.lower().endswith('.pdf'))
for p in files:
    rel = os.path.relpath(p, SRC)
    name = rel.replace(os.sep, '__')[:120] + '.txt'
    dst = os.path.join(OUT, name)
    if os.path.exists(dst):
        idx.append({'pdf': rel, 'txt': name, 'chars': os.path.getsize(dst)})
        continue
    try:
        d = pymupdf.open(p)
        t = '\n\f\n'.join(d[i].get_text() for i in range(d.page_count))
        pages = d.page_count
        d.close()
        tmp = dst + '.tmp'
        io.open(tmp, 'w', encoding='utf-8').write(t)
        os.replace(tmp, dst)
        idx.append({'pdf': rel, 'txt': name, 'chars': len(t), 'pages': pages})
        print('%6d \u0437\u043d. %3d \u0441\u0442. %s' % (len(t), pages, rel[:70]), flush=True)
    except Exception as e:
        print('\u0437\u0431\u0456\u0439:', rel[:60], str(e)[:80], flush=True)
io.open(os.path.join(OUT, '_\u043f\u043e\u043a\u0430\u0436\u0447\u0438\u043a.json'), 'w', encoding='utf-8').write(
    json.dumps(idx, ensure_ascii=False, indent=1))
print('\u0433\u043e\u0442\u043e\u0432\u043e:', len(idx))
