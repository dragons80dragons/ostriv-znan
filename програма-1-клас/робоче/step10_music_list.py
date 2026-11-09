# -*- coding: utf-8 -*-
"""Крок 10. Дописує в gen_island_music.py мелодії для 34 нових островів.

Логіка та сама, що вже була: кожне море має свій тембр, острови всередині —
відтінок. Нове Море Мистецтва отримує найвиразніші тембри, але так само
тихо: це тло під завдання, а не музика, яку слухають.
Ідемпотентний: якщо острів уже в списку, не чіпає. Робить резервну копію.
"""
import io, os, re, shutil, datetime

P = r'G:\ostriv-znan\tools\gen_island_music.py'
NEW = [
    ('# Море Чисел — доповнення', None, None),
    ('num20',   'two bright marimba voices answering each other, ten and ten', 96),
    ('num100',  'rolling marimba scale upward, wide and open', 100),
    ('add100',  'steady xylophone steps, confident and even', 98),
    ('measure', 'slow glockenspiel drops like a measuring tape, careful', 84),
    ('task',    'thoughtful kalimba, a question hanging in the air', 86),
    ('data',    'tidy pizzicato grid, neat and orderly', 94),
    ('lines',   'clean sine bells drawing straight shapes, minimal', 90),
    ('# Море Мови — доповнення', None, None),
    ('stress',  'soft frame drum with one strong beat in each bar', 92),
    ('sent',    'short clarinet phrases with clear endings, speaking feel', 88),
    ('abc',     'tiny celesta ladder going up step by step', 96),
    ('mean',    'two warm flutes echoing each other, question and answer', 86),
    ('group',   'soft guitar gathering notes into little chords', 90),
    ('quest',   'curious bassoon and woodblock, asking mood', 94),
    ('text',    'quiet storytelling harp, pages turning, cosy', 80),
    ('# Море Світу — доповнення', None, None),
    ('body',    'gentle heartbeat pulse with soft mallets, warm', 82),
    ('safe',    'calm and reassuring strings, steady and safe', 84),
    ('jobs',    'light workshop rhythm, woodblocks and whistle, busy but kind', 100),
    ('signs',   'clear simple bell signals, attentive but not alarming', 90),
    ('country', 'soft bandura and gentle folk melody, warm and homely', 88),
    ('alive',   'wooden flute and growing plucked notes, spring morning', 86),
    ('animals', 'playful piccolo and light percussion, animals walking', 98),
    ('stuff',   'soft wood and glass percussion, handmade textures', 92),
    ('invent',  'curious music box turning into bright bells, discovery', 94),
    ('# Море Уваги — доповнення', None, None),
    ('info',    'airy chimes and soft breaths, senses waking up', 78),
    ('ask',     'light upward pizzicato questions, inquisitive', 90),
    ('code',    'two alternating clean tones, simple and binary', 96),
    ('true',    'balanced low strings and a small bell, weighing mood', 80),
    ('plan',    'four even kalimba steps repeating, orderly and calm', 88),
    ('card',    'quiet workshop music box, step by step', 86),
    ('# Море Мистецтва — нове море', None, None),
    ('rhythm',  'hand drums and claps alone, clear simple rhythm, no melody', 100),
    ('tempo',   'one bright mallet voice changing speed, playful', 104),
    ('instr',   'small folk ensemble taking turns, triangle drum flute', 96),
    ('notes',   'solo celesta playing a simple scale, clean and clear', 88),
    ('ornament','gentle Ukrainian folk motif on bandura and bells, decorative', 92),
]

src = io.open(P, encoding='utf-8').read()
m = re.search(r"(ISLANDS = \{\n)(.*?)(\n\}\n)", src, re.S)
assert m, 'ISLANDS не знайдено'
body = m.group(2)
lines = []
added = []
for key, text, bpm in NEW:
    if text is None:
        lines.append('    ' + key)
        continue
    if ("'%s':" % key) in body:
        continue
    lines.append("    '%s':%s(BASE + '%s', %d)," % (key, ' ' * max(1, 10 - len(key)), text, bpm))
    added.append(key)
if not added:
    print('усе вже є')
else:
    shutil.copy2(P, P + '.bak-' + datetime.datetime.now().strftime('%Y%m%d-%H%M'))
    out = src[:m.end(2)] + '\n' + '\n'.join(lines) + src[m.end(2):]
    tmp = P + '.tmp'
    io.open(tmp, 'w', encoding='utf-8').write(out)
    os.replace(tmp, P)
    print('додано мелодій:', len(added))
