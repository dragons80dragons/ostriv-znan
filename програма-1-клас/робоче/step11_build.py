# -*- coding: utf-8 -*-
"""Крок 11. Збирає НОВУ гру на весь 1 клас: G:\\ostriv-znan\\index.html

Стара гра лишається недоторканою як демо — тепер під ім'ям `demo.html`. Нова гра — та сама
машинерія (профілі, краб, рівні, зірки, наліпки, вчительський звіт), але
52 острови в п'яти морях і поділ по чвертях.

Чому не переписуємо гру з нуля: уся складна частина — краб із CSS-ригом,
перевірка обведення по масці, профілі на планшеті, черга звітів по Wi-Fi —
уже написана й перевірена в класі. Міняється зміст, не рушій.

Куди що вставляється (порядок важить):
  1–3 вставки — перед `const LESSONS = [`: там уже оголошені WORDS, PEN,
      SYLL, BY_ID, P, say1 і решта, на що вони спираються;
  4-та вставка — ПІСЛЯ масиву SEAS, бо вона переписує LESSONS, BY_LES і
      SEAS, а BY_LES оголошено аж після LESSONS;
  далі — точкові заміни в home(), syId і wdId.
Ідемпотентний: завжди збирає з чистої `demo.html`.
"""
import io, os, re

G = r'G:\ostriv-znan'
W = r'G:\ostriv-znan\програма-1-клас\робоче'
# Чисте джерело — демоверсія. Доти вона звалася index.html, але це ім'я
# віддає GitHub Pages за кореневою адресою, тобто корінь сайту відкривав
# демо замість гри. Тепер index.html — це ЗІБРАНА гра, а чисте джерело
# лежить під власним ім'ям. Ідемпотентність від цього не постраждала:
# збірка так само щоразу починається з недоторканого demo.html.
SRC = os.path.join(G, 'demo.html')
DST = os.path.join(G, 'index.html')
PARTS = ['\u0432\u0441\u0442\u0430\u0432\u043a\u0430_1_\u043f\u0440\u043e\u043f\u0438\u0441\u0438.js',
         '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_2_\u0432\u043c\u0456\u0441\u0442.js',
         '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_3_\u043e\u0441\u0442\u0440\u043e\u0432\u0438.js']
MAP = '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_4_\u043a\u0430\u0440\u0442\u0430.js'
DRAG = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_5_'
        '\u043f\u0435\u0440\u0435\u0442\u044f\u0433\u0443\u0432\u0430\u043d\u043d\u044f.js')
DEEP = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_6_'
        '\u0437\u0430\u0433\u043b\u0438\u0431\u043b\u0435\u043d\u043d\u044f.js')
FIND = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_7_'
        '\u0437\u043d\u0430\u0439\u0434\u0438.js')
RHY = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_8_'
       '\u0440\u0438\u0442\u043c_\u043a\u0440\u0430\u043f\u043a\u0438.js')
BLD = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_9_'
       '\u0437\u0431\u0435\u0440\u0438.js')
# Шар голосу для фішок мусить іти ПОСЛІДНІМ: він загортає l.gen, а
# вставки 5, 7, 8 і 9 роблять те саме. Якби він ішов раніше, їхні
# обгортки стали б зовні, і додані ними фішки лишилися б без голосу.
VOI = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_10_'
       '\u0433\u043e\u043b\u043e\u0441.js')
# Домашнє завдання стоїть після шару голосу: завдань островів воно не
# породжує, тож обгортати його тим шаром нічого.
HWK = ('\u0432\u0441\u0442\u0430\u0432\u043a\u0430_11_'
       '\u0434\u043e\u043c\u0430\u0448\u043d\u0454.js')

s = io.open(SRC, encoding='utf-8').read()


def sub1(old, new, what):
    global s
    assert s.count(old) == 1, 'якір «%s» трапляється %d разів' % (what, s.count(old))
    s = s.replace(old, new)


# ---------- 1. назва
sub1('<title>Острів Знань</title>',
     '<title>Острів Знань — 1 клас</title>', 'title')
sub1('    <h1>Острів Знань</h1>',
     '    <h1>Острів Знань <small class="klas">1 клас</small></h1>', 'h1')
sub1('  --tint:rgba(216,238,243,.52);\n}',
     '  --tint:rgba(216,238,243,.52);\n}\n'
     '/* Додано у версії на весь 1 клас */\n'
     '.klas{font-size:.52em;opacity:.75;font-weight:600;letter-spacing:.02em}\n'
     '.terms{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 2px}\n'
     '.terms b{font:600 14px/1 var(--body);color:var(--muted)}\n'
     '.terms button{font:700 14px/1 var(--body);border:1px solid var(--line);\n'
     '  background:var(--card);color:var(--ink);border-radius:999px;padding:7px 13px;cursor:pointer}\n'
     '.terms button[aria-pressed="true"]{background:var(--sea-deep);color:#fff;border-color:var(--sea-deep)}\n'
     '.tbl{border-collapse:collapse;margin:0 auto;font:700 30px/1.15 var(--body)}\n'
     '.tbl td{border:2px solid var(--line);padding:4px 14px;text-align:center}\n'
     '.tbl td.n{min-width:54px}\n'
     '.ln{width:150px;height:90px}\n'
     '.ln path,.ln circle{stroke:#2f6fa8;stroke-width:4;fill:none;stroke-linecap:round}\n'
     '.ln circle{fill:#2f6fa8;stroke:none}\n'
     '.stave{width:170px;height:110px}\n'
     '.orn{width:120px;height:72px}\n'
     '.word.small{font-size:.62em;line-height:1.35;max-width:30ch;display:inline-block}\n'
     '.ans .big{font-size:46px;line-height:1.05;display:inline-block}\n'
     '.ans .ln,.ans .orn{width:120px;height:68px}\n'
     '.ans .stave{width:132px;height:86px}\n'
     '/* --- Перетягування. Усе велике: палець шестирічки влучає погано, */\n'
     '/* тож найменша ціль — 64 px, а місце для скидання ще більше. --- */\n'
     '.drag{display:flex;flex-direction:column;gap:14px;align-items:center}\n'
     '.drag .slots{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;width:100%}\n'
     '.drag .pool{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;\n'
     '  min-height:76px;padding:8px;border-radius:16px;background:rgba(255,255,255,.55);width:100%}\n'
     '.drag .slot{display:flex;align-items:center;gap:8px;background:var(--card);\n'
     '  border:2.5px dashed var(--line);border-radius:16px;padding:8px 12px;min-height:72px}\n'
     '.drag .slot .lab{font:700 19px/1.15 var(--body);color:var(--ink);max-width:14ch}\n'
     '.drag .slot .lab .big{font-size:40px;line-height:1;display:inline-block}\n'
     '.drag .slot .lab img.pic{width:48px;height:48px}\n'
     '.drag .slot .lab .ln,.drag .slot .lab .orn{width:96px;height:56px}\n'
     '.drag .slot .drop{display:flex;gap:6px;flex-wrap:wrap;min-width:64px;min-height:56px;\n'
     '  align-items:center;justify-content:center}\n'
     '.drag .slot.over{border-color:var(--sea-deep);background:#eaf7fb;transform:scale(1.04)}\n'
     '.drag .slot.hint{border-color:var(--sun);border-style:solid;box-shadow:0 0 0 4px rgba(242,182,50,.35)}\n'
     '.drag .slot.no{animation:shake .4s}\n'
     '.drag .chip{min-width:64px;min-height:64px;font:700 22px/1.1 var(--body);\n'
     '  background:var(--card);border:2px solid var(--line);border-radius:14px;\n'
     '  padding:6px 10px;cursor:grab;touch-action:none;color:var(--ink)}\n'
     '.drag .chip .big{font-size:40px;line-height:1}\n'
     '.drag .chip img.pic{width:48px;height:48px}\n'
     '.drag .chip .ln,.drag .chip .orn{width:96px;height:56px}\n'
     '.drag .chip.pick{border-color:var(--sea-deep);box-shadow:0 0 0 4px rgba(47,127,153,.28)}\n'
     '.drag .chip.taken{opacity:.35}\n'
     '.drag .chip.done{border-color:var(--leaf);cursor:default;opacity:1}\n'
     '.drag .chip.ghost{position:fixed;z-index:99;pointer-events:none;opacity:.95;\n'
     '  box-shadow:0 10px 22px rgba(0,0,0,.28);transform:rotate(-3deg)}\n'
     '.drag.order .slot{flex-direction:column;min-width:76px}\n'
     '.drag.order .slot.num .lab{font-size:15px;color:var(--muted)}\n'
     '.drag.basket .slot{flex-direction:column;min-width:116px;padding:10px}\n'
     '.drag.basket .slot .drop{min-height:64px}\n'
     '.drag .tip{font:600 14px/1.3 var(--body);color:var(--muted);margin:0;text-align:center}\n'
     '/* --- Заглиблення: нитка з кроків --- */\n'
     '.island.deep .got i{opacity:.28}\n'
     '.island.deep .got{letter-spacing:3px;color:var(--sea-deep)}\n'
     '.deep .path{display:flex;flex-direction:column;gap:8px;margin:12px 0 16px}\n'
     '.deep .st{display:flex;align-items:center;gap:12px;padding:10px 14px;\n'
     '  border-radius:14px;background:rgba(255,255,255,.6);border:2px solid transparent}\n'
     '.deep .st .ico{font-size:28px;line-height:1}\n'
     '.deep .st b{font:700 18px/1.2 var(--body);color:var(--muted)}\n'
     '.deep .st.got{background:#eaf7ee;border-color:var(--leaf)}\n'
     '.deep .st.got b{color:var(--ink)}\n'
     '.deep .st.now{background:var(--card);border-color:var(--sea-deep)}\n'
     '.deep .st.now b{color:var(--ink)}\n'
     '.deep .wait{color:var(--muted);font-size:17px}\n'
     '.deep .big-ok{color:var(--leaf);font-weight:800;font-size:21px}\n'
     '/* --- Знайди на картині. Сцена — поле з предметами поверх нього. --- */\n'
     '.find{display:flex;flex-direction:column;gap:8px;align-items:center;width:100%}\n'
     '.find .field{position:relative;width:100%;max-width:640px;aspect-ratio:4/3;\n'
     '  border-radius:20px;overflow:hidden;background-size:cover;background-position:center}\n'
     '.find.scn-forest .field{background:linear-gradient(#d9eeff 0 42%,#cfe9c4 42% 100%)}\n'
     '.find.scn-room   .field{background:linear-gradient(#fdf1d8 0 58%,#e8d3ae 58% 100%)}\n'
     '.find.scn-sea    .field{background:linear-gradient(#dff2fa 0 46%,#bfe3f2 46% 100%)}\n'
     '.find .field .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}\n'
     # Предмет на сцені СТОЇТЬ НА СВІТЛІЙ ПЛАШЦІ, а не просто лежить на
     # малюнку. Без неї цифри зливалися з тлом: у «знайди числа більше
     # ніж» низ сцени темно-бежевий, і темні цифри на ньому майже не
     # видно. Плашка не залежить від того, що намалював ComfyUI, —
     # контраст лишається сталим на будь-якій сцені.
     '.find .obj{position:absolute;transform:translate(-50%,-50%);\n'
     '  background:#fff;border:3px solid rgba(23,61,74,.22);border-radius:16px;\n'
     '  padding:4px 7px;cursor:pointer;color:var(--ink);\n'
     '  box-shadow:0 2px 7px rgba(0,0,0,.3);\n'
     '  min-width:54px;min-height:54px;line-height:1}\n'
     '.find .obj .big{font-size:40px;line-height:1;display:inline-block;\n'
     '  font-weight:800}\n'
     '.find .obj img.pic{width:46px;height:46px}\n'
     '.find .obj.got{border-color:var(--leaf);background:#dcf1e3}\n'
     '.find .obj.no{animation:shake .4s}\n'
     # --- Домашнє завдання: рядок зошита. Клітинки стоять в один
     # рядок і переносяться самі, якщо екран вузький.
     '/* --- Домашнє завдання: рядок прописів --- */\n'
     '.hw{display:flex;flex-direction:column;gap:12px;align-items:center}\n'
     '.hw .hwline{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}\n'
     '.hw .cell{position:relative;width:min(150px,30vw);aspect-ratio:1}\n'
     '.hw .cell canvas,.hw .cell svg{position:absolute;inset:0;width:100%;\n'
     '  height:100%;border-radius:14px}\n'
     '.hw .cell svg.glyph{background:var(--sea);border:2px solid var(--line)}\n'
     '.hw .cell canvas.ink{touch-action:none;cursor:crosshair}\n'
     '.hw .cell.model svg.glyph{background:#fff}\n'
     '.hw .cell.model .tag{position:absolute;left:50%;bottom:4px;\n'
     '  transform:translateX(-50%);font-size:12px;color:var(--ink);\n'
     '  background:rgba(255,255,255,.85);border-radius:8px;padding:1px 6px}\n'
     '.hw .cell.ok svg.glyph{border-color:var(--leaf);background:#eaf7ee}\n'
     '.hw .cell.ok::after{content:"\u2713";position:absolute;right:6px;top:2px;\n'
     '  color:var(--leaf);font:800 18px system-ui}\n'
     '.hw .cell.ok canvas.ink{pointer-events:none}\n'
     '.hw .cell.no{animation:shake .4s}\n'
     '.find .obj.hint{animation:pulse 1s infinite}\n'
     '@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(242,182,50,.8)}\n'
     '  50%{box-shadow:0 0 0 10px rgba(242,182,50,0)}}\n'
     '.find .count{font:800 20px/1 var(--body);color:var(--muted);margin:0}\n'
     '.find .count b{color:var(--sea-deep);font-size:26px}\n'
     '/* --- Ритм пальцем --- */\n'
     '.tapz{display:flex;flex-direction:column;gap:14px;align-items:center}\n'
     '.big-say{font:700 19px/1 var(--body);padding:12px 20px;border-radius:999px}\n'
     '.drum{width:190px;height:190px;border-radius:50%;border:5px solid var(--sea-deep);\n'
     '  background:var(--card);display:flex;flex-direction:column;align-items:center;\n'
     '  justify-content:center;gap:4px;cursor:pointer;touch-action:none;user-select:none}\n'
     '.drum span{font-size:62px;line-height:1}\n'
     '.drum b{font:800 19px/1 var(--body);color:var(--muted)}\n'
     '.drum.hit{animation:hit .18s}\n'
     '@keyframes hit{50%{transform:scale(.92);background:#eaf7fb}}\n'
     '/* --- Крапки по числах --- */\n'
     '.dotsz{display:flex;flex-direction:column;gap:8px;align-items:center;width:100%}\n'
     '.dotsz .board{width:100%;max-width:440px;aspect-ratio:1;background:var(--card);\n'
     '  border-radius:20px;border:2px solid var(--line)}\n'
     '.dotsz .dot circle{fill:var(--card);stroke:var(--sea-deep);stroke-width:1.4;\n'
     '  cursor:pointer}\n'
     '.dotsz .dot text{font:700 6px var(--body);fill:var(--ink);text-anchor:middle;\n'
     '  pointer-events:none}\n'
     '.dotsz .dot.got circle{fill:var(--leaf);stroke:var(--leaf)}\n'
     '.dotsz .dot.got text{fill:#fff}\n'
     '.dotsz .dot.no circle{stroke:var(--coral);stroke-width:2.6}\n'
     '.dotsz .dot.hint circle{animation:pulse 1s infinite}\n'
     '.dotsz .line{fill:none;stroke:var(--sea-deep);stroke-width:2.2;\n'
     '  stroke-linejoin:round;stroke-linecap:round}\n'
     '.dotsz .line.done{stroke:var(--leaf);stroke-width:3}\n'
     '/* --- Симетрія --- */\n'
     '.mirz{display:flex;flex-direction:column;gap:8px;align-items:center;position:relative}\n'
     '.mirz .grid{display:grid;gap:4px;background:var(--line);padding:4px;\n'
     '  border-radius:14px;position:relative}\n'
     '.mirz .cl{width:46px;height:46px;border:none;border-radius:7px;\n'
     '  background:var(--card);cursor:default;padding:0}\n'
     '.mirz .cl.right{cursor:pointer;background:#fbfdfe}\n'
     '.mirz .cl.fill{background:var(--sea-deep)}\n'
     '.mirz .cl.no{animation:shake .4s}\n'
     '.mirz .cl.hint{animation:pulse 1s infinite}\n'
     '/* Лінія згину. Без неї дитина не бачить, ДЕ саме дзеркало, і\n'
     '   завдання перетворюється на «повтори клітинки десь праворуч». */\n'
     '.mirz .cl.edge{margin-right:10px;box-shadow:14px 0 0 -4px var(--coral)}\n'
     '/* --- Збери, а не вибери --- */\n'
     '.build{display:flex;flex-direction:column;gap:14px;align-items:center;width:100%}\n'
     '.build .strip{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;\n'
     '  min-height:74px;align-items:center}\n'
     '.build .cell{min-width:74px;min-height:66px;border:3px dashed var(--line);\n'
     '  border-radius:14px;display:flex;align-items:center;justify-content:center;\n'
     '  font:800 28px/1.1 var(--body);color:var(--ink);padding:4px 10px}\n'
     '.build .cell.fill{border-style:solid;border-color:var(--leaf);background:#eaf7ee}\n'
     '.build .pool{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;\n'
     '  padding:10px;border-radius:16px;background:rgba(255,255,255,.55);width:100%}\n'
     '.build .tile{min-width:72px;min-height:64px;font:800 26px/1.1 var(--body);\n'
     '  background:var(--card);border:2px solid var(--line);border-radius:14px;\n'
     '  padding:6px 12px;cursor:pointer;color:var(--ink)}\n'
     '.build .tile.used{opacity:.3;cursor:default}\n'
     '.build .tile.no{animation:shake .4s;border-color:var(--coral)}\n'
     '.build .tile.hint{animation:pulse 1s infinite}\n'
     '.build .tip{font:600 14px/1.3 var(--body);color:var(--muted);margin:0;text-align:center}\n',
     'styles')

# ---------- 2. склади: мапа id покривала лише п'ять приголосних.
# Нові склади («ра», «то») давали б id виду sy_undefined — кліп не
# знайшовся б, і гра щоразу читала б їх синтезатором замість запису.
sub1("const syId = s => 'sy_' + {м:'m',л:'l',с:'s',к:'k',н:'n'}[s[0]] + {а:'a',о:'o',у:'u'}[s[1]];",
     "const CMAP_ = {м:'m',л:'l',с:'s',к:'k',н:'n',р:'r',т:'t',д:'d',п:'p',"
     "в:'v',б:'b',г:'h',з:'z'};\n"
     "const VMAP_ = {а:'a',о:'o',у:'u',и:'y',і:'i',е:'e'};\n"
     "const syId = s => 'sy_' + (CMAP_[s[0]] || 'x') + (VMAP_[s[1]] || 'x');",
     'syId')
sub1("const wdId = w => 'wd_' + w.split('').map(c =>\n"
     "  ({м:'m',л:'l',с:'s',к:'k',н:'n',п:'p',а:'a',о:'o',у:'u'})[c] || '').join('');",
     "const wdId = w => 'wd_' + w.split('').map(c =>\n"
     "  CMAP_[c] || VMAP_[c] || '').join('');",
     'wdId')

# ---------- 2б. кнопка-відповідь: що вважати картинкою, а що підписом.
# Демоверсія розрізняла їх за наявністю <img> і довжиною рядка. Нові
# острови дають варіанти емодзі в <span class="big"> і фігури в <svg> —
# за старим правилом вони вважалися довгим підписом і малювалися дрібним
# текстом. Рахуємо їх картинками.
sub1("      const long = !o.html.includes('<img') && [...o.html].length > 2;",
     "      const pic_ = o.html.includes('<img') || o.html.includes('<svg')\n"
     "        || o.html.includes('class=\"big\"');\n"
     "      const long = !pic_ && [...o.html].length > 2;",
     'розмір відповіді')

# ---------- 3. вставки 1–3 перед LESSONS
block = '\n\n'.join(io.open(os.path.join(W, p), encoding='utf-8').read() for p in PARTS)
sub1('const LESSONS = [', block + '\n\nconst LESSONS = [', 'перед LESSONS')

# ---------- 4. карта — після SEAS
anchor = ("   ls:['memo','logic','shadow']},\n];")
sub1(anchor, anchor + '\n\n' + io.open(os.path.join(W, MAP), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, DRAG), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, DEEP), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, FIND), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, RHY), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, BLD), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, VOI), encoding='utf-8').read()
     + '\n\n' + io.open(os.path.join(W, HWK), encoding='utf-8').read(),
     'після SEAS')

# ---------- 4в. заглиблення: нитка крізь кілька островів
# Режим живе поряд зі щоденною мандрівкою: DEEPID замість DAILY. Через це
# finish() треба навчити трьох речей — записати картку в путівник, назвати
# заглиблення на підсумковому екрані й повернути не на карту, а в нитку.
sub1('function startDaily(){\n  DAILY = true;',
     'function startDaily(){\n  DAILY = true; DEEPID = null;', 'скидання в мандрівці')
sub1('function start(id, v){\n  DAILY = false;',
     'function start(id, v){\n  DAILY = false; DEEPID = null;', 'скидання на острові')
sub1('  if (DAILY){ k.day = today(); k.trips = (k.trips || 0) + 1; }\n  else {',
     '  const dres = DEEPID ? deepFinish() : null;\n'
     '  if (DEEPID || DAILY){ if (DAILY){ k.day = today(); k.trips = (k.trips || 0) + 1; } }\n'
     '  else {', 'підсумок заглиблення')
sub1('  const gift = (s === 3 || DAILY) ? award(k) : null;',
     '  const gift = (s === 3 || DAILY || DEEPID) ? award(k) : null;', 'наліпка за крок')
sub1("  const lname = DAILY ? 'Щоденна мандрівка' : `${L.name}, ${LEVELS[lvl-1].name}`;",
     "  const lname = dres ? `${L.name}: ${dres.step.name}`\n"
     "    : DAILY ? 'Щоденна мандрівка' : `${L.name}, ${LEVELS[lvl-1].name}`;",
     'назва на підсумку')
sub1("      ${DAILY ? '' : '<button class=\"next\" id=\"again\">Ще раз</button>'\n"
     "        + '<button class=\"back\" id=\"lv\">Інший рівень</button>'}",
     "      ${dres ? '<button class=\"next\" id=\"deepbk\">'\n"
     "          + (dres.last ? 'Путівник зібрано!' : 'До нитки') + '</button>'\n"
     "        : DAILY ? '' : '<button class=\"next\" id=\"again\">Ще раз</button>'\n"
     "          + '<button class=\"back\" id=\"lv\">Інший рівень</button>'}",
     'кнопки на підсумку')
sub1("  if (!DAILY){\n    $('#again').onclick = () => start(L.id, lvl);\n"
     "    $('#lv').onclick = () => levels(L.id);\n  }",
     "  if (dres){\n"
     "    // Картка кроку лягає в путівник одразу, щоб дитина побачила,\n"
     "    // що нитка посунулася, а не просто «ще один урок».\n"
     "    const did = DEEPID; DEEPID = null;\n"
     "    $('#deepbk').onclick = () => deepScreen(did);\n"
     "  } else if (!DAILY){\n    $('#again').onclick = () => start(L.id, lvl);\n"
     "    $('#lv').onclick = () => levels(L.id);\n  }",
     'повернення в нитку')

# ---------- 4г. нитки на карті, одразу під щоденною мандрівкою
sub1("    ${SEAS.map(s => {", "    ${deepBlock()}\n    ${SEAS.map(s => {",
     'блок заглиблень на карті')
sub1("  document.querySelectorAll('.island[data-id]').forEach(b => b.onclick = () => levels(b.dataset.id));",
     "  document.querySelectorAll('.island[data-id]').forEach(b => b.onclick = () => levels(b.dataset.id));\n"
     "  document.querySelectorAll('.island[data-deep]').forEach(b =>\n"
     "    b.onclick = () => deepScreen(b.dataset.deep));",
     'натискання на нитку')

# ---------- 4б. завдання-перетягування — ще один вид поряд із memo й trace
sub1("  (t.kind === 'memo' ? showMemo : t.kind === 'trace' ? showTrace : showChoice)(t, $('#body'));",
     "  ({memo: showMemo, trace: showTrace, drag: showDrag, find: showFind,\n"
     "    tap: showTap, dots: showDots, mirror: showMirror, build: showBuild}[t.kind]\n"
     "    || showChoice)(t, $('#body'));",
     'диспетчер видів завдань')

# ---------- 5. карта показує лише чверті до поточної
sub1("""    ${SEAS.map(s => {
      const got = s.ls.reduce((a,id)=>a+lessonStars(id), 0), max = s.ls.length*9;
      return `<div class="seahead"><span class="ico">${s.ico}</span>${s.name}
        <b>${got} / ${max} ★</b></div>
      <div class="map">${s.ls.map(id => islandCard(BY_LES[id], id === NEWFLAG)).join('')}</div>`;
    }).join('')}</div>`;""",
     """    ${SEAS.map(s => {
      // Острови з наступних чвертей не ховаються назавжди: їх видно, щойно
      // вчитель перемкне чверть. Показувати все одразу не можна — 52 картки
      // першокласник оком не охопить, та й завдання ще не вчили.
      const ls = s.ls.filter(id => inTerm(BY_LES[id]));
      if (!ls.length) return '';
      const got = ls.reduce((a,id)=>a+lessonStars(id), 0), max = ls.length*9;
      return `<div class="seahead"><span class="ico">${s.ico}</span>${s.name}
        <b>${got} / ${max} ★</b></div>
      <div class="map">${ls.map(id => islandCard(BY_LES[id], id === NEWFLAG)).join('')}</div>`;
    }).join('')}</div>`;""",
     'фільтр морів')

# ---------- 6. перемикач чверті
sub1("""    <p class="lead">Обери острів. На кожному три рівні. Якщо помилишся, не страшно: з'явиться підказка.</p>""",
     """    <p class="lead">Обери острів. На кожному три рівні. Якщо помилишся, не страшно: з'явиться підказка.</p>
    <div class="terms"><b>Чверть:</b>${[1,2,3,4].map(i =>
      `<button data-t="${i}" aria-pressed="${term()===i}">${i}</button>`).join('')}
      <button data-t="0" aria-pressed="${term()===0}">усе</button></div>""",
     'перемикач чверті')
sub1("""  $('#trip').onclick = startDaily;""",
     """  document.querySelectorAll('.terms button').forEach(b =>
    b.onclick = () => setTerm(+b.dataset.t));
  $('#trip').onclick = startDaily;""",
     'обробник чверті')

# ---------- 7. щоденна мандрівка бере лише відкриті острови
sub1("  for (const l of pick(LESSONS.filter(x => x.id !== 'memo'), 5)){",
     "  for (const l of pick(LESSONS.filter(x => x.id !== 'memo' && inTerm(x)), 5)){",
     'щоденна мандрівка')

# ---------- 8. картка «Домашнє завдання» на карті
# Поряд зі «Щоденною мандрівкою», а не серед островів: це не урок із
# зірками, а тренування руки, і робити його можна скільки завгодно разів.
sub1("""      <button class="island" id="alb"><span class="ico">🏅</span><h2>Мої наліпки</h2>
        <p>Зібрано ${mine} із ${STICKERS.length}</p></button>""",
     """      <button class="island" id="hw">
        <span class="ico">${k.hw === today() ? '✅' : '✏️'}</span>
        <h2>Домашнє завдання</h2>
        <p>${k.hw === today() ? 'Сьогодні вже написано. Можна ще!'
            : 'Написати букви в рядок'}</p></button>
      <button class="island" id="alb"><span class="ico">🏅</span><h2>Мої наліпки</h2>
        <p>Зібрано ${mine} із ${STICKERS.length}</p></button>""",
     'картка домашнього')
sub1("""  $('#trip').onclick = startDaily;""",
     """  $('#hw').onclick = startHw;
  $('#trip').onclick = startDaily;""",
     'обробник домашнього')

io.open(DST + '.tmp', 'w', encoding='utf-8').write(s)
os.replace(DST + '.tmp', DST)
print('зібрано %s — %d КБ (демо: %d КБ)'
      % (os.path.basename(DST), len(s) // 1024,
         os.path.getsize(SRC) // 1024))
