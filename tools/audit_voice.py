# -*- coding: utf-8 -*-
"""Де в грі немає записаного голосу.

Дві діри, які чує дитина, різні за природою:
  1. ідентифікатор є, а файла нема — гра підставляє синтез Windows, а на цій
     системі українського голосу немає, і виходить каша (саме це «хуйня
     замість голосу»);
  2. голос узагалі не кличеться — тиша.

Перша перевіряється порівнянням ідентифікаторів із файлами, друга — пошуком
місць, де текст показується без say(). Тут робимо першу і готуємо список для
догенерації.

Приймає файл із переліком ідентифікаторів (по одному в рядку або через кому),
зібраних обходом гри в браузері.
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(os.path.dirname(ROOT), 'assets', 'voice')
HTML = os.path.join(os.path.dirname(ROOT), sys.argv[2] if len(sys.argv) > 2
                    else 'index-1klas.html')

with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
    man = json.load(f)['voice']['items']

runtime = []
with open(sys.argv[1], encoding='utf-8') as f:
    for chunk in re.split(r'[,\s]+', f.read()):
        c = chunk.strip()
        if c:
            runtime.append(c)

have = {n[:-4] for n in os.listdir(VOICE) if n.endswith('.wav')}

# --- 1. ідентифікатори з обходу завдань
ids = [i for i in runtime if not i.startswith('en:')]
no_file = sorted(i for i in ids if i not in have)
no_man = sorted(i for i in ids if i not in man)

# --- 2. ідентифікатори, вписані прямо в код інтерфейсу (не з завдань):
#        say([['x_id','текст']]) і speak:[['x_id',...]]
src = open(HTML, encoding='utf-8').read()
lit = set(re.findall(r"\[\s*'([a-z][a-z0-9_]{1,30})'\s*,", src))
lit |= set(re.findall(r'\[\s*"([a-z][a-z0-9_]{1,30})"\s*,', src))
ui = sorted(i for i in lit if i not in set(ids))
ui_no_file = sorted(i for i in ui if i not in have)

print('ОБХІД ЗАВДАНЬ')
print('  ідентифікаторів:      %d' % len(ids))
print('  без файла:            %d' % len(no_file))
print('  немає в маніфесті:    %d' % len(no_man))
if no_file:
    print('  -> ' + ', '.join(no_file))
if no_man:
    print('  маніфест: ' + ', '.join(no_man))
print()
print('ІНТЕРФЕЙС (ідентифікатори в коді, яких обхід завдань не дав)')
print('  усього:               %d' % len(ui))
print('  без файла:            %d' % len(ui_no_file))
if ui_no_file:
    print('  -> ' + ', '.join(ui_no_file))
print()
print('ФАЙЛИ')
print('  записано:             %d' % len(have))
print('  у маніфесті:          %d' % len(man))
orphan = sorted(i for i in man if i not in have)
if orphan:
    print('  у маніфесті без файла: ' + ', '.join(orphan))
