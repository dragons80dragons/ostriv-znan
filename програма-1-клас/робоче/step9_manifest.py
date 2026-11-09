# -*- coding: utf-8 -*-
"""Крок 9. Доповнює G:\\ostriv-znan\\tools\\manifest.json під повний 1 клас.

manifest.json — єдине джерело правди для генерації ресурсів; gen_images.py,
gen_voice.py і gen_island_music.py читають саме його. Тому новий вміст треба
покласти туди, а не в окремий список.

Що додається:
  image.items  — картинка-іконка для кожного нового острова (i_*) і картинка
                 для кожного нового слова (w_*);
  voice.items  — кожна пара [id, 'текст'] з нових генераторів.
Ідемпотентний: наявні записи не чіпає, пише резервну копію перед заміною.
"""
import json, io, os, re, shutil, datetime

TOOLS = r'G:\ostriv-znan\tools'
W = r'G:\ostriv-znan\програма-1-клас\робоче'
MAN = os.path.join(TOOLS, 'manifest.json')
SRC = ['\u0432\u0441\u0442\u0430\u0432\u043a\u0430_1_\u043f\u0440\u043e\u043f\u0438\u0441\u0438.js',
       '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_2_\u0432\u043c\u0456\u0441\u0442.js',
       '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_3_\u043e\u0441\u0442\u0440\u043e\u0432\u0438.js']
MAP = '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_4_\u043a\u0430\u0440\u0442\u0430.js'

# ---------- картинки островів. Промпт іде в style_island:
# «...one small tropical island with {object}...», тому тут лише предмет.
ISLANDS = {
  # Море Чисел
  'i_num20':   'twenty small round stones laid in two rows of ten and a palm tree',
  'i_num100':  'ten stacks of ten coins and a palm tree',
  'i_add100':  'a big wooden plus sign and a big wooden minus sign and a palm tree',
  'i_measure': 'a long wooden ruler, a balance scale and a glass jug, and a palm tree',
  'i_task':    'an open notebook with a pencil and a thinking lightbulb, and a palm tree',
  'i_data':    'a wooden board with a simple two column table drawn on it and a palm tree',
  'i_lines':   'a straight line, a zigzag line and a circle drawn in the sand, and a palm tree',
  # Море Мови
  'i_stress':  'a drum with one big beater raised above it and a palm tree',
  'i_sent':    'a wooden sign with a full stop, a question mark and an exclamation mark, and a palm tree',
  'i_abc':     'wooden letter tiles lined up in a row and a palm tree',
  'i_mean':    'two speech bubbles facing each other and a palm tree',
  'i_group':   'three wicker baskets with different things sorted into them and a palm tree',
  'i_quest':   'a big wooden question mark and a palm tree',
  'i_text':    'an open storybook with a bookmark and a palm tree',
  # Море Світу
  'i_body':    'a friendly cartoon face with big eye, ear and nose, and a palm tree',
  'i_safe':    'a traffic light and a small first aid kit and a palm tree',
  'i_signs':   'three warning road signs on posts and a palm tree',
  'i_country': 'a blue and yellow flag on a pole, a sunflower and a palm tree',
  'i_jobs':    'a doctor hat, a chef hat and a builder helmet on a shelf, and a palm tree',
  'i_alive':   'a green sprout in soil next to a grey stone, and a palm tree',
  'i_animals': 'a butterfly, a fish and a small bird together, and a palm tree',
  'i_stuff':   'a wooden plank, a glass jar and a ball of yarn, and a palm tree',
  'i_invent':  'an old wooden wheel and a glowing lightbulb and a palm tree',
  # Море Уваги
  'i_info':    'a big eye, a big ear and a big hand around a palm tree',
  'i_ask':     'three speech bubbles with question marks and a palm tree',
  'i_code':    'a green circle and a red circle and the digits zero and one, and a palm tree',
  'i_true':    'a balance scale with a tick on one side and a cross on the other, and a palm tree',
  'i_plan':    'four numbered wooden stepping stones in a row and a palm tree',
  'i_card':    'a wooden instruction card with small pictures on it, scissors and glue, and a palm tree',
  # Море Мистецтва
  'i_rhythm':  'a tambourine and two clapping hands and a palm tree',
  'i_tempo':   'a metronome and a palm tree',
  'i_instr':   'a drum, a triangle and a wooden flute together, and a palm tree',
  'i_notes':   'a music staff with a treble clef and two notes, and a palm tree',
  'i_ornament':'a painted Ukrainian easter egg and a paper cut snowflake, and a palm tree',
}

# ---------- картинки нових слів. Стиль спільний (image.style), тут лише
# предмет. Формулювання те саме, що в наявних: один предмет, нічого навколо.
WORDPIC = {
  'w_avtobus': 'yellow school bus seen from the side',
  'w_hryb': 'one mushroom with a red cap and white spots',
  'w_gava': 'one black crow standing',
  'w_eskimo': 'one ice cream cone with one scoop',
  'w_yenot': 'one raccoon standing',
  'w_zaiets': 'one grey hare sitting',
  'w_indyk': 'one turkey bird standing',
  'w_yizhak': 'one hedgehog standing',
  'w_yohurt': 'one glass of milk',
  'w_nizh': 'one kitchen knife',
  'w_olivets': 'one yellow pencil with a sharpened tip',
  'w_tort': 'one round birthday cake with candles',
  'w_udav': 'one green snake coiled',
  'w_farba': 'one paint palette with colourful paints and a brush',
  'w_tsybulia': 'one onion bulb',
  'w_cherepakha': 'one tortoise standing',
  'w_shapka': 'one knitted winter hat',
  'w_shchuka': 'one pike fish swimming',
  'w_yula': 'one spinning top toy',
  'w_dim': 'one small house with a red roof',
  'w_vikno': 'one window with a wooden frame',
  'w_kvitka': 'one daisy flower with a stem',
  'w_more': 'one blue wave of the sea',
  'w_ptakh': 'one small bird standing',
  'w_raketa': 'one rocket flying up',
  'w_sumka': 'one school backpack',
  'w_litak': 'one aeroplane flying',
  'w_bananu': 'one yellow banana',
  'w_zholud': 'one acorn with its cap',
  'w_khmara': 'one white fluffy cloud',
}

PAIR = re.compile(r"\[\s*'([a-z][a-zA-Z0-9_]{1,24})'\s*,\s*'([^'\\]{2,120})'\s*\]")
# Таблиці даних тримають озвучку третім елементом: ['eye','очі','se_eye','👁️',…]
TRIPLE = re.compile(r"\[\s*'([a-z][a-zA-Z0-9_]*)'\s*,\s*'([^'\\]{2,80})'\s*,\s*'([a-z][a-zA-Z0-9_]+)'")
# І зворотний порядок: ['комаха','an_komakha']
REVPAIR = re.compile(r"\[\s*'([^'\\]*[\u0400-\u04ff][^'\\]*)'\s*,\s*'([a-z][a-zA-Z0-9_]+)'\s*\]")
SAY1 = re.compile(r"say1\(\s*'[^']*'\s*,\s*'([^'\\]{1,80})'\s*,\s*'([a-z][a-zA-Z0-9_]{1,24})'\s*\)")
CYR = re.compile(r'[\u0400-\u04ff]')


# Назва острова й моря озвучується окремим кліпом: на карті краб читає її
# вголос. У вставці вони лежать не парою, а полями vo: і name:.
NAMED = re.compile(r"vo:'([a-z][a-zA-Z0-9_]+)'[^}]*?name:'([^']+)'")


def collect_voice():
    out = {}
    for name in SRC:
        t = io.open(os.path.join(W, name), encoding='utf-8').read()
        for vid, txt in PAIR.findall(t):
            if CYR.search(txt) and '${' not in txt:
                out.setdefault(vid, txt)
        for txt, vid in SAY1.findall(t):
            if CYR.search(txt) and '${' not in txt:
                out.setdefault(vid, txt)
        for _, txt, vid in TRIPLE.findall(t):
            if CYR.search(txt) and '${' not in txt:
                out.setdefault(vid, txt)
        for txt, vid in REVPAIR.findall(t):
            if CYR.search(txt) and '${' not in txt:
                out.setdefault(vid, txt)
    t = io.open(os.path.join(W, MAP), encoding='utf-8').read()
    for vid, txt in NAMED.findall(t):
        if CYR.search(txt):
            out.setdefault(vid, txt)
    return out


def main():
    man = json.load(io.open(MAN, encoding='utf-8'))
    shutil.copy2(MAN, MAN + '.bak-' + datetime.datetime.now().strftime('%Y%m%d-%H%M'))

    img = man['image']['items']
    added_i = [k for k in list(ISLANDS) + list(WORDPIC) if k not in img]
    img.update({k: v for k, v in ISLANDS.items() if k not in img})
    img.update({k: v for k, v in WORDPIC.items() if k not in img})

    voc = man['voice']['items']
    found = collect_voice()
    # назви островів і морів озвучуються окремо — беремо з LESSONS нижче
    added_v = []
    for vid, txt in sorted(found.items()):
        if vid in voc:
            continue
        kind = 'phrase' if len(txt.split()) > 2 or txt.endswith(('?', '!', '.')) else 'word'
        voc[vid] = [txt, kind]
        added_v.append(vid)

    tmp = MAN + '.tmp'
    io.open(tmp, 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))
    os.replace(tmp, MAN)
    io.open(os.path.join(W, '_\u0434\u043e\u0434\u0430\u043d\u043e_\u0432_manifest.txt'), 'w', encoding='utf-8').write(
        'картинок: %d\n%s\n\nголосу: %d\n%s\n'
        % (len(added_i), '\n'.join('  %s = %s' % (k, img[k]) for k in added_i),
           len(added_v), '\n'.join('  %s = %s' % (k, voc[k][0]) for k in added_v)))
    print('картинок додано: %d, голосу: %d, усього в manifest: %d / %d'
          % (len(added_i), len(added_v), len(img), len(voc)))


main()
