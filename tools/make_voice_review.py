# -*- coding: utf-8 -*-
"""Сторінка для прослуховування всіх кліпів: tools\\voice_review.html.

Машина чує слова (verify_voice.py), але не чує наголосів і того, чи голос
приємний дитині. Ця сторінка — щоб прослухати все швидко: кнопка на кожен
кліп, окремо кнопка на склеєні фрази, які гра справді вимовляє.

Запуск:  python make_voice_review.py   (потрібен лише стандартний Python)
"""
import html
import io
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'voice_review.html')

# Те, що гра склеює з кліпів — саме тут чути, чи рівна інтонація.
CHAINS = [
    ('Лічба: 3 + 2', ['n3', 'p_plus', 'n2', 'p_together']),
    ('Лічба: було 5, забрали 2', ['p_was', 'n5', 'p_took', 'n2', 'p_left']),
    ('Букви: кіт', ['w_kit', 'p_letter', 'w_kit']),
    ('Похвала', ['ok_1']),
    ('Кінець уроку на 3 зірки', ['f_3', 'p_get', 'st_3']),
]


def main():
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as f:
        man = json.load(f)
    items = man['voice']['items']
    speaker = man['voice'].get('speaker', '')

    rows = []
    for cid, (text, kind) in items.items():
        rows.append(
            '<tr><td><button data-ids="%s">▶</button></td>'
            '<td class="id">%s</td><td>%s</td><td class="k">%s</td></tr>'
            % (cid, cid, html.escape(text), 'слово' if kind == 'word' else 'фраза'))

    chains = []
    for title, ids in CHAINS:
        words = ' '.join(items[i][0] for i in ids if i in items)
        chains.append(
            '<tr><td><button data-ids="%s">▶</button></td>'
            '<td class="id">%s</td><td>%s</td><td class="k">склеєно</td></tr>'
            % (','.join(ids), html.escape(title), html.escape(words)))

    page = """<!doctype html>
<meta charset="utf-8">
<title>Острів Знань — голос</title>
<style>
 body{font:16px/1.5 system-ui,sans-serif;margin:24px;max-width:760px;color:#173a45}
 h1{font-size:1.3rem} p{color:#55707a}
 table{border-collapse:collapse;width:100%%} td{border-bottom:1px solid #dce8ec;padding:4px 8px}
 button{font:inherit;cursor:pointer;border:1px solid #c3dde4;background:#eef7f9;border-radius:8px;padding:2px 10px}
 .id{font-family:ui-monospace,monospace;color:#2f7f99;white-space:nowrap}
 .k{color:#8aa5ad;font-size:.85rem;white-space:nowrap}
 h2{font-size:1.05rem;margin-top:28px}
</style>
<h1>Голос гри — %(speaker)s</h1>
<p>Кліпи лежать в <code>assets\\voice</code>. Гра склеює їх у фрази, тому
спершу послухайте склеєні — саме там чути, чи рівна інтонація.</p>
<h2>Склеєні фрази</h2>
<table>%(chains)s</table>
<h2>Усі кліпи (%(n)d)</h2>
<table>%(rows)s</table>
<script>
let cur = null, token = 0;
function play(ids){
  const t = ++token; let i = 0;
  if (cur) { cur.pause(); cur = null; }
  const next = () => {
    if (t !== token || i >= ids.length) return;
    const a = new Audio('../assets/voice/' + ids[i++] + '.wav');
    cur = a; a.onended = next; a.play().catch(()=>{});
  };
  next();
}
document.querySelectorAll('button[data-ids]').forEach(b =>
  b.onclick = () => play(b.dataset.ids.split(',')));
</script>
""" % {'speaker': html.escape(speaker), 'chains': ''.join(chains),
       'rows': ''.join(rows), 'n': len(items)}

    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(page)
    print('[review] %d кліпів -> %s' % (len(items), OUT))


if __name__ == '__main__':
    main()
