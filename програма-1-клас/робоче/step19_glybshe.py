# -*- coding: utf-8 -*-
"""Крок 19. Читає найцікавіші місця авторських програм повністю.

Крок 18 показав, ДЕ шукати. Тут беремо довгі шматки довкола ключових
місць у чотирьох системах, які найбільше відрізняються способом роботи:
вальдорфська (епоха), «Освіта. Діти. Майбутнє» (тематичні блоки),
«Інтелект України», «Росток».
"""
import io, os, re

B = r'G:\ostriv-znan\програма-1-клас\робоче\txt_avtorski'
OUT = r'G:\ostriv-znan\програма-1-клас\робоче\_глибше.md'
TARGETS = [
 ('\u0432\u0430\u043b\u044c\u0434\u043e\u0440\u0444', ['\u0435\u043f\u043e\u0445', '\u0440\u0438\u0442\u043c', '\u0434\u0432\u043e\u0445\u0433\u043e\u0434\u0438\u043d', '\u0441\u043f\u043e\u0433\u0430\u0434', '\u043e\u0431\u0440\u0430\u0437']),
 ('odm',            ['\u0442\u0435\u043c\u0430\u0442\u0438\u0447\u043d\u0438\u0445 \u0431\u043b\u043e\u043a', '\u043a\u0430\u043d\u0430\u043b', '\u0456\u043d\u0442\u0435\u043b\u0435\u043a\u0442-\u043a\u0430\u0440\u0442']),
 ('intelekt',       ['\u0435\u0439\u0434\u0435\u0442', '\u043f\u0430\u043c\u2019\u044f\u0442', '\u0448\u0432\u0438\u0434\u043a', '\u0442\u0440\u0435\u043d\u0430\u0436', '\u0441\u0438\u0441\u0442\u0435\u043c\u0430 \u0440\u043e\u0431\u043e\u0442']),
 ('rostok',         ['\u0434\u0456\u044f\u043b\u044c\u043d\u0456\u0441\u043d', '\u0432\u0456\u0434\u043a\u0440\u0438\u0442', '\u043f\u0440\u043e\u0431\u043b\u0435\u043c\u043d']),
 ('krylatykh',      ['\u0442\u043e\u043b\u043e\u043a', '\u043a\u0432\u0435\u0441\u0442', '\u0444\u043e\u0440\u043c']),
 ('krayina',        ['\u0440\u043e\u043b\u044c\u043e\u0432', '\u0432\u0438\u043a\u043b\u0438\u043a', '\u0444\u043e\u0440\u043c']),
 ('DRiM',           ['\u0440\u043e\u0437\u0432\u0438\u0432\u0430\u043b\u044c\u043d', '\u043d\u0430\u0432\u0447\u0430\u043b\u044c\u043d\u0430 \u0437\u0430\u0434\u0430\u0447', '\u043c\u043e\u0434\u0435\u043b']),
]
out = io.open(OUT, 'w', encoding='utf-8')
out.write('# Що саме роблять авторські системи інакше\n\n'
          'Довгі витяги довкола ключових місць. Читати очима.\n\n')
files = sorted(f for f in os.listdir(B) if f.endswith('.txt'))
for tag, keys in TARGETS:
    picked = [f for f in files if tag.lower() in f.lower()]
    if not picked:
        continue
    out.write('# === %s ===\n\n' % tag)
    seen = set()
    for f in picked[:3]:
        t = io.open(os.path.join(B, f), encoding='utf-8').read()
        low = t.lower()
        for key in keys:
            for m in list(re.finditer(re.escape(key), low))[:3]:
                a, b = max(0, m.start() - 450), min(len(t), m.end() + 650)
                frag = re.sub(r'\s+', ' ', t[a:b]).strip()
                h = frag[:80]
                if h in seen:
                    continue
                seen.add(h)
                out.write('**%s** / `%s`\n\n> %s\n\n' % (f.replace('.txt', '')[:55], key, frag))
out.close()
print('готово,', os.path.getsize(OUT) // 1024, 'КБ')
