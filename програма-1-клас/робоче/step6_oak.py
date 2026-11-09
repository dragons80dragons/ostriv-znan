# -*- coding: utf-8 -*-
"""Крок 6. Розбирає відкриті дані Oak National Academy (KS1 = 5–7 р., ~1–2 клас)
на ідеї завдань.

Структура файлів (встановлено розбором, не з документації):
- `розділи.json`  — список по роках: {yearSlug, yearTitle, units:[{unitSlug, unitTitle}]}
- `уроки.json`    — список по розділах: {unitSlug, unitTitle, lessons:[{lessonSlug, lessonTitle}]}
  Року тут немає — рік беремо через unitSlug із «розділи.json».
- `питання тестів.json` — по уроках: {lessonSlug, lessonTitle, starterQuiz:[...], exitQuiz:[...]}
  Кожне питання: {question, questionType, questionImage, answers:[{type, content, distractor}]}
  Тобто **видно, що правильне, а що відволікач** — саме це й потрібно для гри.

Ідемпотентний: пише `_oak_year1.md`.
"""
import json, io, os, collections

ROOT = ('G:\\' + '\u041e\u0441\u0442\u0440\u0456\u0432 \u0417\u043d\u0430\u043d\u044c \u2014 \u041c\u0430\u0442\u0435\u0440\u0456\u0430\u043b\u0438'
        + '\\02_\u0417\u0430\u043a\u043e\u0440\u0434\u043e\u043d\u043d\u0456'
        + '\\\u0410\u043d\u0433\u043b\u0456\u044f \u2014 National Curriculum'
        + '\\Oak National Academy \u2014 \u0432\u0456\u0434\u043a\u0440\u0438\u0442\u0456 \u0434\u0430\u043d\u0456 (OGL)'
        + '\\KS1 (5-7 \u0440., \u22481-2 \u043a\u043b\u0430\u0441)')
B = r'G:\ostriv-znan\програма-1-клас\робоче'
F_UNITS = '\u0440\u043e\u0437\u0434\u0456\u043b\u0438.json'
F_LESS = '\u0443\u0440\u043e\u043a\u0438.json'
F_Q = '\u043f\u0438\u0442\u0430\u043d\u043d\u044f \u0442\u0435\u0441\u0442\u0456\u0432.json'


def load(p):
    if not os.path.exists(p):
        return []
    try:
        j = json.load(io.open(p, encoding='utf-8'))
        return j if isinstance(j, list) else []
    except Exception:
        return []


def main():
    subjects = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    data = {}
    for s in subjects:
        d = os.path.join(ROOT, s)
        units_by_year = {}
        for rec in load(os.path.join(d, F_UNITS)):
            units_by_year[rec.get('yearSlug')] = rec.get('units') or []
        lessons_by_unit = {}
        for rec in load(os.path.join(d, F_LESS)):
            lessons_by_unit[rec.get('unitSlug')] = rec.get('lessons') or []
        q_by_lesson = {}
        for rec in load(os.path.join(d, F_Q)):
            q_by_lesson[rec.get('lessonSlug')] = rec
        data[s] = (units_by_year, lessons_by_unit, q_by_lesson)

    L = []
    a = L.append
    a('# Oak National Academy, Year 1 — на ідеї завдань\n')
    a('Ліцензія OGL: матеріал можна читати й переробляти. Англійською, тому')
    a('цінність не в текстах, а в **типах завдань і порядку уроків**.')
    a('Шлях: `02_Закордонні\\Англія — National Curriculum\\Oak ... (OGL)\\KS1 ...`\n')
    a('У кожному питанні видно не лише правильну відповідь, а й **відволікачі**')
    a('(`distractor: true`) — тобто типові дитячі помилки, вже відібрані.')
    a('Для гри це готовий матеріал на хибні варіанти у трьох рівнях складності.\n')
    a('## Скільки чого є на Year 1\n')
    a('| Предмет Oak | Розділів | Уроків | Уроків із питаннями | Питань |')
    a('|---|---:|---:|---:|---:|')
    tot_u = tot_l = tot_q = 0
    for s in subjects:
        uby, lby, qby = data[s]
        units = uby.get('year-1') or []
        nl = nq = nlq = 0
        for u in units:
            ls = lby.get(u.get('unitSlug')) or []
            nl += len(ls)
            for x in ls:
                r = qby.get(x.get('lessonSlug'))
                if r:
                    k = len(r.get('starterQuiz') or []) + len(r.get('exitQuiz') or [])
                    if k:
                        nlq += 1
                        nq += k
        a('| %s | %d | %d | %d | %d |' % (s, len(units), nl, nlq, nq))
        tot_u += len(units); tot_l += nl; tot_q += nq
    a('| **усього** | **%d** | **%d** | | **%d** |' % (tot_u, tot_l, tot_q))
    a('')
    types = collections.Counter()
    for s in subjects:
        uby, lby, qby = data[s]
        for r in qby.values():
            for q in (r.get('starterQuiz') or []) + (r.get('exitQuiz') or []):
                types[str(q.get('questionType'))] += 1
    a('## Типи питань (за всім KS1)\n')
    a('| Тип | Питань | Що це дає грі |')
    a('|---|---:|---|')
    HINT = {
        'multiple-choice': 'вибір із варіантів + готові відволікачі',
        'match': 'з\u2019єднати пари — як у завданнях на склади',
        'order': 'упорядкувати — для послідовностей, лічби, подій',
        'short-answer': 'ввести відповідь — для прописів і чисел',
        'explanatory-text': 'пояснення вчителя, не завдання',
    }
    for k, v in types.most_common():
        a('| `%s` | %d | %s |' % (k, v, HINT.get(k, '—')))
    a('')
    a('## Розділи й уроки Year 1 по предметах\n')
    for s in subjects:
        uby, lby, qby = data[s]
        units = uby.get('year-1') or []
        if not units:
            continue
        a('### %s\n' % s)
        for i, u in enumerate(units, 1):
            ls = lby.get(u.get('unitSlug')) or []
            a('**%d. %s** — уроків: %d' % (i, u.get('unitTitle'), len(ls)))
            a('')
            for x in ls:
                r = qby.get(x.get('lessonSlug')) or {}
                k = len(r.get('starterQuiz') or []) + len(r.get('exitQuiz') or [])
                a('   - %s%s' % (x.get('lessonTitle'), (' — питань: %d' % k) if k else ''))
            a('')
    io.open(os.path.join(B, '_oak_year1.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('предметів %d, розділів Y1 %d, уроків %d, питань %d' % (len(subjects), tot_u, tot_l, tot_q))


main()
