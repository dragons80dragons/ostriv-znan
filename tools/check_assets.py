# -*- coding: utf-8 -*-
"""Перевірка, що гра справді підхоплює файли: що чого бракує.

Звіряє три списки:
  * які id просить index.html (витягує з коду);
  * які id описано в manifest.json;
  * які файли реально лежать в assets/.

Запуск:  python check_assets.py
Виходить з кодом 1, якщо чогось бракує — зручно для .cmd.
"""
import json
import os
import re
import sys
import wave

# Консоль Windows тут cp1251 — український print інакше вбиває скрипт.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
HTML = os.path.join(PROJ, 'index.html')
IMG = os.path.join(PROJ, 'assets', 'img')
VOICE = os.path.join(PROJ, 'assets', 'voice')
MUSIC = os.path.join(PROJ, 'assets', 'music')


def ids_from_html(src):
    """Що саме просить гра.

    Шукати виклики pic(...) марно: гра передає туди змінні — pic(f[0],f[1]).
    Самі id лежать у масивах даних: ['o_apple','🍎'], ['w_kit','🐱','кіт','К'],
    ['s_red','🔴']. Числа n0..n10 узагалі збираються в коді ('n'+k).
    """
    imgs = set(re.findall(r"\['((?:i|o|w|s)_[a-z0-9_]+)'\s*,", src))
    imgs |= set(re.findall(r"img:\s*'([a-z0-9_]+)'", src))
    voice = set(re.findall(r"\['((?:p|ok|f|st|w)_[a-z0-9_]+)'\s*,", src))
    # Підказки уроку письма стоять другим елементом (['А','t_a','а']) або
    # збираються в коді ('t_d'+k), тому їх ловимо окремими шаблонами.
    voice |= set(re.findall(r"'(t_[a-z0-9_]+)'", src))
    # Кольори й назви фігур стоять третім елементом (['circle','круг','sh_circle']).
    voice |= set(re.findall(r"'((?:c|sh)_[a-z]+)'", src))
    if '`or_${k+1}`' in src:      # порядкові номери збираються в коді
        voice |= {'or_%d' % k for k in range(1, 6)}
    if "'t_d'+k" in src:
        voice.discard('t_d')                 # це початок виразу, а не id
        voice |= {'t_d%d' % k for k in range(1, 6)}
    if "'n'+k" in src:
        voice |= {'n%d' % k for k in range(11)}
    return imgs, voice


def wav_seconds(path):
    try:
        with wave.open(path, 'rb') as f:
            return f.getnframes() / float(f.getframerate())
    except Exception:                                             # noqa: BLE001
        return None


def report(title, need, folder, ext):
    have, missing, empty = [], [], []
    for cid in sorted(need):
        p = os.path.join(folder, cid + ext)
        if not os.path.exists(p):
            missing.append(cid)
        elif os.path.getsize(p) < 200:
            empty.append(cid)
        else:
            have.append(cid)
    print('\n%s: %d з %d' % (title, len(have), len(need)))
    if missing:
        print('  НЕМАЄ (%d): %s' % (len(missing), ', '.join(missing)))
    if empty:
        print('  ПОРОЖНІ (%d): %s' % (len(empty), ', '.join(empty)))
    return missing + empty


def main():
    with open(HTML, encoding='utf-8') as f:
        src = f.read()
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        man = json.load(f)

    html_img, html_voice = ids_from_html(src)
    man_img = set(man['image']['items'])
    # Матрицю «фігура × колір» гра збирає рядком (`f_${фігура}_${колір}`),
    # у маніфесті вона описана списками — звідти й беремо очікувані id.
    fig = man.get('figures')
    if fig:
        matrix = {'f_%s_%s' % (s, c) for s in fig['shapes'] for c in fig['colors']}
        man_img |= matrix
        if 'f_${' in src:
            html_img |= matrix
    man_voice = set(man['voice']['items'])
    # Id складів гра збирає функцією syId() — у коді їх не видно, тому
    # беремо список із маніфесту.
    for fn, pref in (('syId', 'sy_'), ('wdId', 'wd_')):
        if fn in src:
            html_voice |= {i for i in man_voice if i.startswith(pref)}

    print('index.html просить: %d картинок, %d голосових кліпів'
          % (len(html_img), len(html_voice)))
    for name, a, b in (('картинок', html_img, man_img),
                       ('голосу', html_voice, man_voice)):
        only_html = sorted(a - b)
        only_man = sorted(b - a)
        if only_html:
            print('  УВАГА, %s немає в маніфесті: %s' % (name, ', '.join(only_html)))
        if only_man:
            print('  у маніфесті зайве (%s): %s' % (name, ', '.join(only_man)))

    bad = []
    bad += report('Картинки assets/img', html_img | man_img, IMG, '.png')
    bad += report('Голос assets/voice', html_voice | man_voice, VOICE, '.wav')

    theme = os.path.join(MUSIC, man['music']['file'])
    if os.path.exists(theme) and os.path.getsize(theme) > 200:
        secs = wav_seconds(theme)
        print('\nМузика: %s%s' % (man['music']['file'],
                                  ' — %.1f с' % secs if secs else ''))
    else:
        print('\nМузика: НЕМАЄ %s (кнопка «Музика» в грі не з’явиться)'
              % man['music']['file'])
        bad.append('theme')

    short = [f for f in sorted(os.listdir(VOICE)) if f.endswith('.wav')
             and (wav_seconds(os.path.join(VOICE, f)) or 1) < 0.2] \
        if os.path.isdir(VOICE) else []
    if short:
        print('\nПідозріло короткі кліпи (<0,2 с): %s' % ', '.join(short))

    print('\n%s' % ('ВСЕ НА МІСЦІ' if not bad else 'БРАКУЄ %d файлів' % len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
