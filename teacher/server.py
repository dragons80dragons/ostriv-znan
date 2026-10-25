# -*- coding: utf-8 -*-
"""Режим вчителя: роздає гру планшетам і збирає результати. Без інтернету.

Запускати на ПК вчителя ярликом «Режим вчителя.cmd» поруч. Планшети в тій
самій мережі класу відкривають адресу, яку скрипт друкує при старті —
більше нічого налаштовувати не треба: гра сама надсилає результат уроку
на той сервер, з якого її відкрили.

Що зберігається: ім'я, яке дитина вибрала в грі, назва уроку, зірки,
кількість помилок і час. Нічого іншого — ні списку пристроїв, ні того, що
дитина натискала. Усе лишається на цьому комп'ютері, у файлі
teacher\\results.jsonl (по рядку на урок, зручно для Excel через «Звіт → CSV»).

Тільки стандартна бібліотека: на планшетах і ПК нічого не встановлювати.
"""
import csv
import html
import io
import json
import os
import socket
import sys
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:                                                 # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)                      # папка з index.html
STORE = os.path.join(HERE, 'results.jsonl')
# 8777, а не 8080: на цьому ПК 8080 уже слухає інша програма на 127.0.0.1,
# і Windows дозволяє другому процесу зайняти 0.0.0.0:8080 поруч — сервер
# ніби працює, але браузер потрапляє не туди. Порт можна змінити змінною
# OSTRIV_PORT.
PORT = int(os.environ.get('OSTRIV_PORT', '8777'))
LOCK = threading.Lock()

# Порядок той самий, що на карті в грі, а не за абеткою: вчителька шукає
# урок там, де його бачила дитина. Моря — ті самі чотири групи, що на карті.
SEAS = [
    ('Числа', ['math', 'num', 'compare', 'order', 'money', 'time']),
    ('Мова',  ['read', 'syll', 'sound', 'write', 'en']),
    ('Світ',  ['world', 'weather', 'place', 'fig']),
    ('Увага', ['memo', 'logic', 'shadow']),
]
LESSON_NAMES = {
    'math': 'Лічба', 'num': 'Числа', 'compare': 'Порівняння', 'order': 'Порядок',
    'money': 'Гривня', 'time': 'Час',
    'read': 'Букви', 'syll': 'Читання', 'sound': 'Звуки', 'write': 'Письмо',
    'en': 'Англійська',
    'world': 'Природа', 'weather': 'Погода', 'place': 'Напрямки', 'fig': 'Фігури',
    'memo': "Пам'ять", 'logic': 'Візерунки', 'shadow': 'Тіні',
    'daily': 'Мандрівка',
}
LESSON_ORDER = [l for _, ls in SEAS for l in ls]
LEVELS = (1, 2, 3)
LEVEL_NAMES = {1: 'Легко', 2: 'Середньо', 3: 'Складно', 0: 'мандрівка'}


def lan_ip():
    """Адреса цього ПК у мережі класу (без інтернету теж працює)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))          # нікуди не йде, лише маршрут
        return s.getsockname()[0]
    except Exception:                                             # noqa: BLE001
        return '127.0.0.1'
    finally:
        s.close()


def rows():
    if not os.path.exists(STORE):
        return []
    out = []
    with io.open(STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def report_html():
    data = rows()
    kids = {}
    for r in data:
        k = kids.setdefault(r.get('kid', '?'),
                            {'ava': r.get('ava', ''), 'les': {}, 'trips': 0, 'last': 0})
        les = r.get('lesson', '?')
        if les == 'daily':
            k['trips'] += 1
        else:
            # Зірки тепер за рівнями: в клітинці — сума найкращих по трьох
            # рівнях, максимум дев'ять. Старі записи без «lvl» — це перший
            # рівень, саме так їх і зберігала гра до появи рівнів.
            v = k['les'].setdefault(les, {'best': {}, 'runs': 0, 'miss': 0})
            lvl = int(r.get('lvl', 1) or 1)
            v['best'][lvl] = max(v['best'].get(lvl, 0), int(r.get('stars', 0)))
            v['runs'] += 1
            v['miss'] += int(r.get('mistakes', 0))
        k['last'] = max(k['last'], int(r.get('t', 0)))

    order = LESSON_ORDER
    # Заголовок у два рядки: моря зверху, уроки під ними — так вісімнадцять
    # стовпців читаються так само, як карта в грі.
    seahead = ''.join('<th colspan="%d" class="sea">%s</th>' % (len(ls), html.escape(nm))
                      for nm, ls in SEAS)
    head = ''.join('<th>%s</th>' % html.escape(LESSON_NAMES[l]) for l in order)
    body = []
    for name, k in sorted(kids.items(), key=lambda x: -x[1]['last']):
        cells = []
        for l in order:
            v = k['les'].get(l)
            # Число з дев'яти, а не дев'ять зірочок: вісімнадцять стовпців
            # по дев'ять зірок у рядок не влазять на жоден екран.
            if v:
                got = sum(v['best'].get(n, 0) for n in LEVELS)
                cells.append('<td><b class="%s" title="спроб: %d, помилок: %d, рівні: %s">%d</b></td>'
                             % ('full' if got == 9 else '', v['runs'], v['miss'],
                                '/'.join(str(v['best'].get(n, 0)) for n in LEVELS), got))
            else:
                cells.append('<td><span class="no">—</span></td>')
        when = datetime.fromtimestamp(k['last'] / 1000).strftime('%d.%m %H:%M') if k['last'] else ''
        total = sum(sum(v['best'].values()) for v in k['les'].values())
        body.append('<tr><td class="kid">%s %s</td><td class="tot">%d</td>'
                    '<td class="trip">%s</td>%s<td class="when">%s</td></tr>'
                    % (html.escape(k['ava']), html.escape(name), total,
                       k['trips'] or '—', ''.join(cells), when))

    return """<!doctype html>
<meta charset="utf-8"><title>Острів Знань — звіт</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{font:16px/1.5 system-ui,sans-serif;margin:24px;color:#173a45;background:#f3fafc}
 h1{font-size:1.4rem;margin:0 0 4px} p.lead{color:#55707a;margin:0 0 18px}
 table{border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;
   box-shadow:0 1px 3px rgba(0,0,0,.08);width:100%%}
 th,td{border-bottom:1px solid #e3eff2;padding:6px 7px;text-align:center;vertical-align:middle}
 th{background:#eef7f9;font-size:.78rem;font-weight:600;white-space:nowrap}
 td b{font-size:1rem;color:#8aa5ad;cursor:help;font-variant-numeric:tabular-nums}
 td b.full{color:#3f9a5c}
 th.sea{background:#dcecf0;border-right:2px solid #c3dde4;font-size:.85rem}
 td.kid{text-align:left;font-weight:700;white-space:nowrap}
 td.tot{font-weight:800;color:#f2b632}
 td.trip{color:#2f7f99;font-weight:700}
 small{display:block;color:#8aa5ad;font-size:.72rem}
 .no{color:#c3dde4} .when{color:#8aa5ad;font-size:.85rem;white-space:nowrap}
 a.btn{display:inline-block;margin:16px 8px 0 0;padding:8px 14px;background:#2f7f99;color:#fff;
   border-radius:10px;text-decoration:none}
</style>
<h1>Острів Знань — звіт класу</h1>
<p class="lead">Уроків пройдено: %(n)d. Сторінка оновлюється сама що 30 секунд.
У клітинці — скільки зірок зібрано на острові з дев'яти можливих (три рівні по три).
Наведіть курсор, щоб побачити рівні окремо, спроби й помилки.</p>
<table><tr><th rowspan="2">Учень</th><th rowspan="2">Зірки</th><th rowspan="2">Мандрівок</th>
%(seahead)s<th rowspan="2">Востаннє</th></tr><tr>%(head)s</tr>%(body)s</table>
<a class="btn" href="results.csv">Завантажити CSV</a>
<a class="btn" href="/" style="background:#55707a">Відкрити гру</a>
<script>setTimeout(()=>location.reload(), 30000)</script>
""" % {'n': len(data), 'head': head, 'seahead': seahead,
       'body': ''.join(body) or '<tr><td colspan="%d">Ще нічого немає. '
                                'Відкрийте гру на планшеті й пройдіть урок.</td></tr>'
                                % (len(order) + 4)}


def diag_html():
    """Сторінка-перевірка: що саме бачить браузер на чужому пристрої.

    Тут навмисно свій, незалежний від гри, краб із тією самою CSS-анімацією:
    якщо не рухається навіть він, справа не в грі, а в пристрої чи браузері.
    """
    return """<!doctype html>
<meta charset="utf-8"><title>Перевірка руху</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{font:16px/1.5 system-ui,sans-serif;margin:16px;background:#d8eef3;color:#173a45}
 h1{font-size:1.2rem}
 .box{background:#fff;border-radius:16px;padding:16px;margin:12px 0}
 .crab{width:120px;height:120px;background:#e8684a;border-radius:24px;margin:0 auto;
   animation:sway 1.4s ease-in-out infinite}
 @keyframes sway{0%{transform:rotate(-14deg)}25%{transform:rotate(10deg) translateY(-10px)}
   50%{transform:rotate(-4deg)}75%{transform:rotate(12deg) translateY(-8px)}
   100%{transform:rotate(-14deg)}}
 table{width:100%;border-collapse:collapse}
 td{padding:5px 0;border-bottom:1px solid #e3eff2;font-size:.95rem}
 td.v{text-align:right;font-weight:700}
 .ok{color:#2e7d4f} .no{color:#c0392b}
 #sent{font-weight:700;text-align:center;margin-top:10px}
</style>
<h1>Перевірка руху</h1>
<div class="box">
  <p style="margin:0 0 10px;text-align:center">Цей червоний квадрат має
     гойдатися. Якщо він стоїть — рух вимкнено на рівні пристрою.</p>
  <div class="crab" id="c"></div>
</div>
<div class="box"><table id="t"></table><div id="sent">надсилаю…</div></div>
<script>
function run(){
  var el = document.getElementById('c');
  var seen = {}, n = 0;
  var tid = setInterval(function(){
    seen[getComputedStyle(el).transform] = 1; n++;
    if (n >= 8){
      clearInterval(tid);
      var moves = Object.keys(seen).length > 1;
      var d = {
        рухається: moves,
        прибратиАнімації: matchMedia('(prefers-reduced-motion: reduce)').matches,
        анімаційНаСторінці: (document.getAnimations ? document.getAnimations().length : -1),
        підтримка_not: CSS.supports('selector(*:not(.a *))'),
        екран: innerWidth + 'x' + innerHeight,
        браузер: navigator.userAgent,
        коли: new Date().toISOString()
      };
      var rows = '';
      for (var k in d){
        var v = d[k];
        var cls = (k === 'рухається') ? (v ? 'ok' : 'no') : '';
        rows += '<tr><td>' + k + '</td><td class="v ' + cls + '">' + v + '</td></tr>';
      }
      document.getElementById('t').innerHTML = rows;
      fetch('api/diag', {method:'POST', headers:{'Content-Type':'application/json'},
                         body: JSON.stringify(d)})
        .then(function(){ document.getElementById('sent').textContent = 'Надіслано ✓'; })
        .catch(function(){ document.getElementById('sent').textContent =
          'Не надіслалось — прочитайте таблицю вголос'; });
    }
  }, 120);
}
run();
</script>
"""


def report_csv():
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';')
    w.writerow(['Учень', 'Урок', 'Рівень', 'Зірки', 'Помилок', 'Завдань', 'Коли'])
    for r in rows():
        lvl = int(r.get('lvl', 1) or (0 if r.get('lesson') == 'daily' else 1))
        w.writerow([r.get('kid', ''), LESSON_NAMES.get(r.get('lesson'), r.get('lesson', '')),
                    LEVEL_NAMES.get(lvl, lvl),
                    r.get('stars', ''), r.get('mistakes', ''), r.get('n', ''),
                    datetime.fromtimestamp(int(r.get('t', 0)) / 1000).strftime('%d.%m.%Y %H:%M')
                    if r.get('t') else ''])
    # BOM — щоб Excel відкрив українські літери без танців із кодуванням
    return ('﻿' + buf.getvalue()).encode('utf-8')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)

    def log_message(self, fmt, *args):                 # тиша замість потоку GET
        pass

    def end_headers(self):
        # http.server не шле Cache-Control, і браузер вирішує сам, скільки
        # тримати сторінку. Планшет, який відкрив гру вчора, показував
        # учорашню версію — і виглядало це так, ніби нове просто не працює.
        # Для самої сторінки просимо щоразу перепитати; картинки, голос і
        # музику лишаємо кешованими, вони й важать найбільше.
        path = self.path.split('?', 1)[0]
        if path.endswith('.html') or path.endswith('/') or path in ('', '/teacher', '/zvit'):
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def _send(self, body, ctype='text/html; charset=utf-8', code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Шлях без «?...» і без кінцевої похилої: браузер легко додає і те,
        # і те (/teacher/?v=2), а звіт має відкритися в будь-якому випадку.
        path = self.path.split('?', 1)[0].rstrip('/')
        if path in ('/teacher', '/zvit'):
            return self._send(report_html().encode('utf-8'))
        if path == '/diag':
            return self._send(diag_html().encode('utf-8'))
        if path in ('', '/') and not os.path.exists(os.path.join(GAME, 'index.html')):
            # Папка «на флешку» містить гру одним файлом під власною назвою,
            # а index.html у ній немає — без цього браузер отримав би
            # перелік файлів замість гри.
            one = [f for f in sorted(os.listdir(GAME)) if f.lower().endswith('.html')]
            if one:
                with io.open(os.path.join(GAME, one[0]), 'rb') as f:
                    return self._send(f.read())
        if path.endswith('results.csv'):
            return self._send(report_csv(), 'text/csv; charset=utf-8')
        return super().do_GET()

    def do_POST(self):
        # Діагностика: сторінка /diag сама заміряє, що бачить браузер на
        # тому пристрої, і надсилає сюди. Інакше про чужий планшет можна
        # лише здогадуватись, а здогадки вже двічі виявились хибними.
        if self.path.startswith('/api/diag'):
            try:
                n = int(self.headers.get('Content-Length', '0'))
                raw = self.rfile.read(n).decode('utf-8')
            except Exception:                                     # noqa: BLE001
                return self._send(b'{"ok":false}', 'application/json', 400)
            with LOCK:
                with io.open(os.path.join(HERE, 'diag.jsonl'), 'a',
                             encoding='utf-8') as f:
                    f.write(raw.replace('\n', ' ') + '\n')
            return self._send(b'{"ok":true}', 'application/json')
        if not self.path.startswith('/api/report'):
            return self._send(b'no', 'text/plain; charset=utf-8', 404)
        try:
            n = int(self.headers.get('Content-Length', '0'))
            data = json.loads(self.rfile.read(n).decode('utf-8'))
            items = data if isinstance(data, list) else [data]
        except Exception:                                         # noqa: BLE001
            return self._send(b'{"ok":false}', 'application/json', 400)

        clean = []
        for it in items:
            if not isinstance(it, dict):
                continue
            clean.append({
                'kid': str(it.get('kid', ''))[:40],
                'ava': str(it.get('ava', ''))[:8],
                'lesson': str(it.get('lesson', ''))[:16],
                'lvl': max(0, min(3, int(it.get('lvl', 1) or 0))),
                'stars': int(it.get('stars', 0) or 0),
                'mistakes': int(it.get('mistakes', 0) or 0),
                'n': int(it.get('n', 0) or 0),
                't': int(it.get('t', 0) or 0),
            })
        with LOCK:
            with io.open(STORE, 'a', encoding='utf-8') as f:
                for it in clean:
                    f.write(json.dumps(it, ensure_ascii=False) + '\n')
        self._send(b'{"ok":true}', 'application/json')


class Server(ThreadingHTTPServer):
    # Типово http.server вмикає SO_REUSEADDR, і тоді другий запуск спокійно
    # стає на той самий порт поруч із першим: відповідає все одно старий
    # процес, а вчитель бачить звіт без свіжих уроків і не розуміє чому.
    # Перевірено 2026-10-21: так назбиралося п'ять живих серверів.
    allow_reuse_address = False


def main():
    ip = lan_ip()
    print('=' * 58)
    print('  Острів Знань — режим вчителя')
    print('=' * 58)
    print('  На планшетах відкрити:   http://%s:%d/' % (ip, PORT))
    print('  Звіт для вчителя:        http://%s:%d/teacher' % (ip, PORT))
    print('  Результати пишуться у:   %s' % STORE)
    print('=' * 58)
    print('  Вікно не закривати, поки триває урок. Вихід — Ctrl+C.')
    # flush: якщо вивід перенаправлено у файл, Python його буферизує
    # і адреса з'являється аж наприкінці — коли вона вже не потрібна.
    print(flush=True)
    try:
        Server(('0.0.0.0', PORT), Handler).serve_forever()
    except OSError as e:
        print()
        print('  НЕ ЗАПУСТИВСЯ: порт %d уже зайнятий (%s).' % (PORT, e))
        print('  Найімовірніше, сервер уже працює в іншому вікні — тоді')
        print('  просто відкрийте http://%s:%d/teacher' % (ip, PORT))
        print('  Якщо ні, змініть порт: set OSTRIV_PORT=8778 перед запуском.')
        sys.exit(1)


if __name__ == '__main__':
    main()
