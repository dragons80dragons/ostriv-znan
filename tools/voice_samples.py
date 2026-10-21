# -*- coding: utf-8 -*-
"""Зразки голосів: той самий текст кількома голосами, щоб вибрати один.

Завантажує модель один раз і проганяє всі голоси. Кожен файл — це реальний
склеєний ланцюжок кліпів («три» + «додати» + «два» + «Скільки буде разом?»),
бо саме так гра говорить; окремі слова звучать інакше, ніж суцільна фраза.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_voice as gv                                            # noqa: E402

import numpy as np
import torch

VOICES = sys.argv[1].split('|') if len(sys.argv) > 1 else []
OUT = sys.argv[2] if len(sys.argv) > 2 else r'G:\ostriv-znan\assets\voice\_samples'

CHAIN = [
    ('три', 'word'), ('додати', 'word'), ('два', 'word'),
    ('Скільки буде разом?', 'phrase'),
    ('Молодець!', 'phrase'),
    ('кіт', 'word'), ('З якої букви починається слово', 'word'), ('кіт', 'word'),
]
GAP = np.zeros(int(gv.SR * 0.12), dtype=np.float32)


def main():
    from ipa_uk import ipa
    from styletts2_inference.models import StyleTTS2
    from ukrainian_word_stress import Stressifier, StressSymbol
    import re
    from unicodedata import normalize
    stressify = Stressifier()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'[samples] device={device}', flush=True)
    model = StyleTTS2(hf_path='patriotyk/styletts2_ukrainian_multispeaker', device=device)
    os.makedirs(OUT, exist_ok=True)

    for vname in VOICES:
        p = os.path.join('voices', vname + '.pt')
        if not os.path.exists(p):
            print(f'[samples] немає голосу: {vname}', flush=True)
            continue
        style = torch.load(p, map_location=device)
        t0 = time.time()
        parts = []
        for text, kind in CHAIN:
            t = text.strip()
            t += ',' if kind == 'word' else '.'
            t = normalize('NFKC', t.replace('+', StressSymbol.CombiningAcuteAccent))
            t = re.sub(r' - ', ': ', t)
            ps = ipa(stressify(t))
            with torch.no_grad():
                wav = model(model.tokenizer.encode(ps), speed=0.95, s_prev=style)
            parts.append(gv.trim_and_level(wav.cpu().numpy().astype(np.float32)))
            parts.append(GAP)
        out = os.path.join(OUT, f'{vname}.wav')
        gv.write_wav(out, np.concatenate(parts))
        print(f'[samples] {vname}: {time.time()-t0:.1f} с -> {out}', flush=True)


if __name__ == '__main__':
    main()
