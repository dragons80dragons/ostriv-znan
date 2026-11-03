# -*- coding: utf-8 -*-
"""Оновлює теку «Острів Знань (на флешку)» на робочому столі.

Ця тека — те, що беруть на чужий комп'ютер: гра одним файлом, сервер
режиму вчителя, іконки, ярликороб і ЧИТАТИ.txt. У ній немає `index.html`:
гра лежить під власною назвою, і `server.py` це враховує — якщо index.html
немає, головною сторінкою стає єдиний .html у теці.

Навіщо скрипт. Теку збирали руками, і вона тихо відстала на два тижні:
ярлики з робочого столу відкривали гру без прописів, без нового краба й
без музики островів, а ЧИТАТИ.txt обіцяв шістнадцять островів замість
вісімнадцяти. Нічого при цьому не ламалося — саме тому й не помічалося.

Джерела всього, що в ній лежить, тепер у проєкті: тексти й скрипти — у
`flash\\`, гра — збірка `build_single.py`, решта — `teacher\\` та `icons\\`.

Запуск (спершу build_single.py, інакше покладеться стара збірка):
    "<python>" pack_flash.py
    "<python>" pack_flash.py --dest "D:\\Острів Знань"
"""
import argparse
import ctypes
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
SINGLE = 'ostriv-znan-один-файл.html'
GAME = 'Острів Знань.html'          # під цією назвою гра лежить у теці

# teacher\ копіюємо не цілком: results.jsonl — результати класу, і на
# чужому комп'ютері їм робити нічого.
TEACHER = ['server.py', '_address.txt', '_nopy.txt', '_ui.txt',
           'Кіоск на планшеті.cmd', 'Режим вчителя.cmd', 'ЯК_РОЗГОРНУТИ.md']


def default_dest():
    return os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop',
                        'Острів Знань (на флешку)')


def copy(src, dst):
    """Копіює байт у байт: у .cmd має лишитися ASCII, у .ps1 — BOM.

    Два місця, де проста copy2 падає. По-перше, desktop.ini прихований і
    системний — Windows не дає його перезаписати, поки не зняти ознаки.
    По-друге, перезаписувати те, що не змінилося, шкода: тека лежить на
    робочому столі, і кожен дотик до файлу переставляє йому дату.
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    was = None
    if os.path.exists(dst):
        with open(src, 'rb') as a, open(dst, 'rb') as b:
            if a.read() == b.read():
                return os.path.getsize(dst)
        was = ctypes.windll.kernel32.GetFileAttributesW(dst)
        if was != -1:
            ctypes.windll.kernel32.SetFileAttributesW(dst, 0x80)   # NORMAL
    shutil.copy2(src, dst)
    if was not in (None, -1):
        ctypes.windll.kernel32.SetFileAttributesW(dst, was)
    return os.path.getsize(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dest', default='')
    args = ap.parse_args()
    dest = args.dest or default_dest()

    game = os.path.join(PROJ, SINGLE)
    if not os.path.exists(game):
        sys.exit('немає однофайлової збірки — спершу tools/build_single.py')

    n = 0
    size = copy(game, os.path.join(dest, GAME))
    print('[флешка] %s — %.1f МБ' % (GAME, size / 1e6), flush=True)

    for fn in sorted(os.listdir(os.path.join(PROJ, 'flash'))):
        copy(os.path.join(PROJ, 'flash', fn), os.path.join(dest, fn)); n += 1
    for fn in TEACHER:
        src = os.path.join(PROJ, 'teacher', fn)
        if os.path.exists(src):
            copy(src, os.path.join(dest, 'teacher', fn)); n += 1
    for fn in sorted(os.listdir(os.path.join(PROJ, 'icons'))):
        if fn.endswith('.ico'):
            copy(os.path.join(PROJ, 'icons', fn),
                 os.path.join(dest, 'icons', fn)); n += 1

    print('[флешка] решта файлів: %d' % n, flush=True)
    print('[флешка] тека: %s' % dest, flush=True)
    print('[флешка] ярлики на столі робить «Zrobyty yarlyky.cmd» із цієї ж теки',
          flush=True)


if __name__ == '__main__':
    main()
