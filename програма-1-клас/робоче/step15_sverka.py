# -*- coding: utf-8 -*-
"""Крок 15. Звіряє manifest із тим, що гра СПРАВДІ просить озвучити.

Перелік id знято з живої гри (прогін усіх островів у браузері) і лежить
поруч у `_id_гри.txt`. Скрипт каже дві речі:
  * чого бракує в маніфесті — такі місця гра читатиме синтезатором;
  * що в маніфесті зайве — ці кліпи згенеруються намарне.
Нічого не змінює: це перевірка, а рішення за людиною.
"""
import io, json, os

MAN = r'G:\ostriv-znan\tools\manifest.json'
W = r'G:\ostriv-znan\програма-1-клас\робоче'
used = set(io.open(os.path.join(W, '_id_\u0433\u0440\u0438.txt'), encoding='utf-8').read().split())
voc = json.load(io.open(MAN, encoding='utf-8'))['voice']['items']
have = set(voc)
miss = sorted(used - have)
extra = sorted(have - used)
out = []
out.append('# Звірка озвучення: гра проти маніфесту\n')
out.append('Гра просить: %d кліпів. У маніфесті: %d.\n' % (len(used), len(have)))
out.append('## Бракує в маніфесті — читатиме синтезатор (%d)\n' % len(miss))
out.append('\n'.join('- `%s`' % m for m in miss) if miss else 'немає')
out.append('\n\n## У маніфесті є, а гра не просить (%d)\n' % len(extra))
out.append('Це не помилка: частина — з демоверсії `index.html`, яка лишається\n'
           'як окрема гра і має свої кліпи.\n')
out.append('\n'.join('- `%s` — %s' % (e, voc[e][0]) for e in extra) if extra else 'немає')
io.open(os.path.join(W, '_\u0437\u0432\u0456\u0440\u043a\u0430_\u043e\u0437\u0432\u0443\u0447\u0435\u043d\u043d\u044f.md'),
        'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\u0433\u0440\u0430 \u043f\u0440\u043e\u0441\u0438\u0442\u044c %d | \u0432 \u043c\u0430\u043d\u0456\u0444\u0435\u0441\u0442\u0456 %d | \u0431\u0440\u0430\u043a\u0443\u0454 %d | \u0437\u0430\u0439\u0432\u043e\u0433\u043e %d'
      % (len(used), len(have), len(miss), len(extra)))
if miss:
    print('\u0431\u0440\u0430\u043a\u0443\u0454:', ' '.join(miss))
