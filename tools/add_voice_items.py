# -*- coding: utf-8 -*-
"""Доповнення маніфесту кліпами для фішок, які досі молчали.

Навіщо. У грі є два шари озвучення: завдання (що спитали) і ФІШКИ (що
намальовано). Перший був повний, другий — ні: у перетягуванні, «знайди на
картині» та складанках дитина тицяла в картинку й не чула нічого. Ще пʼять
ідентифікаторів (органи чуття) кликалися без запису — там гра підставляла
синтез Windows, а українського голосу в системі немає, тож виходила каша.

Тут лише дані. Прив'язка «що показано -> який кліп» — у вставці 10.
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.join(ROOT, 'manifest.json')

# --- назви картинок, яких не було в даних гри. Беремо дитячі, звичні
#     слова: не «келих», а «склянка»; не «матрьошка», а «лялька».
EMOJI = {
    '📄': ('em_papir', 'папір'),        '🍽️': ('em_tarilka', 'тарілка'),
    '⏰': ('em_budylnyk', 'будильник'), '💧': ('em_kraplia', 'крапля'),
    '🕳️': ('em_yama', 'яма'),          '🫖': ('em_chajnyk', 'чайник'),
    '🔥': ('em_vohon', 'вогонь'),       '🚦': ('em_svitlofor', 'світлофор'),
    '👀': ('em_ochi', 'очі'),           '🛑': ('em_stop', 'знак «стоп»'),
    '🍵': ('em_chashka', 'чашка'),      '🖼️': ('em_kartyna', 'картина'),
    '🚶': ('em_pishokhid', 'пішохід'),  '🌱': ('em_rostok', 'росток'),
    '🪑': ('em_stilets', 'стілець'),    '🥔': ('em_kartoplia', 'картопля'),
    '🛏️': ('em_lizhko', 'ліжко'),      '🥕': ('em_morkva', 'морква'),
    '👖': ('em_shtany', 'штани'),       '🔨': ('em_molotok', 'молоток'),
    '👕': ('em_futbolka', 'футболка'),  '🪚': ('em_pylka', 'пилка'),
    '🧥': ('em_kurtka', 'куртка'),      '🍐': ('em_hrushka', 'грушка'),
    '🚪': ('em_dveri', 'двері'),        '🚂': ('em_potiah', 'потяг'),
    '🪛': ('em_vykrutka', 'викрутка'),  '🥄': ('em_lozhka', 'ложка'),
    '🔌': ('em_rozetka', 'розетка'),    '🧴': ('em_pliashka', 'пляшка'),
    '📗': ('em_knyzhka', 'книжка'),     '🧸': ('em_vedmedyk', 'ведмедик'),
    '💊': ('em_tabletky', 'таблетки'),  '⚽': ('em_miach', "м'яч"),
    '⛰️': ('em_hora', 'гора'),          '🪨': ('em_kamin', 'камінь'),
    '🌸': ('em_kvitka', 'квітка'),      '🪴': ('em_vazon', 'вазон'),
    '🍃': ('em_lystok', 'листок'),      '🌿': ('em_steblo', 'стебло'),
    '🦋': ('em_metelyk', 'метелик'),    '🐶': ('em_pesyk', 'песик'),
    '🐜': ('em_murashka', 'мурашка'),   '🐔': ('em_kurka', 'курка'),
    '🐄': ('em_korova', 'корова'),      '🩴': ('em_kaptsi', 'капці'),
    '🪣': ('em_vidro', 'відро'),        '🔍': ('em_lupa', 'лупа'),
    '📰': ('em_hazeta', 'газета'),      '🧃': ('em_sik', 'сік'),
    '🧣': ('em_sharf', 'шарф'),         '🧦': ('em_shkarpetky', 'шкарпетки'),
    '🔑': ('em_kliuch', 'ключ'),        '🍷': ('em_sklianka', 'склянка'),
    '🫙': ('em_banka', 'банка'),        '🗒️': ('em_bloknot', 'блокнот'),
    '🪆': ('em_lialka', 'лялька'),
}

# --- одяг за погодою: картинки вже намальовані, голосу не було
WEAR = {
    'we_jacket':   ('em_kurtka', 'куртка'),
    'we_panama':   ('em_panamka', 'панамка'),
    'we_scarf':    ('em_sharf', 'шарф'),
    'we_umbrella': ('em_parasolka', 'парасолька'),
}

# --- слова з речень, яких не було серед записаних
WORDS = {
    'ws_vysoko': 'високо', 'ws_harna': 'гарна', 'ws_zoshyt': 'зошит',
    'ws_kanikuly': 'канікули', 'ws_knyzhku': 'книжку', 'ws_letyt': 'летить',
    'ws_mij': 'мій', 'ws_peche': 'пече', 'ws_pyrih': 'пиріг',
    'ws_spyt': 'спить', 'ws_tam': 'там', 'ws_chytaie': 'читає',
    'ws_murchyk': 'Мурчик',
}

# --- знаки в кінці речення: дитина має почути, як вони називаються
PUNCT = {'pq_dot': 'крапка', 'pq_quest': 'знак питання', 'pq_excl': 'знак оклику'}

# --- домашнє завдання з каліграфії
HOME = {
    'q_hwrow':  'Напиши букву в рядок, як зразок',
    'q_hwdone': 'Рядок готовий!',
    'q_hwfin':  'Домашнє завдання виконано. Молодець!',
}

# --- органи чуття: кликалися в грі, а запису не було
SENSE = {'sn_eye': 'очі', 'sn_ear': 'вуха', 'sn_nose': 'ніс',
         'sn_tongue': 'язик', 'sn_hand': 'шкіра'}

# --- числа. Були тільки до дванадцяти, а острови дають до ста.
ONES = {1: 'один', 2: 'два', 3: 'три', 4: 'чотири', 5: "п'ять",
        6: 'шість', 7: 'сім', 8: 'вісім', 9: "дев'ять"}
TEENS = {11: 'одинадцять', 12: 'дванадцять', 13: 'тринадцять',
         14: 'чотирнадцять', 15: "п'ятнадцять", 16: 'шістнадцять',
         17: 'сімнадцять', 18: 'вісімнадцять', 19: "дев'ятнадцять"}
TENS = {10: 'десять', 20: 'двадцять', 30: 'тридцять', 40: 'сорок',
        50: "п'ятдесят", 60: 'шістдесят', 70: 'сімдесят',
        80: 'вісімдесят', 90: "дев'яносто", 100: 'сто'}


def num_word(n):
    if n in TEENS:
        return TEENS[n]
    if n in TENS:
        return TENS[n]
    if n in ONES:
        return ONES[n]
    if n == 0:
        return 'нуль'
    if n == 110:
        return 'сто десять'
    t, o = n // 10 * 10, n % 10
    return TENS[t] + ' ' + ONES[o]


def main():
    with open(MAN, encoding='utf-8') as f:
        man = json.load(f)
    items = man['voice']['items']
    before = len(items)
    added = []

    def put(vid, text):
        if vid in items:
            return
        items[vid] = [text, 'word']
        added.append((vid, text))

    for vid, text in EMOJI.values():
        put(vid, text)
    for vid, text in WEAR.values():
        put(vid, text)
    for vid, text in WORDS.items():
        put(vid, text)
    for vid, text in PUNCT.items():
        put(vid, text)
    for vid, text in HOME.items():
        # Це цілі речення, а не слова: інтонація має бути фразова.
        if vid not in items:
            items[vid] = [text, 'phrase']
            added.append((vid, text))
    for vid, text in SENSE.items():
        put(vid, text)
    for n in list(range(0, 101)) + [110]:
        put('n%d' % n, num_word(n))

    # Порядок у файлі лишаємо стабільним: інакше кожен запуск давав би
    # величезний несправжній діфф.
    man['voice']['items'] = dict(sorted(items.items()))
    with io.open(MAN, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print('було %d, додано %d, стало %d' % (before, len(added), len(items)))
    for vid, text in added:
        print('  %-16s %s' % (vid, text))


if __name__ == '__main__':
    main()
