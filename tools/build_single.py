# -*- coding: utf-8 -*-
"""Збірка гри в ОДИН файл: ostriv-znan-один-файл.html.

Навіщо: щоб гру можна було дати комусь одним файлом — скопіювати на
флешку, покласти на Диск, відкрити подвійним клацанням на будь-якому
комп'ютері чи планшеті. Папка assets при цьому не потрібна взагалі.

Як: усі картинки й звуки перетворюються на `data:` і кладуться у
window.EMBED. Гра сама дивиться туди (див. asset() в index.html), тож
код уроків не змінюється ні на рядок.

Розмір має значення, бо файл качатимуть на планшети:
  * картинки PNG -> WebP (у 3–4 рази менше, видно так само);
  * голос і музика WAV -> MP3 (голос моно 64 кбіт, музика 128).
Разом виходить близько 5 МБ замість 28.

Запуск (потрібні Pillow і ffmpeg — є у venv агента 11_BGREMOVE):
    "Зібрати один файл.cmd"
"""
import base64
import io
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
OUT = os.path.join(PROJ, 'ostriv-znan-один-файл.html')
FFMPEG = os.path.join(r'G:\LOCAL AI AGENTS\00_SHARED\bin', 'ffmpeg.exe')


def as_webp(path, quality=88):
    im = Image.open(path).convert('RGBA')
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=quality, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


def as_mp3(path, bitrate, mono):
    tmp = os.path.join(tempfile.gettempdir(), 'ostriv_tmp.mp3')
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-i', path, '-b:a', bitrate]
    if mono:
        cmd += ['-ac', '1']
    cmd.append(tmp)
    subprocess.run(cmd, check=True, capture_output=True)
    with open(tmp, 'rb') as f:
        data = f.read()
    os.remove(tmp)
    return 'data:audio/mpeg;base64,' + base64.b64encode(data).decode()


def main():
    if not os.path.exists(FFMPEG):
        sys.exit('немає ffmpeg: %s' % FFMPEG)
    embed, raw, packed = {}, 0, 0

    img_dir = os.path.join(PROJ, 'assets', 'img')
    for fn in sorted(os.listdir(img_dir)):
        if not fn.endswith('.png'):
            continue
        p = os.path.join(img_dir, fn)
        raw += os.path.getsize(p)
        uri = as_webp(p)
        packed += len(uri)
        embed['img/' + fn] = uri
    print('[збірка] картинок: %d' % len(embed), flush=True)

    # Стрічки кадрів краба. Їх може не бути — гра тоді показує одну
    # картинку й рухає її сама, тож папка не обов'язкова.
    crab_dir = os.path.join(PROJ, 'assets', 'crab')
    k = 0
    if os.path.isdir(crab_dir):
        for fn in sorted(os.listdir(crab_dir)):
            if not fn.endswith('.png'):
                continue
            p = os.path.join(crab_dir, fn)
            raw += os.path.getsize(p)
            uri = as_webp(p)
            packed += len(uri)
            embed['crab/' + fn] = uri
            k += 1
    print('[збірка] стрічок краба: %d' % k, flush=True)

    voice_dir = os.path.join(PROJ, 'assets', 'voice')
    n = 0
    for fn in sorted(os.listdir(voice_dir)):
        if not fn.endswith('.wav'):
            continue
        p = os.path.join(voice_dir, fn)
        raw += os.path.getsize(p)
        uri = as_mp3(p, '64k', True)
        packed += len(uri)
        embed['voice/' + fn] = uri
        n += 1
    print('[збірка] кліпів: %d' % n, flush=True)

    theme = os.path.join(PROJ, 'assets', 'music', 'theme.wav')
    if os.path.exists(theme):
        raw += os.path.getsize(theme)
        embed['music/theme.wav'] = as_mp3(theme, '128k', False)
        print('[збірка] музика вбудована', flush=True)

    with io.open(os.path.join(PROJ, 'index.html'), encoding='utf-8') as f:
        html = f.read()
    tag = ('<script>window.EMBED=%s</script>\n'
           % json.dumps(embed, ensure_ascii=False, separators=(',', ':')))
    # Вставляємо ПЕРЕД головним скриптом, щоб asset() уже бачив мапу.
    marker = '<script>\nconst $ = s => document.querySelector(s);'
    if marker not in html:
        sys.exit('не знайшов місця для вставки — index.html змінився?')
    html = html.replace(marker, tag + marker, 1)

    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('[збірка] %s — %.1f МБ (було %.1f МБ у папці assets)'
          % (OUT, os.path.getsize(OUT) / 1e6, raw / 1e6), flush=True)


if __name__ == '__main__':
    main()
