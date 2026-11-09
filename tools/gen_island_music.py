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
    # Море Чисел — доповнення
    'num20':     (BASE + 'two bright marimba voices answering each other, ten and ten', 96),
    'num100':    (BASE + 'rolling marimba scale upward, wide and open', 100),
    'add100':    (BASE + 'steady xylophone steps, confident and even', 98),
    'measure':   (BASE + 'slow glockenspiel drops like a measuring tape, careful', 84),
    'task':      (BASE + 'thoughtful kalimba, a question hanging in the air', 86),
    'data':      (BASE + 'tidy pizzicato grid, neat and orderly', 94),
    'lines':     (BASE + 'clean sine bells drawing straight shapes, minimal', 90),
    # Море Мови — доповнення
    'stress':    (BASE + 'soft frame drum with one strong beat in each bar', 92),
    'sent':      (BASE + 'short clarinet phrases with clear endings, speaking feel', 88),
    'abc':       (BASE + 'tiny celesta ladder going up step by step', 96),
    'mean':      (BASE + 'two warm flutes echoing each other, question and answer', 86),
    'group':     (BASE + 'soft guitar gathering notes into little chords', 90),
    'quest':     (BASE + 'curious bassoon and woodblock, asking mood', 94),
    'text':      (BASE + 'quiet storytelling harp, pages turning, cosy', 80),
    # Море Світу — доповнення
    'body':      (BASE + 'gentle heartbeat pulse with soft mallets, warm', 82),
    'safe':      (BASE + 'calm and reassuring strings, steady and safe', 84),
    'jobs':      (BASE + 'light workshop rhythm, woodblocks and whistle, busy but kind', 100),
    'signs':     (BASE + 'clear simple bell signals, attentive but not alarming', 90),
    'country':   (BASE + 'soft bandura and gentle folk melody, warm and homely', 88),
    'alive':     (BASE + 'wooden flute and growing plucked notes, spring morning', 86),
    'animals':   (BASE + 'playful piccolo and light percussion, animals walking', 98),
    'stuff':     (BASE + 'soft wood and glass percussion, handmade textures', 92),
    'invent':    (BASE + 'curious music box turning into bright bells, discovery', 94),
    # Море Уваги — доповнення
    'info':      (BASE + 'airy chimes and soft breaths, senses waking up', 78),
    'ask':       (BASE + 'light upward pizzicato questions, inquisitive', 90),
    'code':      (BASE + 'two alternating clean tones, simple and binary', 96),
    'true':      (BASE + 'balanced low strings and a small bell, weighing mood', 80),
    'plan':      (BASE + 'four even kalimba steps repeating, orderly and calm', 88),
    'card':      (BASE + 'quiet workshop music box, step by step', 86),
    # Море Мистецтва — нове море
    'rhythm':    (BASE + 'hand drums and claps alone, clear simple rhythm, no melody', 100),
    'tempo':     (BASE + 'one bright mallet voice changing speed, playful', 104),
    'instr':     (BASE + 'small folk ensemble taking turns, triangle drum flute', 96),
    'notes':     (BASE + 'solo celesta playing a simple scale, clean and clear', 88),
    'ornament':  (BASE + 'gentle Ukrainian folk motif on bandura and bells, decorative', 92),
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
    ap.add_argument('--skip-existing', action='store_true',
                    help='не переробляти мелодії, які вже лежать в assets\\music')
    args = ap.parse_args()

    ids = [i.strip() for i in args.only.split(',') if i.strip()] or list(ISLANDS)
    os.makedirs(MUSIC, exist_ok=True)
    # Без цього щогодинний перезапуск (а він потрібен, щоб робота сама
    # піднімалася після вимкнення світла) щоразу переробляв би всі
    # пʼятдесят дві мелодії — це година роботи відеокарти намарне.
    if args.skip_existing:
        was = len(ids)
        ids = [c for c in ids if not os.path.exists(os.path.join(MUSIC, c + '.mp3'))]
        print('[music] пропущено готових: %d, лишилося: %d' % (was - len(ids), len(ids)),
              flush=True)
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
