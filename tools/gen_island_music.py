# -*- coding: utf-8 -*-
"""Своя мелодія для кожного острова.

Запускає gen_music.py вісімнадцять разів із різними описами й зводить
результат у MP3: вісімнадцять WAV по 5 МБ ніхто на планшети не понесе,
а 96 кбіт/с для тихого фону під уроком чути неможливо.

Треки навмисно короткі (30 с) і без ударних у більшості островів: це тло
під завдання, а не музика, яку слухають. Якщо мелодія перетягує увагу на
себе, дитина перестає чути голос.

Запуск (довго, близько пів години):
    "<python>" gen_island_music.py
    "<python>" gen_island_music.py --only math,read
"""
import argparse
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
MUSIC = os.path.join(PROJ, 'assets', 'music')
BASE = ('gentle instrumental background music for a children game, '
        'soft and quiet, simple melody, no vocals, ')

# (опис, темп). Кожне море має свій тембр, а острови всередині —
# відтінок: так дитина впізнає, куди припливла, навіть не дивлячись.
ISLANDS = {
    # Море Чисел — дзвіночки й маримба, світле й рахункове
    'math':    (BASE + 'music box and marimba, curious and bright', 96),
    'num':     (BASE + 'marimba and soft claps, playful counting feel', 100),
    'compare': (BASE + 'two alternating xylophone voices, balanced', 92),
    'order':   (BASE + 'tiny toy march, pizzicato strings, orderly', 104),
    'money':   (BASE + 'light accordion and triangle, market morning', 98),
    'time':    (BASE + 'soft clock ticking, celesta, calm and steady', 88),
    # Море Мови — дерев'яні духові й голосні теплі тембри
    'read':    (BASE + 'warm clarinet and soft guitar, friendly', 90),
    'syll':    (BASE + 'simple recorder melody, like a nursery song', 94),
    'sound':   (BASE + 'hand claps and wood blocks, rhythmic and light', 102),
    'write':   (BASE + 'quiet piano, slow and careful, pencil mood', 80),
    'en':      (BASE + 'ukulele and whistle, travel and sunshine', 100),
    # Море Світу — природа, флейти, повітря
    'world':   (BASE + 'wooden flute and bird whistles, forest morning', 86),
    'weather': (BASE + 'airy pads, rain sticks and chimes, changing sky', 84),
    'place':   (BASE + 'plucked strings wandering up and down, searching', 92),
    'fig':     (BASE + 'clean bells in simple geometric patterns', 96),
    # Море Уваги — тихе, зосереджене
    'memo':    (BASE + 'very quiet vibraphone, spacious and calm', 76),
    'logic':   (BASE + 'repeating pattern on kalimba, puzzle mood', 90),
    'shadow':  (BASE + 'soft low strings and harp, gentle mystery', 78),
}


def run(cid, prompt, bpm, dur, keep):
    # Зведенням у MP3 займається сам gen_music.py: він бачить розширення
    # у --file. Тут лишилося тільки сказати, з яким бітрейтом.
    mp3 = os.path.join(MUSIC, cid + '.mp3')
    cmd = [sys.executable, os.path.join(ROOT, 'gen_music.py'),
           '--prompt', prompt, '--bpm', str(bpm), '--dur', str(dur),
           '--file', cid + '.mp3', '--bitrate', '96k']
    if keep:
        cmd.append('--keep')            # лишити сирий трек ACE-Step
    r = subprocess.run(cmd)
    return mp3 if r.returncode == 0 and os.path.exists(mp3) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='через кому; типово — усі')
    ap.add_argument('--dur', type=int, default=30)
    ap.add_argument('--keep-raw', action='store_true',
                    help='не видаляти сирий трек ACE-Step у tools\\_music')
    args = ap.parse_args()

    ids = [i.strip() for i in args.only.split(',') if i.strip()] or list(ISLANDS)
    os.makedirs(MUSIC, exist_ok=True)
    t0 = time.time()
    done = fail = 0
    for k, cid in enumerate(ids, 1):
        if cid not in ISLANDS:
            print('[music] невідомий острів: %s' % cid, flush=True)
            continue
        prompt, bpm = ISLANDS[cid]
        print('[music] %2d/%d %-8s %s' % (k, len(ids), cid, prompt[60:100]), flush=True)
        t1 = time.time()
        mp3 = run(cid, prompt, bpm, args.dur, args.keep_raw)
        if mp3:
            done += 1
            print('[music] %-8s готово за %.0f с -> %s (%d КБ)'
                  % (cid, time.time() - t1, os.path.basename(mp3),
                     os.path.getsize(mp3) // 1024), flush=True)
        else:
            fail += 1
            print('[music] %-8s збій' % cid, flush=True)
    print('[music] разом: %d мелодій, збоїв %d, %.1f хв'
          % (done, fail, (time.time() - t0) / 60), flush=True)
    # Останнім ділом зрівнюємо гучність: ACE-Step видає треки з розкидом
    # у чотири децибели, і перехід між островами чути як стрибок.
    if done:
        subprocess.run([sys.executable, os.path.join(ROOT, 'level_music.py')])


if __name__ == '__main__':
    main()
