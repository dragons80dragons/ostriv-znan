# -*- coding: utf-8 -*-
"""Фігури для «Острова Візерунків» — малюються кодом, не моделлю.

SDXL на запит «red circle» видавав намальованого песика в червоному, а для
завдання «продовж візерунок» потрібні однакові чисті фігури з рівним краєм.
Тут вони виходять ідеальні, за секунду й без GPU.

Малюємо вчетверо більшими й зменшуємо — так краї згладжуються без фільтрів.

Запуск (будь-який Python з Pillow, напр. venv агента 11_BGREMOVE):
    python draw_shapes.py
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

# Консоль Windows тут cp1251 — український print інакше вбиває скрипт.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(ROOT), 'assets', 'img')
SIZE = 512
SS = 4                      # суперсемплінг
LINE = 10                   # товщина обведення в підсумкових пікселях


def poly_star(cx, cy, r_out, r_in, points=5, rot=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw(kind, fill, outline):
    s = SIZE * SS
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = LINE * SS
    pad = int(s * 0.10)
    box = (pad, pad, s - pad, s - pad)

    if kind == 'circle':
        d.ellipse(box, fill=fill, outline=outline, width=w)
    elif kind == 'oval':
        pad_y = int(s * 0.22)
        d.ellipse((pad, pad_y, s - pad, s - pad_y), fill=fill, outline=outline, width=w)
    elif kind == 'rect':
        pad_y = int(s * 0.24)
        d.rounded_rectangle((pad, pad_y, s - pad, s - pad_y), radius=int(s * 0.06),
                            fill=fill, outline=outline, width=w)
    elif kind == 'square':
        r = int(s * 0.10)
        d.rounded_rectangle((pad, pad, s - pad, s - pad), radius=r,
                            fill=fill, outline=outline, width=w)
    elif kind == 'triangle':
        h = s - 2 * pad
        pts = [(s / 2, pad), (s - pad, pad + h), (pad, pad + h)]
        d.polygon(pts, fill=fill, outline=outline, width=w)
    elif kind == 'star':
        pts = poly_star(s / 2, s / 2 + s * 0.02, (s - 2 * pad) / 2,
                        (s - 2 * pad) / 2 * 0.47)
        d.polygon(pts, fill=fill, outline=outline, width=w)
    else:
        raise ValueError('невідома фігура: %s' % kind)

    return im.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        man = json.load(f)
    sh = man['shapes']
    os.makedirs(OUT, exist_ok=True)
    outline = sh['outline']
    for cid, (kind, fill) in sh['items'].items():
        path = os.path.join(OUT, cid + '.png')
        draw(kind, fill, outline).save(path)
        print('[shapes] %-12s %-9s %s -> %s' % (cid, kind, fill, path))

    # Матриця «фігура × колір» для уроку фігур: та сама фігура в чотирьох
    # кольорах і той самий колір у п'яти фігурах — інакше дитина не зрозуміє,
    # про що саме питають, про форму чи про колір.
    fig = man.get('figures')
    if not fig:
        return
    n = 0
    for kind in fig['shapes']:
        for color, hexv in fig['colors'].items():
            cid = 'f_%s_%s' % (kind, color)
            draw(kind, hexv, outline).save(os.path.join(OUT, cid + '.png'))
            n += 1
    print('[shapes] матриця фігур: %d файлів' % n)


if __name__ == '__main__':
    main()
