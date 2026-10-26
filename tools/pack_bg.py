# -*- coding: utf-8 -*-
"""Фони з _raw у assets/bg.

Навмисно НЕ через cut_bg.py: там вирізається тло, а тут воно і є
картинкою. І не PNG, а JPEG — прозорість фону не потрібна, а різниця
у вазі десятикратна: по 1,5 МБ на кожен фон гра б не пережила.

Додатково фон трохи висвітлюється: поверх нього лежать текст і кнопки, і
навіть «тиха» картинка з генератора буває темнішою, ніж треба.
"""
import argparse
import glob
import os
import sys

from PIL import Image, ImageEnhance

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, '_raw')
OUT = os.path.join(os.path.dirname(ROOT), 'assets', 'bg')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--width', type=int, default=1024)
    ap.add_argument('--quality', type=int, default=82)
    ap.add_argument('--fade', type=float, default=0.35,
                    help='наскільки підмішати білого: 0 — як є, 1 — білий аркуш')
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, 'bg_*.png')))
    if not files:
        sys.exit('[bg] у _raw немає жодного bg_*.png')

    for f in files:
        cid = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f).convert('RGB')
        if im.width != args.width:
            h = round(im.height * args.width / im.width)
            im = im.resize((args.width, h), Image.LANCZOS)
        white = Image.new('RGB', im.size, (255, 255, 255))
        im = Image.blend(im, white, args.fade)
        im = ImageEnhance.Color(im).enhance(0.85)
        dst = os.path.join(OUT, cid + '.jpg')
        im.save(dst, 'JPEG', quality=args.quality, optimize=True, progressive=True)
        print('[bg] %-10s -> %s (%d КБ)'
              % (cid, os.path.basename(dst), os.path.getsize(dst) // 1024), flush=True)


if __name__ == '__main__':
    main()
