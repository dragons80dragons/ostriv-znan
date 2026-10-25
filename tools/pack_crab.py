# -*- coding: utf-8 -*-
"""Кадри краба -> стрічка спрайтів для гри.

Бере кадри з tools/_anim/<настрій>/, вирізає фон і складає їх в один
горизонтальний рядок assets/crab/<настрій>.png. Гра крутить його
звичайною CSS-анімацією зі steps() — без жодного JavaScript.

Головне, чим це відрізняється від cut_bg.py: там кожна картинка
обрізається по своїй рамці й центрується. Для анімації так не можна —
центрування кожного кадру окремо з'їло б увесь рух. Тут рамка рахується
одна на всі кадри настрою, і всі вони ріжуться однаково.

Запускати інтерпретатором агента 11_BGREMOVE (там rembg):

    "G:\\LOCAL AI AGENTS\\11_BGREMOVE\\.venv\\Scripts\\python.exe" pack_crab.py
"""
import argparse
import os
import sys
import time

from PIL import Image
from rembg import new_session, remove

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(ROOT, '_anim')
OUT = os.path.join(os.path.dirname(ROOT), 'assets', 'crab')
CELL = 128                  # розмір кадру в стрічці
MARGIN = 0.03


def frames_of(mood):
    d = os.path.join(ANIM, mood)
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.png')]


def pack(mood, session):
    files = frames_of(mood)
    if not files:
        return None
    cut = [remove(Image.open(f).convert('RGBA'), session=session) for f in files]

    # Одна рамка на весь настрій: інакше кожен кадр центрувався б окремо
    # і рух зник би — краб стояв би на місці, смикаючи клешнями.
    box = None
    for im in cut:
        b = im.getbbox()
        if not b:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                     max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        return None

    w, h = box[2] - box[0], box[3] - box[1]
    inner = int(CELL * (1 - 2 * MARGIN))
    scale = min(inner / float(w), inner / float(h))
    tw, th = max(1, round(w * scale)), max(1, round(h * scale))
    strip = Image.new('RGBA', (CELL * len(cut), CELL), (0, 0, 0, 0))
    for i, im in enumerate(cut):
        piece = im.crop(box).resize((tw, th), Image.LANCZOS)
        strip.paste(piece, (i * CELL + (CELL - tw) // 2, (CELL - th) // 2), piece)

    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, mood + '.png')
    strip.save(dst, optimize=True)
    return dst, len(cut)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--moods', default='', help='через кому; типово — усі з _anim')
    ap.add_argument('--model', default='birefnet-general')
    args = ap.parse_args()

    moods = [m.strip() for m in args.moods.split(',') if m.strip()]
    if not moods:
        moods = sorted(d for d in os.listdir(ANIM)
                       if os.path.isdir(os.path.join(ANIM, d)))
    session = new_session(args.model)
    print('[pack] модель %s, настроїв %d' % (args.model, len(moods)), flush=True)

    t0 = time.time()
    for m in moods:
        try:
            res = pack(m, session)
        except Exception as e:                                    # noqa: BLE001
            print('[pack] %-8s збій: %r' % (m, e), flush=True)
            continue
        if not res:
            print('[pack] %-8s кадрів немає' % m, flush=True)
            continue
        dst, n = res
        print('[pack] %-8s %2d кадрів -> %s (%d КБ)'
              % (m, n, os.path.basename(dst), os.path.getsize(dst) // 1024), flush=True)
    print('[pack] готово за %.1f хв' % ((time.time() - t0) / 60), flush=True)


if __name__ == '__main__':
    main()
