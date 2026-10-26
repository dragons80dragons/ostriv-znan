# -*- coding: utf-8 -*-
"""Оновлює папку «_для диску» — те, що віддають на флешці чи Диску.

Там лежать дві речі й три ярлики:
  * ostriv-znan-один-файл.html — гра одним файлом, нічого не потрібно;
  * ostriv-znan-повний.zip — проєкт для комп'ютера вчителя: гра, усі
    ресурси, сервер режиму вчителя й інструкція розгортання.

Ярлики (.url) скрипт не чіпає: вони вказують на адреси, а не на файли.

Чого в архіві НЕМАЄ і чому:
  * teacher/results.jsonl — це результати класу, дані дітей. Копіювати
    їх на чужий комп'ютер не можна, та й новому класу вони ні до чого.
  * tools/ — генерація ресурсів прив'язана до ШІ-парку G:\\LOCAL AI
    AGENTS. На іншій машині ці скрипти не запустяться, а важать разом
    із чернетками більше за саму гру. Готові ресурси в архіві є.
  * __pycache__ і .pyc — службове сміття Python.

Запуск:
    "<python>" pack_drive.py
"""
import os
import shutil
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
DRIVE = os.path.join(PROJ, '_для диску')
SINGLE = 'ostriv-znan-один-файл.html'
ZIP = 'ostriv-znan-повний.zip'

# Що кладемо в архів. Теки беруться цілком, окрім винятків нижче.
FOLDERS = ['assets', 'teacher', 'icons']
FILES = ['index.html', 'README.md', 'HANDOVER.md']
SKIP_NAMES = {'results.jsonl', 'desktop.ini', 'Thumbs.db'}
SKIP_DIRS = {'__pycache__'}


def wanted(path, name):
    if name in SKIP_NAMES or name.endswith('.pyc'):
        return False
    return not any(part in SKIP_DIRS for part in path.split(os.sep))


def main():
    os.makedirs(DRIVE, exist_ok=True)
    src = os.path.join(PROJ, SINGLE)
    if not os.path.exists(src):
        sys.exit('немає однофайлової збірки — спершу tools/build_single.py')

    shutil.copy2(src, os.path.join(DRIVE, SINGLE))
    print('[диск] %s — %.1f МБ' % (SINGLE, os.path.getsize(src) / 1e6), flush=True)

    # Пишемо поруч і підміняємо в кінці: якщо збірка обірветься на
    # середині, стара робоча копія лишиться на місці.
    out = os.path.join(DRIVE, ZIP)
    tmp = out + '.tmp'
    n = 0
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for fn in FILES:
            p = os.path.join(PROJ, fn)
            if os.path.exists(p):
                z.write(p, fn); n += 1
        for folder in FOLDERS:
            base = os.path.join(PROJ, folder)
            for cur, dirs, names in os.walk(base):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in sorted(names):
                    p = os.path.join(cur, name)
                    if not wanted(p, name):
                        continue
                    z.write(p, os.path.relpath(p, PROJ).replace(os.sep, '/'))
                    n += 1
    os.replace(tmp, out)
    print('[диск] %s — %d файлів, %.1f МБ'
          % (ZIP, n, os.path.getsize(out) / 1e6), flush=True)


if __name__ == '__main__':
    main()
