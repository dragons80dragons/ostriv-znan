# -*- coding: utf-8 -*-
"""Крок 22. Ресурси для «знайди на картині».

Три сцени й девʼять умов пошуку. Окремо — назви всіх 33 літер (`let_*`):
їх раніше не було, бо літеру завжди вимовляли всередині довгої фрази
(«Обведи пальцем букву ем»). Тут потрібна сама назва, і ці кліпи ще
знадобляться скрізь, де треба назвати букву.
Ідемпотентний.
"""
import io, json, os

MAN = r'G:\ostriv-znan\tools\manifest.json'
VOICE = {
 "f_alive":  "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0435 \u0436\u0438\u0432\u0435",
 "f_letter": "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0435, \u0449\u043e \u043f\u043e\u0447\u0438\u043d\u0430\u0454\u0442\u044c\u0441\u044f \u043d\u0430 \u0431\u0443\u043a\u0432\u0443",
 "f_group":  "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0456\u0445, \u0445\u0442\u043e \u043d\u0430\u043b\u0435\u0436\u0438\u0442\u044c \u0434\u043e \u0433\u0440\u0443\u043f\u0438",
 "f_danger": "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0435, \u0449\u043e \u043d\u0435\u0431\u0435\u0437\u043f\u0435\u0447\u043d\u0435",
 "f_mat":    "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0435, \u0449\u043e \u0437\u0440\u043e\u0431\u043b\u0435\u043d\u043e \u0437 \u0446\u044c\u043e\u0433\u043e \u043c\u0430\u0442\u0435\u0440\u0456\u0430\u043b\u0443",
 "f_fig":    "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0456 \u0442\u0430\u043a\u0456 \u0444\u0456\u0433\u0443\u0440\u0438",
 "f_num":    "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0456 \u0447\u0438\u0441\u043b\u0430, \u0431\u0456\u043b\u044c\u0448\u0456 \u0437\u0430 \u0446\u0435",
 "f_syl":    "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0441\u043b\u043e\u0432\u0430, \u0443 \u044f\u043a\u0438\u0445 \u0441\u0442\u0456\u043b\u044c\u043a\u0438 \u0447\u0430\u0441\u0442\u0438\u043d",
 "f_grp":    "\u0417\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456 \u0432\u0441\u0435, \u0449\u043e \u043d\u0430\u043b\u0435\u0436\u0438\u0442\u044c \u0434\u043e \u0433\u0440\u0443\u043f\u0438",
}
# назва літери так, як її каже вчитель 1 класу
LET = {
 'a':'\u0430','o':'\u043e','u':'\u0443','y':'\u0438','i':'\u0456','e':'\u0435','ye':'\u0454',
 'yu':'\u044e','ya':'\u044f','yi':'\u0457','j':'\u0439\u043e\u0442',
 'soft':'\u0437\u043d\u0430\u043a \u043c\u2019\u044f\u043a\u0448\u0435\u043d\u043d\u044f',
 'm':'\u0435\u043c','en':'\u0435\u043d','el':'\u0435\u043b','es':'\u0435\u0441','ka':'\u043a\u0430',
 'be':'\u0431\u0435','ve':'\u0432\u0435','he':'\u0433\u0435','ge':'\u0491\u0435','de':'\u0434\u0435',
 'zhe':'\u0436\u0435','ze':'\u0437\u0435','pe':'\u043f\u0435','er':'\u0435\u0440','te':'\u0442\u0435',
 'ef':'\u0435\u0444','ha':'\u0445\u0430','tse':'\u0446\u0435','che':'\u0447\u0435','sha':'\u0448\u0430',
 'shcha':'\u0449\u0430',
}
IMG = {
 'sc_forest': 'a simple empty forest clearing with sky above and grass below, '
              'nothing in the middle, plenty of empty space',
 'sc_room':   'a simple empty child room with a wall above and a wooden floor below, '
              'nothing in the middle, plenty of empty space',
 'sc_sea':    'a simple empty sea view with sky above and calm water below, '
              'nothing in the middle, plenty of empty space',
}

man = json.load(io.open(MAN, encoding='utf-8'))
voc, img = man['voice']['items'], man['image']['items']
av = []
for k, t in VOICE.items():
    if k not in voc:
        voc[k] = [t, 'phrase']; av.append(k)
for lat, nm in LET.items():
    k = 'let_' + lat
    if k not in voc:
        voc[k] = [nm, 'word']; av.append(k)
ai = []
for k, t in IMG.items():
    if k not in img:
        img[k] = t; ai.append(k)
# Сцени малюються іншим промптом, ніж предмети: це тло, а не вирізаний
# об'єкт. Беремо той самий стиль, що для шпалер (`style_bg`).
man['image'].setdefault('_scene_note',
    '\u0421\u0446\u0435\u043d\u0438 sc_* \u2014 \u0442\u043b\u043e \u0434\u043b\u044f \u00ab\u0437\u043d\u0430\u0439\u0434\u0438 \u043d\u0430 \u043a\u0430\u0440\u0442\u0438\u043d\u0456\u00bb. \u0407\u0445 \u041d\u0415 \u043f\u0440\u043e\u0433\u0430\u043d\u044f\u0442\u0438 \u0447\u0435\u0440\u0435\u0437 cut_bg.py: '
    '\u0442\u0430\u043c \u0432\u0438\u0440\u0456\u0437\u0430\u0454\u0442\u044c\u0441\u044f \u0442\u043b\u043e, \u0430 \u0442\u0443\u0442 \u0432\u043e\u043d\u043e \u0456 \u0454 \u043a\u0430\u0440\u0442\u0438\u043d\u043a\u043e\u044e \u2014 \u0442\u0430\u043a \u0441\u0430\u043c\u043e, \u044f\u043a bg_*.')
io.open(MAN + '.tmp', 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))
os.replace(MAN + '.tmp', MAN)
print('\u043a\u043b\u0456\u043f\u0456\u0432 +%d (\u0443\u0441\u044c\u043e\u0433\u043e %d), \u043a\u0430\u0440\u0442\u0438\u043d\u043e\u043a +%d (\u0443\u0441\u044c\u043e\u0433\u043e %d)'
      % (len(av), len(voc), len(ai), len(img)))
