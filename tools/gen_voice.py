# -*- coding: utf-8 -*-
"""Пакетний синтез голосу для «Острова Знань» (StyleTTS2-ukrainian).

Запускати інтерпретатором з venv агента 02_VOICE і з його ж папки:
    cd "G:\LOCAL AI AGENTS\02_VOICE\StyleTTS2-UA"
    .venv\Scripts\python.exe "G:\ostriv-znan\tools\gen_voice.py" --all

Чому не через Gradio: UI тримає модель у пам'яті й віддає аудіо файлом у temp.
Тут та сама логіка синтезу, що в app.py, але без UI — модель вантажиться раз
і прогонює всі кліпи.

Записує WAV 24 кГц / 16 біт / моно, тишу з країв обрізано, гучність зведено
до спільного рівня — інакше склеєні фрази («три додати два») стрибали б.
"""
import argparse
import json
import os
import re
import sys
import time
import wave
from unicodedata import normalize

import numpy as np
import torch

# Консоль Windows тут cp1251 — український print інакше вбиває скрипт.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

SR = 24000
TARGET_RMS = 0.1          # ≈ -20 dBFS: однаково для всіх кліпів
PEAK_LIMIT = 0.95
# Поріг тиші свідомо низький: кінцеві глухі приголосні («місяць», «ведмідь»)
# тихіші за 2 % від піку, і при грубішій обрізці слово втрачає хвіст —
# Whisper чув «місет» і «відміть» замість «місяць» і «ведмідь».
SILENCE = 0.008
PAD_MS = 90               # лишаємо трохи тиші, щоб кліп не починався обрізаним


def load_manifest(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def trim_and_level(wav):
    """Обрізає тишу з країв і зводить гучність."""
    if wav.size == 0:
        return wav
    env = np.abs(wav)
    thr = max(env.max() * SILENCE, 1e-4)
    idx = np.flatnonzero(env > thr)
    if idx.size:
        pad = int(SR * PAD_MS / 1000)
        wav = wav[max(0, idx[0] - pad): min(wav.size, idx[-1] + pad)]
    rms = float(np.sqrt(np.mean(wav ** 2))) or 1.0
    wav = wav * (TARGET_RMS / rms)
    peak = float(np.abs(wav).max())
    if peak > PEAK_LIMIT:
        wav = wav * (PEAK_LIMIT / peak)
    return wav


def write_wav(path, wav):
    data = (np.clip(wav, -1.0, 1.0) * 32767).astype('<i2')
    with wave.open(path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(data.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default=r'G:\ostriv-znan\tools\manifest.json')
    ap.add_argument('--out', default=r'G:\ostriv-znan\assets\voice')
    # Голос і швидкість беремо з маніфесту: у .cmd українське ім'я писати
    # не можна (запускачі — чистий ASCII, див. CLAUDE.md агентів).
    ap.add_argument('--voice', default='', help="ім'я файлу стилю з voices/ без .pt")
    ap.add_argument('--speed', type=float, default=0.0)
    ap.add_argument('--ids', default='', help='через кому; типово — усі з маніфесту')
    ap.add_argument('--text', default='', help='разовий синтез: --text "..." --name sample')
    ap.add_argument('--name', default='sample')
    ap.add_argument('--kind', default='phrase', choices=['word', 'phrase'])
    ap.add_argument('--skip-existing', action='store_true')
    ap.add_argument('--cpu', action='store_true',
                    help='рахувати на процесорі: відеокарта тут одна, і поки '
                         'на ній малює SDXL чи грає ACE-Step, модель голосу '
                         'на неї не влізе')
    args = ap.parse_args()

    man = load_manifest(args.manifest)
    if not args.voice:
        args.voice = man['voice'].get('speaker', 'Інна Гелевера')
    if not args.speed:
        args.speed = float(man['voice'].get('speed', 0.95))

    # Той самий конвеєр, що в app.py агента (див. 02_VOICE\StyleTTS2-UA\app.py)
    from ipa_uk import ipa
    from styletts2_inference.models import StyleTTS2
    from ukrainian_word_stress import Stressifier, StressSymbol
    stressify = Stressifier()

    device = 'cpu' if args.cpu or not torch.cuda.is_available() else 'cuda'
    print(f'[voice] device={device} torch={torch.__version__}', flush=True)
    t0 = time.time()
    model = StyleTTS2(hf_path='patriotyk/styletts2_ukrainian_multispeaker', device=device)
    style_path = os.path.join('voices', args.voice + '.pt')
    if not os.path.exists(style_path):
        sys.exit(f'[voice] немає голосу: {style_path}')
    style = torch.load(style_path, map_location=device)
    print(f'[voice] модель і голос «{args.voice}» завантажено за {time.time()-t0:.1f} с', flush=True)

    def synth(text, kind):
        t = text.strip().replace('"', '')
        # Кліпи-слова склеюються у фразу, тому крапка (падіння тону) їм шкодить:
        # кома лишає інтонацію рівною. Речення беремо як є.
        if kind == 'word':
            if t[-1] not in '.?!:,-':
                t += ','
        elif t[-1] not in '.?!:-':
            t += '.'
        t = t.replace('+', StressSymbol.CombiningAcuteAccent)
        t = normalize('NFKC', t)
        t = re.sub(r'[᠆‐‑‒–—―⁻₋−⸺⸻]', '-', t)
        t = re.sub(r' - ', ': ', t)
        t = stressify(t)
        ps = ipa(t)
        if not ps:
            return None
        tokens = model.tokenizer.encode(ps)
        with torch.no_grad():
            wav = model(tokens, speed=args.speed, s_prev=style)
        return trim_and_level(wav.cpu().numpy().astype(np.float32))

    os.makedirs(args.out, exist_ok=True)

    if args.text:
        jobs = [(args.name, args.text, args.kind)]
    else:
        items = man['voice']['items']
        wanted = [i.strip() for i in args.ids.split(',') if i.strip()] or list(items)
        jobs = [(i, items[i][0], items[i][1]) for i in wanted]

    done = fail = 0
    t0 = time.time()
    for cid, text, kind in jobs:
        path = os.path.join(args.out, cid + '.wav')
        if args.skip_existing and os.path.exists(path):
            continue
        try:
            wav = synth(text, kind)
            if wav is None or wav.size == 0:
                print(f'[voice] {cid}: порожній результат — пропущено', flush=True)
                fail += 1
                continue
            write_wav(path, wav)
            done += 1
            print(f'[voice] {cid:14s} {wav.size/SR:5.2f} с  «{text}»', flush=True)
        except Exception as e:                                    # noqa: BLE001
            fail += 1
            print(f'[voice] {cid}: ПОМИЛКА {e!r}', flush=True)
    print(f'[voice] готово: {done} кліпів, збоїв {fail}, {time.time()-t0:.1f} с', flush=True)


if __name__ == '__main__':
    main()
