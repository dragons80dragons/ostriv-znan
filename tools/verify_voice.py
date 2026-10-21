# -*- coding: utf-8 -*-
"""Замкнене коло: синтезовані кліпи -> Whisper -> порівняння з текстом.

Це не оцінка голосу (краси й наголосів машина не чує), а перевірка, що в
кожному файлі справді сказано те, що мало бути: не тиша, не обрізане слово,
не чуже слово. Той самий прийом, яким перевіряли парк агентів.

Запускати інтерпретатором з venv агента 04_STT і з його ж папки, щоб
підхопилися DLL cuDNN:

    "6 Перевірка голосу.cmd"
"""
import json
import os
import re
import sys
import unicodedata

from faster_whisper import WhisperModel

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(os.path.dirname(ROOT), 'assets', 'voice')


def norm(s):
    s = unicodedata.normalize('NFKC', s.lower())
    s = s.replace('’', "'").replace('ʼ', "'")
    s = re.sub(r"[^\w' ]+", ' ', s, flags=re.UNICODE)
    return ' '.join(s.split())


def main():
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        items = json.load(f)['voice']['items']

    # int8_float32, а не float16: CTranslate2 на Pascal відмовляє
    # («target device or backend do not support efficient float16»).
    # Той самий тип стоїть у app.py агента 04_STT.
    model = WhisperModel('large-v3-turbo', device='cuda',
                         compute_type='int8_float32')
    print('[перевірка] модель завантажено', flush=True)

    bad = []
    for cid, (text, _kind) in items.items():
        path = os.path.join(VOICE, cid + '.wav')
        if not os.path.exists(path):
            bad.append((cid, text, 'НЕМАЄ ФАЙЛУ'))
            continue
        segs, _ = model.transcribe(path, language='uk', beam_size=5)
        heard = norm(' '.join(s.text for s in segs))
        want = norm(text)
        if heard == want:
            print('[ok] %-14s «%s»' % (cid, text), flush=True)
        else:
            bad.append((cid, text, heard))
            print('[??] %-14s мало бути «%s», почуто «%s»' % (cid, text, heard),
                  flush=True)

    print('\nЗбігів: %d з %d' % (len(items) - len(bad), len(items)))
    if bad:
        print('Перевірити вухом: %s' % ', '.join(b[0] for b in bad))
        print('(розбіжність не завжди помилка: Whisper плутає короткі слова '
              'без контексту й пише числа цифрами)')


if __name__ == '__main__':
    main()
