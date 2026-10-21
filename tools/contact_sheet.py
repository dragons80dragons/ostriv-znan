# -*- coding: utf-8 -*-
"""Один аркуш із усіма картинками — щоб оглянути набір, а не 36 файлів.

Підписує кожну клітинку id, кладе на шахівку (видно прозорість).

    python contact_sheet.py            # tools\_raw -> tools\_sheet_raw.png
    python contact_sheet.py --src ..\assets\img --out _sheet_final.png
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
CELL = 180
PAD = 6
LABEL = 16


def checker(size, step=12):
    im = Image.new('RGB', (size, size), (235, 235, 235))
    d = ImageDraw.Draw(im)
    for y in range(0, size, step):
        for x in range(0, size, step):
            if (x // step + y // step) % 2:
                d.rectangle((x, y, x + step, y + step), fill=(250, 250, 250))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join(ROOT, '_raw'))
    ap.add_argument('--out', default=os.path.join(ROOT, '_sheet_raw.png'))
    ap.add_argument('--cols', type=int, default=7)
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.src) if f.endswith('.png'))
    if not files:
        sys.exit('порожньо: %s' % args.src)
    cols = args.cols
    rows = (len(files) + cols - 1) // cols
    cw, ch = CELL + PAD * 2, CELL + PAD * 2 + LABEL
    sheet = Image.new('RGB', (cols * cw, rows * ch), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    tile = checker(CELL)

    for i, fn in enumerate(files):
        x, y = (i % cols) * cw, (i // cols) * ch
        cell = tile.copy()
        im = Image.open(os.path.join(args.src, fn)).convert('RGBA')
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        cell.paste(im, ((CELL - im.width) // 2, (CELL - im.height) // 2), im)
        sheet.paste(cell, (x + PAD, y + PAD))
        d.text((x + PAD, y + PAD + CELL + 2), os.path.splitext(fn)[0],
               fill=(20, 20, 20))

    sheet.save(args.out)
    print('[sheet] %d картинок -> %s' % (len(files), args.out))


if __name__ == '__main__':
    main()
