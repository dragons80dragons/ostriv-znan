# -*- coding: utf-8 -*-
"""Крок 4. Витягає з букварів 1 класу порядок уведення літер.

Як розпізнається нова літера. Сторінка, на якій буквар уводить літеру,
майже завжди має окремий рядок із парою великої й малої тієї самої літери:
«Уу», «Мм», «А а», «Бб». Це надійніше за підпис «Звук [а]. Букви А а»,
бо той є лише в частині ліній. Обидва шаблони шукаються разом.

Три пастки, через які наївний пошук дає хибну послідовність:
1. **Зміст і таблиця алфавіту** дають ті самі пари, але в алфавітному
   порядку. Тому пробіги, що йдуть строго за алфавітом, відкидаються.
2. **Буквар лежить двома частинами** в окремих PDF. Частини зшиваються
   за іменем файлу (ch1/ch2, chast-1/chast-2, Ch1/Ch2).
3. **Повторні згадки** літери на пізніших сторінках. Береться перша поява.

Ідемпотентний: пише `_порядок_літер.md` і `_порядок_літер.json`.
"""
import json, io, os, re, collections

B = r'G:\ostriv-znan\програма-1-клас\робоче'
TXT = os.path.join(B, 'txt')
UKR = ('\u0430\u0431\u0432\u0433\u0491\u0434\u0435\u0454\u0436\u0437\u0438'
       '\u0456\u0457\u0439\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441'
       '\u0442\u0443\u0444\u0445\u0446\u0447\u0448\u0449\u044c\u044e\u044f')
ALPHA = list(UKR)
POS = {c: i for i, c in enumerate(ALPHA)}
UP = '\u0410-\u042f\u0404\u0406\u0407\u0490'
LOW = '\u0430-\u044f\u0454\u0456\u0457\u0491'
# пара «Уу», «У у», «А  а» на окремому рядку
RE_PAIR = re.compile(r'^\s*([' + UP + r'])\s{0,3}([' + LOW + r'])\s*$')
# «букв(а|и) Б б», «буквою Ї»
RE_LET = re.compile(r'[\u0411\u0431]\u0443\u043a\u0432(?:\u0430|\u0438|\u043e\u044e|\u0443)?\s*'
                    r'[\u00ab"\u201c]?\s*([' + UP + r'])\s*([' + LOW + r'])?')
# «Звук [а]», «Звуки [д], [д']»
RE_SND = re.compile(r'[\u0417\u0437]\u0432\u0443\u043a(?:\u0438|\u0430|\u0456\u0432)?'
                    r"[^\n\[]{0,40}\[\s*([" + LOW + r"])['\u2019\u02bc]?\s*\]")
PAIRABLE = {'\u0430': '\u0410', '\u0431': '\u0411', '\u0432': '\u0412', '\u0433': '\u0413',
            '\u0491': '\u0490', '\u0434': '\u0414', '\u0435': '\u0415', '\u0454': '\u0404',
            '\u0436': '\u0416', '\u0437': '\u0417', '\u0438': '\u0418', '\u0456': '\u0406',
            '\u0457': '\u0407', '\u0439': '\u0419', '\u043a': '\u041a', '\u043b': '\u041b',
            '\u043c': '\u041c', '\u043d': '\u041d', '\u043e': '\u041e', '\u043f': '\u041f',
            '\u0440': '\u0420', '\u0441': '\u0421', '\u0442': '\u0422', '\u0443': '\u0423',
            '\u0444': '\u0424', '\u0445': '\u0425', '\u0446': '\u0426', '\u0447': '\u0427',
            '\u0448': '\u0428', '\u0449': '\u0429', '\u044c': '\u042c', '\u044e': '\u042e',
            '\u044f': '\u042f'}


HEAD_LINES = 4


def page_letters(page, pairs_only=True):
    """Літери, що вводяться на цій сторінці, в порядку появи.

    Пара («Аа») приймається лише якщо стоїть у шапці сторінки — серед перших
    кількох непорожніх рядків. Інакше в послідовність потрапляють підготовчі
    сторінки зі звуконаслідуванням («Ж — жжжж, як жук»), і буквар Іщенко
    починався з «т л р» замість справжніх «а у е о і».
    """
    found = []
    lines = [x for x in page.splitlines() if x.strip()]
    for line in lines[:HEAD_LINES]:
        m = RE_PAIR.match(line)
        if m and PAIRABLE.get(m.group(2)) == m.group(1):
            found.append(m.group(2))
    if pairs_only:
        return found
    for m in RE_LET.finditer(page):
        ch = (m.group(2) or m.group(1)).lower()
        if ch in POS:
            found.append(ch)
    for m in RE_SND.finditer(page):
        found.append(m.group(1))
    return found


def drop_alphabet_runs(seq, minrun=5):
    """Викидає пробіги строго за алфавітом — це зміст або таблиця алфавіту."""
    keep = [True] * len(seq)
    i = 0
    while i < len(seq):
        j = i + 1
        while j < len(seq) and POS[seq[j]] > POS[seq[j - 1]]:
            j += 1
        if j - i >= minrun:
            for k in range(i, j):
                keep[k] = False
        i = j
    return [c for c, k in zip(seq, keep) if k]


def first_appearance(seq):
    out, seen = [], set()
    for c in seq:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


PART = re.compile(r'(?:ch|chast|\u0447\u0430\u0441\u0442)[\W_]*([12])', re.I)


def line_key(path):
    """Ключ авторської лінії: шлях без позначки частини."""
    base = os.path.basename(path)
    base = PART.sub('', base)
    base = re.sub(r'[\W_]+', '', base).lower()
    return base


def part_no(path):
    m = PART.search(os.path.basename(path))
    return int(m.group(1)) if m else 1


def main():
    idx = json.load(io.open(os.path.join(B, 'index1.json'), encoding='utf-8'))
    cand = []
    for r in idx:
        if r.get('status') != 'raw' or not r.get('txt'):
            continue
        p = r['path'].lower()
        if not ('\u0431\u0443\u043a\u0432\u0430\u0440' in p or 'bukvar' in p or 'azbuka' in p):
            continue
        if 'rus' in p or 'polska' in p or 'rum' in p:   # не українські лінії
            continue
        t = io.open(os.path.join(TXT, r['txt']), encoding='utf-8').read()
        pages = t.split('\f')
        cand.append({'path': r['path'], 'pages': r.get('pages'),
                     'strict': [c for p in pages for c in page_letters(p, True)],
                     'loose': [c for p in pages for c in page_letters(p, False)],
                     'authors': r.get('authors') or [],
                     'line': line_key(r['path']), 'part': part_no(r['path'])})
    # зшивання частин однієї лінії
    groups = collections.defaultdict(list)
    for c in cand:
        groups[c['line']].append(c)
    rows = []
    for k, g in groups.items():
        g.sort(key=lambda x: x['part'])
        au = []
        for c in g:
            for x in c['authors']:
                if x not in au:
                    au.append(x)
        rows.append({
            'files': [c['path'] for c in g],
            'authors': au,
            'pages': sum(c['pages'] or 0 for c in g),
            'strict': first_appearance(drop_alphabet_runs(
                [x for c in g for x in c['strict']])),
            'loose': first_appearance(drop_alphabet_runs(
                [x for c in g for x in c['loose']])),
        })
    rows.sort(key=lambda r: -len(r['loose']))
    L = []
    a = L.append
    a('# Порядок уведення літер у букварях 1 класу\n')
    a('Витягнуто `step4_bukvari.py`. Частини одного буквара зшито за іменем файлу,')
    a('автори — з титулів PDF (`step5_avtory.py`). Пробіги, що йдуть строго за')
    a('алфавітом (зміст, таблиця алфавіту в кінці), відкинуто.\n')
    a('**Два проходи, бо жоден не є істиною окремо.**\n')
    a('- **строгий** — пара великої й малої літери («Аа», «У у») у шапці сторінки.')
    a('  Дає надійний ПОЧАТОК послідовності, але губить літери, які буквар уводить')
    a('  усередині тексту, без окремої шапки.')
    a('- **вільний** — додає підписи «Звук [а]», «букви А а» будь-де на сторінці.')
    a('  Покриття повніше, але в нього потрапляють підготовчі сторінки зі')
    a('  звуконаслідуванням («Ж — жжж, як жук») і згадки літер у вправах.\n')
    a('Перевірено очима: у Іщенка–Логачевської строгий прохід дає правильний')
    a('початок «а у е о і», а вільний помилково починав із «т л р» — це були')
    a('підготовчі сторінки про немовні звуки. У Борщевської навпаки: строгий')
    a('прохід знаходить 19 літер, бо решту введено в суцільному тексті.')
    a('Тому для висновків беремо початок зі строгого проходу, а склад і хвіст —')
    a('із вільного, і спірні місця дивимо очима.\n')
    a('| Автори з титулу | Строгий | Вільний | Стор. |')
    a('|---|---:|---:|---:|')
    for r in rows:
        a('| %s | %d | %d | %d |' % (', '.join(r['authors']) or '—',
                                     len(r['strict']), len(r['loose']), r['pages']))
    a('')
    for r in rows:
        if not r['loose'] and not r['strict']:
            continue
        a('## %s' % (', '.join(r['authors']) or os.path.basename(r['files'][0])))
        a('')
        for f in r['files']:
            a('- `%s`' % os.path.basename(f))
        a('- сторінок: %d' % r['pages'])
        a('- **строгий** (%d з 33): %s' % (len(r['strict']), ' '.join(r['strict']) or '—'))
        a('- **вільний** (%d з 33): %s' % (len(r['loose']), ' '.join(r['loose']) or '—'))
        a('')
    io.open(os.path.join(B, '_порядок_літер.md'), 'w', encoding='utf-8').write('\n'.join(L))
    io.open(os.path.join(B, '_порядок_літер.json'), 'w', encoding='utf-8').write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    for r in rows:
        print('строго %2d / вільно %2d | %s' % (
            len(r['strict']), len(r['loose']),
            (', '.join(r['authors']) or os.path.basename(r['files'][0]))[:60]))


main()
