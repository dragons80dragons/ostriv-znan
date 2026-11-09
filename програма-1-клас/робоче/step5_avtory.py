# -*- coding: utf-8 -*-
"""Крок 5. Визначає автора кожного підручника 1 класу З ТИТУЛУ PDF.

Чому не з каталогу: поле «автор» у `_каталог.csv` для підручників 1 класу
порожнє (перевірено) — каталог збирався обходом диска, а не розбором книжок.
Чому не з імені файлу: пастка брифа №6 — транслітерація прізвища в іменах
ІМЗО розходиться з титулом (Guchshina замість «Гущина»).
Тому шукаємо прізвища на перших сторінках витягнутого тексту.
"""
import json, io, os, re

B = r'G:\ostriv-znan\програма-1-клас\робоче'
TXT = os.path.join(B, 'txt')
# «Прізвище І. Б.» або «І. Б. Прізвище»
RE_A1 = re.compile(r'([\u0410-\u042f\u0404\u0406\u0407\u0490][\u0430-\u044f\u0454\u0456\u0457\u0491\u2019\'-]{2,20})\s+'
                   r'([\u0410-\u042f\u0404\u0406\u0407\u0490])\.\s*([\u0410-\u042f\u0404\u0406\u0407\u0490])\.')
RE_A2 = re.compile(r'([\u0410-\u042f\u0404\u0406\u0407\u0490])\.\s*([\u0410-\u042f\u0404\u0406\u0407\u0490])\.\s+'
                   r'([\u0410-\u042f\u0404\u0406\u0407\u0490][\u0430-\u044f\u0454\u0456\u0457\u0491\u2019\'-]{2,20})')
STOP = set('\u0423\u043a\u0440\u0430\u0457\u043d\u0430 \u0423\u043a\u0440\u0430\u0457\u043d\u0438 \u041a\u0438\u0457\u0432 \u041b\u044c\u0432\u0456\u0432 \u0413\u0435\u043d\u0435\u0437\u0430 \u0421\u0432\u0456\u0442 \u0410\u0441\u0442\u043e\u043d \u0411\u043e\u0433\u0434\u0430\u043d \u0413\u0440\u0430\u043c\u043e\u0442\u0430 \u041b\u0456\u0442\u0435\u0440\u0430 \u0420\u0430\u043d\u043e\u043a \u0428\u043a\u043e\u043b\u0430 \u041c\u0456\u043d\u0456\u0441\u0442\u0435\u0440\u0441\u0442\u0432\u043e \u0406\u043d\u0441\u0442\u0438\u0442\u0443\u0442 \u041f\u0456\u0434\u0440\u0443\u0447\u043d\u0438\u043a \u0411\u0443\u043a\u0432\u0430\u0440 \u041c\u0430\u0442\u0435\u043c\u0430\u0442\u0438\u043a\u0430 \u041c\u0438\u0441\u0442\u0435\u0446\u0442\u0432\u043e \u0427\u0430\u0441\u0442\u0438\u043d\u0430'.split())


def authors(text):
    head = '\n'.join(text.split('\f')[:4])
    found, order = {}, []
    for m in RE_A1.finditer(head):
        s = m.group(1)
        if s not in STOP and s not in found:
            found[s] = '%s %s.%s.' % (s, m.group(2), m.group(3)); order.append(s)
    for m in RE_A2.finditer(head):
        s = m.group(3)
        if s not in STOP and s not in found:
            found[s] = '%s %s.%s.' % (s, m.group(1), m.group(2)); order.append(s)
    return [found[s] for s in order[:4]]


def main():
    idx = json.load(io.open(os.path.join(B, 'index1.json'), encoding='utf-8'))
    for r in idx:
        if r.get('status') != 'raw' or not r.get('txt'):
            continue
        t = io.open(os.path.join(TXT, r['txt']), encoding='utf-8').read()
        r['authors'] = authors(t)
    p = os.path.join(B, 'index1.json')
    io.open(p + '.tmp', 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False, indent=1))
    os.replace(p + '.tmp', p)
    L = []
    a = L.append
    a('# Автори підручників 1 класу — з титулів PDF\n')
    a('Поле «автор» у `_каталог.csv` для підручників 1 класу порожнє, а')
    a('транслітерація прізвищ в іменах файлів ІМЗО розходиться з титулом')
    a('(пастка брифа №6). Тому прізвища зчитано з перших сторінок книжок.\n')
    subj = {}
    for r in idx:
        if r.get('status') == 'dup' or not r.get('txt'):
            continue
        subj.setdefault(r['subject'], []).append(r)
    for s in sorted(subj):
        a('## %s\n' % s)
        a('| Автори з титулу | Стор. | Файл |')
        a('|---|---:|---|')
        for r in sorted(subj[s], key=lambda x: x['path']):
            au = ', '.join(r.get('authors') or []) or '—'
            a('| %s | %s | `%s` |' % (au, r.get('pages') or '—', os.path.basename(r['path'])))
        a('')
    io.open(os.path.join(B, '_автори.md'), 'w', encoding='utf-8').write('\n'.join(L))
    got = sum(1 for r in idx if r.get('authors'))
    print('прізвища знайдено в %d книжках' % got)


main()
