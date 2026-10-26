# -*- coding: utf-8 -*-
"""Зрівнює гучність вісімнадцяти острівних мелодій.

ACE-Step видає треки з розкидом у чотири децибели. На самому острові це
непомітно, а от коли дитина пливе з острова на острів, музика то
голоснішає, то стихає — і це чути одразу.

Рівняємо вниз, до найтихішого треку: тоді жоден не треба підсилювати, а
отже ніде не з'явиться обрізаний пік. Викликається сам наприкінці
gen_island_music.py, але можна й окремо:

    "<python>" level_music.py
"""
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.join(os.path.dirname(ROOT), 'assets', 'music')
FFMPEG = r'G:\LOCAL AI AGENTS\00_SHARED\bin\ffmpeg.exe'
TARGET = -20.5          # дБ середньої гучності — рівень найтихішої мелодії


def mean_db(path):
    out = subprocess.run([FFMPEG, '-i', path, '-af', 'volumedetect',
                          '-f', 'null', '-'],
                         capture_output=True, text=True, errors='replace').stderr
    m = re.search(r'mean_volume: (-?[\d.]+) dB', out)
    return float(m.group(1)) if m else None


def main():
    for fn in sorted(os.listdir(MUSIC)):
        if not fn.endswith('.mp3'):
            continue
        p = os.path.join(MUSIC, fn)
        db = mean_db(p)
        if db is None:
            print('[рівень] %-12s не вдалося виміряти' % fn, flush=True)
            continue
        gain = round(TARGET - db, 1)
        if gain >= -0.2:                    # уже тихий — зайве перекодування
            print('[рівень] %-12s %+.1f дБ — лишаємо' % (fn, db), flush=True)
            continue
        tmp = p + '.tmp.mp3'
        subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', p,
                        '-af', 'volume=%.1fdB' % gain,
                        '-codec:a', 'libmp3lame', '-b:a', '96k', tmp], check=True)
        os.replace(tmp, p)
        print('[рівень] %-12s %+.1f дБ -> %+.1f дБ' % (fn, db, TARGET), flush=True)


if __name__ == '__main__':
    main()
