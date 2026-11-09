# -*- coding: utf-8 -*-
"""Крок 12. Дописує в manifest склади (sy_*) і слова для читання (wd_*).

Їх не видно простим пошуком по вставках: у грі вони не записані парою
[id, 'текст'], а збираються з масивів SYLL і WORDS_READ функціями syId і
wdId. Тому рахуємо id тими самими правилами, що й гра — інакше кліп
згенерується під іншим іменем і ніколи не знайдеться.
Ідемпотентний.
"""
import io, json, os

MAN = r'G:\ostriv-znan\tools\manifest.json'
CMAP = {'\u043c':'m','\u043b':'l','\u0441':'s','\u043a':'k','\u043d':'n','\u0440':'r','\u0442':'t',
        '\u0434':'d','\u043f':'p','\u0432':'v','\u0431':'b','\u0433':'h','\u0437':'z'}
VMAP = {'\u0430':'a','\u043e':'o','\u0443':'u','\u0438':'y','\u0456':'i','\u0435':'e'}
SYLL = ('\u043c\u0430 \u043c\u043e \u043c\u0443 \u043b\u0430 \u043b\u043e \u043b\u0443 \u0441\u0430 \u0441\u043e \u0441\u0443 '
        '\u043a\u0430 \u043a\u043e \u043a\u0443 \u043d\u0430 \u043d\u043e \u043d\u0443 '
        '\u0440\u0430 \u0440\u043e \u0440\u0443 \u0442\u0430 \u0442\u043e \u0442\u0443 \u0434\u0430 \u0434\u043e \u0434\u0443 '
        '\u043f\u0430 \u043f\u043e \u043f\u0443 \u0432\u0430 \u0432\u043e \u0432\u0443 \u0431\u0430 \u0431\u043e \u0431\u0443 '
        '\u0433\u0430 \u0433\u043e \u0433\u0443 \u0437\u0430 \u0437\u043e \u0437\u0443').split()
WORDS_READ = ('\u043c\u0430\u043c\u0430 \u043b\u0430\u043c\u0430 \u043c\u0443\u043a\u0430 \u043a\u043e\u043b\u043e '
              '\u043c\u043e\u043b\u043e\u043a\u043e \u043b\u0443\u043d\u0430 \u043a\u043e\u0441\u0430 \u043b\u0430\u043f\u0430 '
              '\u0440\u0443\u043a\u0430 \u0432\u043e\u0434\u0430 \u0434\u043e\u0440\u043e\u0433\u0430 \u0433\u043e\u0440\u0430 '
              '\u043a\u043e\u0437\u0430 \u0442\u0430\u0442\u043e \u043f\u043e\u0440\u0430 \u0440\u0430\u043c\u0430 '
              '\u0433\u0443\u0431\u0430 \u0432\u0430\u0442\u0430').split()
# Слова, які гра показує картинкою й називає голосом (Острів Букв, Звуків)
NEWWORDS = {
 'w_avtobus':'\u0430\u0432\u0442\u043e\u0431\u0443\u0441','w_hryb':'\u0433\u0440\u0438\u0431','w_gava':'\u0491\u0430\u0432\u0430',
 'w_eskimo':'\u0435\u0441\u043a\u0456\u043c\u043e','w_yenot':'\u0454\u043d\u043e\u0442','w_zaiets':'\u0437\u0430\u0454\u0446\u044c',
 'w_indyk':'\u0456\u043d\u0434\u0438\u043a','w_yizhak':'\u0457\u0436\u0430\u043a','w_yohurt':'\u0439\u043e\u0433\u0443\u0440\u0442',
 'w_nizh':'\u043d\u0456\u0436','w_olivets':'\u043e\u043b\u0456\u0432\u0435\u0446\u044c','w_tort':'\u0442\u043e\u0440\u0442',
 'w_udav':'\u0443\u0434\u0430\u0432','w_farba':'\u0444\u0430\u0440\u0431\u0430','w_tsybulia':'\u0446\u0438\u0431\u0443\u043b\u044f',
 'w_cherepakha':'\u0447\u0435\u0440\u0435\u043f\u0430\u0445\u0430','w_shapka':'\u0448\u0430\u043f\u043a\u0430','w_shchuka':'\u0449\u0443\u043a\u0430',
 'w_yula':'\u044e\u043b\u0430','w_dim':'\u0434\u0456\u043c','w_vikno':'\u0432\u0456\u043a\u043d\u043e','w_kvitka':'\u043a\u0432\u0456\u0442\u043a\u0430',
 'w_more':'\u043c\u043e\u0440\u0435','w_ptakh':'\u043f\u0442\u0430\u0445','w_raketa':'\u0440\u0430\u043a\u0435\u0442\u0430','w_sumka':'\u0441\u0443\u043c\u043a\u0430',
 'w_litak':'\u043b\u0456\u0442\u0430\u043a','w_bananu':'\u0431\u0430\u043d\u0430\u043d','w_zholud':'\u0436\u043e\u043b\u0443\u0434\u044c','w_khmara':'\u0445\u043c\u0430\u0440\u0430'}

man = json.load(io.open(MAN, encoding='utf-8'))
voc = man['voice']['items']
add = []
for s in SYLL:
    vid = 'sy_' + CMAP.get(s[0], 'x') + VMAP.get(s[1], 'x')
    if vid not in voc:
        voc[vid] = [s, 'word']; add.append(vid)
for w in WORDS_READ:
    vid = 'wd_' + ''.join(CMAP.get(c) or VMAP.get(c) or '' for c in w)
    if vid not in voc:
        voc[vid] = [w, 'word']; add.append(vid)
for vid, w in NEWWORDS.items():
    if vid not in voc:
        voc[vid] = [w, 'word']; add.append(vid)
io.open(MAN + '.tmp', 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))
os.replace(MAN + '.tmp', MAN)
print('додано кліпів:', len(add), '| усього:', len(voc))
