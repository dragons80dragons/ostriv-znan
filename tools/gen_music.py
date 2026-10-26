# -*- coding: utf-8 -*-
"""Фонова музика для гри: ACE-Step 1.5 (агент 05_MUSIC) + безшовний цикл.

Запускати інтерпретатором з venv агента 05_MUSIC і з його ж папки — простіше
через «Згенерувати музику.cmd» поруч.

Дві речі, через які це не просто «запустити cli.py»:

1. ACE-Step на Pascal дає NaN-латенти у float16 («Float16 overflow on
   pre-Ampere GPU») — тому ACESTEP_DTYPE=float32, як у ярлику агента.
   Платимо швидкістю: приблизно 1,7 с рахунку на секунду звуку.
2. Модель не вміє робити цикл: кінець треку не стикується з початком.
   Тому останні кілька секунд підмішуються в початок хрест-навхрест
   (crossfade), а хвіст відрізається. Так `music.loop = true` у грі не дає
   чутного шва.

cli.py читає TOML через toml.load(open(path)) без кодування — на Windows це
системний ANSI, тому конфіг пишемо суворо ASCII.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import wave

import numpy as np

# Консоль Windows тут cp1251 — український print інакше вбиває скрипт.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
ACE = r'G:\LOCAL AI AGENTS\05_MUSIC\ACE-Step'
OUT_DIR = os.path.join(ROOT, '_music')
FADE = 3.0                  # секунд перехресного згасання


def write_config(path, music, seed):
    cfg = [
        'caption = "%s"' % music['prompt'].replace('"', ''),
        'lyrics = "[Instrumental]"',
        'instrumental = true',
        'duration = %d' % (music['duration'] + FADE),
        'bpm = %d' % music['bpm'],
        'audio_format = "wav"',
        'save_dir = "%s"' % OUT_DIR.replace('\\', '\\\\'),
        'batch_size = 1',
        'backend = "pt"',            # vllm вимагає compute 7.0+, у нас 6.1
        # thinking = false вимикає етап 5Hz LM. Це не оптимізація, а вимога:
        # при thinking = true cli.py вішає гачок редагування промпту, зберігає
        # чернетку в instruction.txt і чекає на Enter (`input()`), а в пакетному
        # запуску stdin порожній — процес падає з EOFError ще до генерації.
        # Побічно це й швидше: саме LM з'їдав дві третини часу.
        'thinking = false',
        'seed = %d' % seed,
        'use_random_seed = false',
    ]
    with open(path, 'w', encoding='ascii') as f:
        f.write('\n'.join(cfg) + '\n')
    return path


def newest_audio(folder, after):
    best = None
    for dirpath, _, files in os.walk(folder):
        for fn in files:
            # службові файли (_decoded.wav) не рахуються за результат
            if fn.startswith('_') or not fn.lower().endswith(('.wav', '.mp3', '.flac')):
                continue
            p = os.path.join(dirpath, fn)
            if os.path.getmtime(p) >= after and (best is None
                                                 or os.path.getmtime(p) > os.path.getmtime(best)):
                best = p
    return best


def read_audio(path):
    """Читаємо через ffmpeg із 00_SHARED\\bin, і це не перестраховка:
    ACE-Step віддає WAV у float32 (wFormatTag=3), а стандартний модуль
    `wave` такий формат не відкриває взагалі — «unknown format: 3».
    Тому будь-який вхід проганяємо в 16-бітний PCM.
    """
    wav = os.path.join(OUT_DIR, '_decoded.wav')
    subprocess.run(['ffmpeg', '-y', '-i', path, '-ac', '2', '-ar', '44100',
                    '-c:a', 'pcm_s16le', wav], check=True, capture_output=True)
    path = wav
    with wave.open(path, 'rb') as f:
        sr, ch = f.getframerate(), f.getnchannels()
        data = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2')
    return data.reshape(-1, ch).astype(np.float32) / 32768.0, sr


def make_loop(audio, sr, fade=FADE):
    n = int(sr * fade)
    if audio.shape[0] <= 2 * n:
        return audio
    head, tail, body = audio[:n], audio[-n:], audio[n:-n]
    ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)[:, None]
    joined = head * ramp + tail * (1.0 - ramp)
    out = np.concatenate([joined, body])
    peak = float(np.abs(out).max()) or 1.0
    return out * (0.89 / peak)


def write_wav(path, audio, sr):
    data = (np.clip(audio, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as f:
        f.setnchannels(audio.shape[1])
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(data.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=20261020)
    ap.add_argument('--keep', action='store_true', help='не видаляти сирий трек')
    ap.add_argument('--use-existing', action='store_true',
                    help='не генерувати заново, взяти останній трек із tools\\_music')
    # Окремі мелодії для островів: та сама машинерія, лише інший опис і
    # інший файл на виході. Описи лежать у gen_island_music.py.
    ap.add_argument('--prompt', default='')
    ap.add_argument('--bpm', type=int, default=0)
    ap.add_argument('--dur', type=int, default=0)
    ap.add_argument('--file', default='')
    args = ap.parse_args()

    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        music = json.load(f)['music']
    if args.prompt:
        music = dict(music, prompt=args.prompt)
    if args.bpm:
        music['bpm'] = args.bpm
    if args.dur:
        music['duration'] = args.dur
    if args.file:
        music['file'] = args.file
    os.makedirs(OUT_DIR, exist_ok=True)
    cfg = write_config(os.path.join(OUT_DIR, 'music.toml'), music, args.seed)

    t0 = time.time()
    if args.use_existing:
        t0 = 0
        print('[music] беру готовий трек із %s' % OUT_DIR, flush=True)
    else:
        env = dict(os.environ)
        env['ACESTEP_DTYPE'] = 'float32'      # інакше NaN-латенти на Pascal
        print('[music] генерую %d с (%s)...' % (music['duration'], music['prompt'][:60]),
              flush=True)
        r = subprocess.run([sys.executable, 'cli.py', '-c', cfg], cwd=ACE, env=env)
        if r.returncode != 0:
            sys.exit('[music] cli.py завершився з кодом %d' % r.returncode)

    src = newest_audio(OUT_DIR, t0 - 5 if t0 else 0)
    if not src:
        sys.exit('[music] не знайшов згенерованого файлу в %s' % OUT_DIR)
    print('[music] сирий трек: %s%s' % (
        src, '' if not t0 else ' (%.1f хв роботи)' % ((time.time() - t0) / 60)), flush=True)

    audio, sr = read_audio(src)
    loop = make_loop(audio, sr)
    dst_dir = os.path.join(PROJ, 'assets', 'music')
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, music['file'])
    write_wav(dst, loop, sr)
    print('[music] цикл %.1f с, %d Гц -> %s' % (loop.shape[0] / sr, sr, dst), flush=True)


if __name__ == '__main__':
    main()
