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
# Шпалери лежать окремо й не в PNG: фото 1024 px важило б більше за всю
# решту гри, тому pack_bg.py зводить їх у JPEG (assets/bg).
BG = os.path.join(PROJ, 'assets', 'bg')
# Краб у грі — не картинка, а порізаний на частини малюнок (rig_krab.py).
KRAB = os.path.join(PROJ, 'assets', 'krab')
# Десять намальованих крабів — чернетки, з яких вибирали одного. У грі
# не лишилося жодного цілою картинкою, тому гра їх і не просить; у
# маніфесті вони потрібні, щоб було чим перегенерувати.
DRAFTS = {'g_krab'} | {'kr%02d' % k for k in range(1, 11)}


def ids_from_html(src):
    """Що саме просить гра.

    Шукати виклики pic(...) марно: гра передає туди змінні — pic(f[0],f[1]).
    Самі id лежать у масивах даних: ['o_apple','🍎'], ['w_kit','🐱','кіт','К'],
    ['s_red','🔴']. Числа n0..n10 узагалі збираються в коді ('n'+k).
    """
    imgs = set(re.findall(r"\['((?:i|o|w|s|we|se)_[a-z0-9_]+)'\s*,", src))
    imgs |= set(re.findall(r"img:\s*'([a-z0-9_]+)'", src))
    # Погода й пори року лежать не першими елементами (одяг — шостим),
    # а краб узагалі приходить лише як pic('g_krab', '🦀'). Фрази краба
    # теж починаються на g_, тому сюди їх пускати не можна.
    imgs |= set(re.findall(r"'((?:we|se|gx)_[a-z0-9_]+)'", src))
    imgs |= set(re.findall(r"pic\('([a-z0-9_]+)'", src))
    voice = set(re.findall(r"\['((?:p|ok|f|st|w|g)_[a-z0-9_]+)'\s*,", src))
    # Назви островів, морів і рівнів стоять у полі vo: острова.
    voice |= set(re.findall(r"vo:\s*'([a-z0-9_]+)'", src))
    # Відповіді словами (a_above, a_sunny…) озвучує кнопка з 🔊.
    voice |= set(re.findall(r"'(a_[a-z0-9_]+)'", src))
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
        # NUM тепер до дванадцяти: на годиннику є одинадцята й дванадцята.
        voice |= {'n%d' % k for k in range(13)}
    return imgs, voice


def krab_parts():
    """Які частини краба мусять лежати: список бере сам риг.

    parts.json пише rig_krab.py, і там же лежать координати, якими гра
    складає краба. Якщо частини не збігаються зі списком — гра збере
    краба з дірками, і це видно лише оком, тому звіряємо списком.
    """
    try:
        with open(os.path.join(KRAB, 'parts.json'), encoding='utf-8') as f:
            return set(json.load(f)['parts']) | {'body'}
    except Exception:                                             # noqa: BLE001
        return {'body'}


def lesson_ids(src):
    """Id уроків — із переліку морів (ls: ['math','num', …])."""
    out = set()
    for block in re.findall(r"ls:\s*\[([^\]]*)\]", src):
        out |= set(re.findall(r"'([a-z0-9_]+)'", block))
    return out


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
    man_img = set(man['image']['items']) - DRAFTS
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

    # Шпалери гра просить не як id, а рядком у scene() — звідси й беремо.
    scenes = {'bg_' + n for n in re.findall(r'scene\("([a-z]+)"\)', src)}
    bgs = {i for i in man_img if i.startswith('bg_')} | scenes
    html_img -= bgs
    man_img -= bgs

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
    bad += report('Шпалери assets/bg', bgs, BG, '.jpg')
    bad += report('Голос assets/voice', html_voice | man_voice, VOICE, '.wav')
    bad += report('Частини краба assets/krab', krab_parts(), KRAB, '.png')

    theme = os.path.join(MUSIC, man['music']['file'])
    if os.path.exists(theme) and os.path.getsize(theme) > 200:
        secs = wav_seconds(theme)
        print('\nМузика: %s%s' % (man['music']['file'],
                                  ' — %.1f с' % secs if secs else ''))
    else:
        print('\nМузика: НЕМАЄ %s (кнопка «Музика» в грі не з’явиться)'
              % man['music']['file'])
        bad.append('theme')

    # Мелодія кожного острова. Без неї гра не падає — просто грає тишу,
    # тому це попередження, а не брак: 18 треків генеруються пів години.
    tunes = lesson_ids(src)
    lack = sorted(t for t in tunes
                  if not os.path.exists(os.path.join(MUSIC, t + '.mp3')))
    print('Мелодії островів: %d з %d' % (len(tunes) - len(lack), len(tunes)))
    if lack:
        print('  НЕМАЄ (%d): %s' % (len(lack), ', '.join(lack)))
        print('  зробити: python gen_island_music.py --only %s' % ','.join(lack))

    short = [f for f in sorted(os.listdir(VOICE)) if f.endswith('.wav')
             and (wav_seconds(os.path.join(VOICE, f)) or 1) < 0.2] \
        if os.path.isdir(VOICE) else []
    if short:
        print('\nПідозріло короткі кліпи (<0,2 с): %s' % ', '.join(short))

    print('\n%s' % ('ВСЕ НА МІСЦІ' if not bad else 'БРАКУЄ %d файлів' % len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
