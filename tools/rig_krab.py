# -*- coding: utf-8 -*-
"""Повний риг краба №6: тіло, дві клешні, шість ніг.

Ноги не обводяться вручну. Нижче панцира вони розходяться віялом, тому
кожну можна відрізати кутовим сектором із центра тіла: де між ногами
порожньо — там і проходить межа. Сектори шукаються самі, по тому, де в
кутовій гістограмі провали.

Очі й рот тут НЕ вирізаються: їх буде намальовано поверх тіла векторними
фігурами. Інакше зіницю не зрушиш — під нею в картинці немає білка, а
домалювати його все одно довелося б.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SP = (r'C:\Users\User\AppData\Local\Temp\claude\G--'
      r'\d57a6877-1ea7-4a2c-99fe-5ea26563915f\scratchpad\krab6')
OUT = r'G:\ostriv-znan\assets\krab'
os.makedirs(OUT, exist_ok=True)

src = Image.open(os.path.join(SP, 'whole.png')).convert('RGBA')
W, H = src.size
CENTRE = (515, 470)               # середина панцира, від неї йде віяло ніг
LEG_TOP = 672                     # нижче панцира: там ноги вже нарізно

CLAWS = {
    'claw_l': {'poly': [(110, 55), (352, 55), (352, 435), (110, 435)],
               'pivot': (300, 400)},
    'claw_r': {'poly': [(553, 55), (890, 55), (890, 435), (690, 435),
                        (686, 298), (640, 248), (553, 193)],
               'pivot': (734, 398)},
}


def cut_mask(mask):
    part = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    part.paste(src, (0, 0), mask)
    return part


meta, body = {}, src.copy()

# --- клешні ---
for name, spec in CLAWS.items():
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(spec['poly'], fill=255)
    part = cut_mask(m)
    box = part.getbbox()
    part.crop(box).save(os.path.join(OUT, name + '.png'))
    body.paste(Image.new('RGBA', (W, H), (0, 0, 0, 0)), (0, 0), m)
    meta[name] = {'box': box, 'pivot': spec['pivot']}

# --- ноги: шукаємо провали в кутовій гістограмі ---
a = np.array(body)[:, :, 3] > 40
ys, xs = np.where(a)
keep = ys > LEG_TOP
ang = (np.degrees(np.arctan2(ys[keep] - CENTRE[1], xs[keep] - CENTRE[0]))) % 360
hist, edges = np.histogram(ang, bins=180, range=(0, 360))
# Ноги дивляться вниз: кути від 10° до 170° в екранних координатах
# (вісь y вниз), тому беремо саме цей діапазон.
lo, hi = 10, 170
band = [(edges[i], hist[i]) for i in range(180) if lo <= edges[i] < hi]
vals = [v for _, v in band]
thr = max(vals) * 0.22
groups, cur = [], None
for (e, v) in band:
    if v > thr:
        cur = [e, e] if cur is None else [cur[0], e]
    elif cur:
        groups.append(cur); cur = None
if cur:
    groups.append(cur)
# Усередині боку ноги перетинаються, тож кутова гістограма дає один
# суцільний блок на бік. Ділимо кожен бік на три рівні сектори: межа
# може зачепити сусідню ногу, але на малих кутах повороту шва не видно.
split = []
for g0, g1 in groups:
    step = (g1 - g0) / 3.0
    for k in range(3):
        split.append([g0 + k * step, g0 + (k + 1) * step])
groups = split
print("ніг:", len(groups), [(round(g[0]), round(g[1])) for g in groups])

yy, xx = np.mgrid[0:H, 0:W]
AN = np.degrees(np.arctan2(yy - CENTRE[1], xx - CENTRE[0])) % 360
for i, (g0, g1) in enumerate(groups, 1):
    sel = a & (yy > LEG_TOP) & (AN >= g0 - 1) & (AN <= g1 + 3)
    if sel.sum() < 2000:
        continue
    m = Image.fromarray((sel * 255).astype('uint8'), 'L')
    part = cut_mask(m)
    box = part.getbbox()
    name = 'leg%d' % i
    part.crop(box).save(os.path.join(OUT, name + '.png'))
    body.paste(Image.new('RGBA', (W, H), (0, 0, 0, 0)), (0, 0), m)
    # Суглоб — найвища точка ноги, тобто там, де вона виходить із панцира
    sy, sx = np.where(sel)
    top = sy.min()
    meta[name] = {'box': box, 'pivot': (int(sx[sy < top + 6].mean()), int(top))}
    print('%s рамка %s суглоб %s' % (name, box, meta[name]['pivot']))

bb = body.getbbox()
body.crop(bb).save(os.path.join(OUT, 'body.png'))
meta['body'] = {'box': bb}

# У відсотках від тіла — так їх зручно ставити в CSS
bw, bh = bb[2] - bb[0], bb[3] - bb[1]
out = {'body': [bw, bh], 'parts': {}}
for name, m in meta.items():
    if name == 'body':
        continue
    box, (px, py) = m['box'], m['pivot']
    out['parts'][name] = {
        'left': round((box[0] - bb[0]) * 100.0 / bw, 2),
        'top': round((box[1] - bb[1]) * 100.0 / bh, 2),
        'width': round((box[2] - box[0]) * 100.0 / bw, 2),
        'ox': round((px - box[0]) * 100.0 / (box[2] - box[0]), 1),
        'oy': round((py - box[1]) * 100.0 / (box[3] - box[1]), 1),
    }
with open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('тіло', bw, bh, '— частин', len(out['parts']))
