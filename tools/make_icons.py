# -*- coding: utf-8 -*-
"""Іконки для ярликів: icons\\*.ico.

Просто покласти картинку острова в .ico мало: на робочому столі іконка
живе в 32 пікселі, і прозорий острівець на світлому тлі зливається з
шпалерами. Тому кожна іконка — кольоровий кружечок-підкладка (як на
плитках у грі) і предмет зверху.

У .ico кладемо одразу шість розмірів: Windows бере 16 px у списку файлів,
32 на робочому столі, 48 у «великих значках» і 256 у попередньому
перегляді. Якщо покласти лише великий, дрібні Windows зменшить сам —
і вийде мило.

Запуск:  python make_icons.py   (потрібен Pillow)
"""
import math
import os
import sys

from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
IMG = os.path.join(PROJ, 'assets', 'img')
OUT = os.path.join(PROJ, 'icons')
S = 512                                   # малюємо великим, потім зменшуємо
SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]


def plate(color, ring):
    """Кружечок-підкладка з тонким обідком."""
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((8, 8, S - 8, S - 8), fill=color, outline=ring, width=12)
    return im


def put(base, name, scale=0.74, dy=0.0):
    """Накласти картинку гри по центру підкладки."""
    src = Image.open(os.path.join(IMG, name)).convert('RGBA')
    side = int(S * scale)
    src.thumbnail((side, side), Image.LANCZOS)
    base.alpha_composite(src, ((S - src.width) // 2,
                               int((S - src.height) // 2 + S * dy)))
    return base


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.46
        a = math.radians(i * 36 - 90)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def report_badge(base):
    """Картка зі списком і зірками — звіт по класу. Рахівниця в 32 пікселі
    розсипалася на риски, а три золоті зірки читаються навіть там."""
    d = ImageDraw.Draw(base)
    w, h = int(S * 0.60), int(S * 0.52)
    x, y = (S - w) // 2, (S - h) // 2
    d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill='#ffffff')
    for i in range(3):                      # рядки «учнів»
        ly = y + int(h * (0.22 + i * 0.26))
        d.rounded_rectangle((x + 22, ly, x + int(w * 0.42), ly + 16),
                            radius=8, fill='#c3dde4')
        for k in range(3):                  # зірки навпроти кожного
            star(d, x + int(w * 0.56) + k * 42, ly + 8, 17, '#f2b632')
    return base


def folder_badge(base):
    """Проста папка — щоб ярлик на Диск читався з першого погляду."""
    d = ImageDraw.Draw(base)
    w, h = int(S * 0.56), int(S * 0.40)
    x, y = (S - w) // 2, int(S * 0.32)
    d.rounded_rectangle((x, y - int(h * 0.26), x + int(w * 0.42), y + 10),
                        radius=14, fill='#ffffff')
    d.rounded_rectangle((x, y, x + w, y + h), radius=18, fill='#ffffff')
    d.rounded_rectangle((x + 14, y + 14, x + w - 14, y + h - 14), radius=12,
                        fill='#2f84d8')
    return base


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    im.resize((256, 256), Image.LANCZOS).save(path, format='ICO', sizes=SIZES)
    print('[icons] %s' % path)
    return path


def main():
    # Гра — острів на морі
    save(put(plate('#d8eef3', '#2f7f99'), 'i_world.png'), 'gra.ico')
    # Звіт — картка зі списком і зірками
    save(report_badge(plate('#fff3d6', '#f2b632')), 'zvit.ico')
    # Диск — папка на зеленому
    save(folder_badge(plate('#def0e3', '#3f9a5c')), 'dysk.ico')


if __name__ == '__main__':
    main()
