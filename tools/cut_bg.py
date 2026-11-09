# -*- coding: utf-8 -*-
"""Вирізання фону й підгонка під гру: tools/_raw/*.png -> assets/img/*.png.

Запускати інтерпретатором з venv агента 11_BGREMOVE (там rembg + onnxruntime
на GPU) і його ж запускачем, бо потрібні DLL cuDNN із site-packages\\nvidia:

    "Вирізати фон для гри.cmd"

Що робить з кожною картинкою:
  1. rembg (birefnet-general) — прозорий фон;
  2. обрізає порожні поля;
  3. вписує в квадрат 512×512 з невеликим полем, зберігає пропорції.

Останні два кроки важливі: гра показує картинки дрібно (44–140 px), і якщо
предмет займає третину кадру, дитина бачить цятку.
"""
import argparse
import json
import os
import shutil
import sys
import time

from PIL import Image
from rembg import new_session, remove

# Консоль Windows тут cp1251 — український print інакше вбиває скрипт.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, '_raw')
OUT = os.path.join(os.path.dirname(ROOT), 'assets', 'img')
SIZE = 512
MARGIN = 0.04               # поле з кожного боку, частка від сторони


def fit_square(im, size=SIZE, margin=MARGIN):
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    inner = int(size * (1 - 2 * margin))
    scale = min(inner / im.width, inner / im.height)
    im = im.resize((max(1, round(im.width * scale)),
                    max(1, round(im.height * scale))), Image.LANCZOS)
    plate = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    plate.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return plate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='birefnet-general')
    ap.add_argument('--ids', default='')
    ap.add_argument('--skip-existing', action='store_true')
    ap.add_argument('--cpu', action='store_true',
                    help='рахувати на процесорі, щоб не відбирати відеокарту '
                         'в генератора картинок чи музики')
    args = ap.parse_args()

    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        man = json.load(f)
    drawn = set(man.get('shapes', {}).get('items', {}))
    reuse = man['image'].get('reuse', {})
    # Тло вирізати НЕ можна: там фон і є картинкою, після rembg лишилася б
    # прозора пляма. Це стосується шпалер (bg_*) і сцен для «знайди на
    # картині» (sc_*) — вони йдуть в assets/img як є.
    ids = [i.strip() for i in args.ids.split(',') if i.strip()] or \
          [k for k in man['image']['items']
           if k not in drawn and k not in reuse and not k.startswith(('bg_', 'sc_'))]

    os.makedirs(OUT, exist_ok=True)
    # Відеокарта тут одна, і поки на ній малює SDXL чи ACE-Step, rembg на
    # неї не влізе. Зате вирізання фону — єдиний крок ланцюга, який цілком
    # прийнятно рахувати на процесорі: втрачаємо секунди, а не години,
    # і робота йде СПРАВДІ паралельно з генерацією.
    if args.cpu:
        session = new_session(args.model, providers=['CPUExecutionProvider'])
        print('[bg] модель %s на ПРОЦЕСОРІ' % args.model, flush=True)
    else:
        session = new_session(args.model)
        print('[bg] модель %s' % args.model, flush=True)

    done = miss = 0
    t0 = time.time()
    for cid in ids:
        src = os.path.join(RAW, cid + '.png')
        dst = os.path.join(OUT, cid + '.png')
        if not os.path.exists(src):
            print('[bg] немає сирої картинки: %s' % cid, flush=True)
            miss += 1
            continue
        if args.skip_existing and os.path.exists(dst):
            continue
        # Вирізання може йти ПАРАЛЕЛЬНО з малюванням (--cpu), і тоді легко
        # натрапити на картинку, яку ComfyUI саме дописує: PIL падає з
        # UnidentifiedImageError і вбиває весь прохід. Тому свіжі файли
        # пропускаємо, а зіпсоване читання не вважаємо смертельним —
        # наступний прохід їх підбере.
        if time.time() - os.path.getmtime(src) < 10:
            print('[bg] %-14s ще дописується — пропускаю' % cid, flush=True)
            miss += 1
            continue
        t1 = time.time()
        try:
            im = Image.open(src)
            im.load()
            cut = remove(im.convert('RGBA'), session=session)
        except Exception as e:                                        # noqa: BLE001
            print('[bg] %-14s не прочиталась (%s) — пропускаю'
                  % (cid, type(e).__name__), flush=True)
            miss += 1
            continue
        fit_square(cut).save(dst)
        done += 1
        print('[bg] %-14s %.2f с -> %s' % (cid, time.time() - t1, dst), flush=True)
    # Сцени для «знайди на картині» переносимо як є: фон у них і є
    # картинкою, різати нічого. Квадрат їм теж не потрібен — гра показує
    # сцену широким полем.
    for cid in man['image']['items']:
        if not cid.startswith('sc_'):
            continue
        src = os.path.join(RAW, cid + '.png')
        dst = os.path.join(OUT, cid + '.png')
        if not os.path.exists(src) or (args.skip_existing and os.path.exists(dst)):
            continue
        Image.open(src).convert('RGB').save(dst)
        print('[bg] %-14s перенесено як тло -> %s' % (cid, dst), flush=True)
    # Картинки, які свідомо повторюють інші (див. manifest.json, reuse).
    for cid, src_id in reuse.items():
        src = os.path.join(OUT, src_id + '.png')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, cid + '.png'))
            print('[bg] %-14s копія %s' % (cid, src_id), flush=True)

    print('[bg] готово: %d, без сирої картинки %d, %.1f с'
          % (done, miss, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
