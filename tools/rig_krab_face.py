# -*- coding: utf-8 -*-
"""Прибирає з тіла намальовані очі й рот — їх малюватиме гра.

Навіщо: зіницю не зрушиш і повікою не кліпнеш, поки очі впечені в
картинку. Очі стирчать над панциром, тож на їхньому місці лишається
прозорість, яку згори накриє намальоване вікторне око. Рот натомість
лежить посеред панцира, і діру там видно було б одразу, тому його
зафарбовуємо кольором панцира, взятим поруч.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT = r'G:\ostriv-znan\assets\krab'
BB = (110, 144)                   # зсув тіла відносно початкової картинки

body = Image.open(os.path.join(OUT, 'body.png')).convert('RGBA')

EYES = [(400, 305, 52, 56), (645, 312, 52, 56)]       # x, y, rx, ry
MOUTH = (408, 390, 618, 462)                          # рамка усмішки

# Рот замальовуємо не плоским кольором, а шматком самого панцира, взятим
# нижче: там чиста заливка з тим самим градієнтом і тією самою тінню.
# Плоска латка одразу впадала в око світлішою плямою.
DY = 92                           # звідки брати: на стільки нижче
x1, y1, x2, y2 = (MOUTH[0] - BB[0], MOUTH[1] - BB[1],
                  MOUTH[2] - BB[0], MOUTH[3] - BB[1])
donor = body.crop((x1, y1 + DY, x2, y2 + DY))

# М'які краї, щоб не було видно шва
soft = Image.new('L', donor.size, 0)
ImageDraw.Draw(soft).rounded_rectangle([6, 6, donor.width - 6, donor.height - 6],
                                       radius=24, fill=255)
soft = soft.filter(ImageFilter.GaussianBlur(9))
body.paste(donor, (x1, y1), soft)

hole = Image.new('L', body.size, 255)
hd = ImageDraw.Draw(hole)
for x, y, rx, ry in EYES:
    hd.ellipse([x - BB[0] - rx, y - BB[1] - ry, x - BB[0] + rx, y - BB[1] + ry], fill=0)
hole = hole.filter(ImageFilter.GaussianBlur(1.5))
body.putalpha(Image.composite(body.getchannel('A'),
                              Image.new('L', body.size, 0), hole))

body.save(os.path.join(OUT, 'body.png'))
print('очі прибрано, рот зафарбовано ->', os.path.join(OUT, 'body.png'))
