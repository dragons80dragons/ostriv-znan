# -*- coding: utf-8 -*-
"""Крок 20. Кліпи, які додало перетягування.

Знято з живої гри тим самим способом, що й решта (`step15_sverka.py`):
прогін усіх островів у браузері. Перевірено, що жоден id не звучить
двома різними текстами і жоден не порожній — у першому прогоні якраз
знайшлася вада: емодзі-фішки на Острові Питань діставали порожній
хвіст id (`qv_`) і всі читали б одне й те саме.
Ідемпотентний.
"""
import io, json, os

MAN = r'G:\ostriv-znan\tools\manifest.json'
ITEMS = {
 "q_row": "\u041f\u043e\u0441\u0442\u0430\u0432 \u0447\u0438\u0441\u043b\u0430 \u043f\u043e \u043f\u043e\u0440\u044f\u0434\u043a\u0443, \u0432\u0456\u0434 \u043c\u0435\u043d\u0448\u043e\u0433\u043e \u0434\u043e \u0431\u0456\u043b\u044c\u0448\u043e\u0433\u043e",
 "q_order": "\u041f\u043e\u0441\u0442\u0430\u0432 \u043f\u043e \u043f\u043e\u0440\u044f\u0434\u043a\u0443, \u0449\u043e \u0437\u0430 \u0447\u0438\u043c \u0440\u043e\u0431\u0438\u043c\u043e",
 "q_seasons": "\u041f\u043e\u0441\u0442\u0430\u0432 \u043f\u043e\u0440\u0438 \u0440\u043e\u043a\u0443 \u043f\u043e \u043f\u043e\u0440\u044f\u0434\u043a\u0443, \u043f\u043e\u0447\u0438\u043d\u0430\u0439 \u0437 \u043e\u0441\u0435\u043d\u0456",
 "q_abcrow": "\u041f\u043e\u0441\u0442\u0430\u0432 \u0431\u0443\u043a\u0432\u0438 \u0437\u0430 \u0430\u0431\u0435\u0442\u043a\u043e\u044e",
 "q_tamewild": "\u0420\u043e\u0437\u043a\u043b\u0430\u0434\u0438 \u0442\u0432\u0430\u0440\u0438\u043d: \u0434\u0438\u043a\u0456 \u0439 \u0441\u0432\u0456\u0439\u0441\u044c\u043a\u0456",
 "a_wild": "\u0434\u0438\u043a\u0456",
 "a_tame": "\u0441\u0432\u0456\u0439\u0441\u044c\u043a\u0456",
}
man = json.load(io.open(MAN, encoding='utf-8'))
voc = man['voice']['items']
add = [v for v in ITEMS if v not in voc]
for vid, txt in ITEMS.items():
    if vid in voc:
        continue
    voc[vid] = [txt, 'phrase' if len(txt.split()) > 2 else 'word']
io.open(MAN + '.tmp', 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))
os.replace(MAN + '.tmp', MAN)
print('\u0434\u043e\u0434\u0430\u043d\u043e:', len(add), '| \u0443\u0441\u044c\u043e\u0433\u043e \u043a\u043b\u0456\u043f\u0456\u0432:', len(voc))
