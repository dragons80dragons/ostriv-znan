// ===== РИТМ ПАЛЬЦЕМ, КРАПКИ ПО ЧИСЛАХ, СИМЕТРІЯ =====
//
// Три завдання з одного пункту `РІЗНОМАНІТТЯ.md`: кінестетичний канал,
// якого в грі майже не було. Усі три не потребують жодного файлу —
// звук береться з того самого WebAudio, що й «правильно / помилка»,
// а малюнки — SVG.

// ---------- 1. РИТМ: гра плеще, дитина повторює пальцем
//
// Чому не «вибери правильний запис», як було на Острові Ритму: вибір із
// трьох рядків нот перевіряє впізнавання, а не відчуття ритму. Тут
// дитина відтворює — і це єдине завдання в грі, де рука має влучити
// не в місце, а в ЧАС.
//
// Як оцінюється. Абсолютний темп не важить: шестирічка повторить
// повільніше чи швидше, і це не помилка. Важить МАЛЮНОК — де довго, а
// де коротко. Тому проміжки між дотиками переводяться у «довгий /
// короткий» відносно найкоротшого, і порівнюється вже рядок.
// ВАЖЛИВО: тривалість ОСТАННЬОЇ ноти дотиком не виміряти — між нею й
// нічим немає проміжку. Тому ритми мусять різнитися вже першими n−1
// тривалостями, інакше два різні записи дають однаковий малюнок і
// рівне постукування проходить обидва. Перевірено: «♩ ♩ ♩» і «♪♪ ♩»
// обидва давали «SS», і другий зараховувався за рівний ритм.
const TAPPAT = [
  ['♩ ♩ ♩',     [.34, .34, .34]],      // SS
  ['♩ ♪♪',      [.34, .16, .16]],      // LS
  ['♪♪ ♩ ♩',    [.16, .16, .34, .34]], // SSL
  ['♩ ♪♪ ♩',    [.34, .16, .16, .34]], // LSS
  ['♩ ♩ ♪♪',    [.34, .34, .16, .16]], // LLS
  ['♪♪ ♩ ♪♪',   [.16, .16, .34, .16, .16]], // SSLS
];
// Малюнок ритму рядком: S — коротко, L — довго. Беремо проміжки МІЖ
// ударами, тому їх на один менше, ніж ударів.
const shape = gaps => {
  const lo = Math.min(...gaps);
  return gaps.map(g => g > lo * 1.45 ? 'L' : 'S').join('');
};
function tapTask(v){
  const pool = v === 1 ? TAPPAT.slice(0, 3) : TAPPAT;
  const [label, durs] = pool[rnd(pool.length)];
  return {kind:'tap', prompt:'Послухай і повтори пальцем',
    speak:[['q_tap', 'Послухай плескання, а тоді повтори його пальцем']],
    label, durs};
}
function showTap(t, host){
  const n = t.durs.length;
  // Проміжки, які гра ЗАГАДУЄ: між ударами лежить тривалість попереднього.
  const want = shape(t.durs.slice(0, -1));
  host.innerHTML = `<div class="tapz">
    <button class="say big-say" type="button" id="hear">🔊 Послухати</button>
    <button class="drum" id="drum"><span>🥁</span><b id="tcnt">0 з ${n}</b></button>
    <p class="tip">Торкайся барабана стільки ж разів і так само: де довго, а де коротко.</p>
    </div>`;
  const msg = $('#msg');
  let taps = [], tries = 0;
  const play = () => {
    let t0 = 0;
    for (const d of t.durs){
      setTimeout(() => beep([[523, d]], .14), t0 * 1000);
      t0 += d + .12;
    }
  };
  $('#hear').onclick = play;
  setTimeout(play, 600);

  const drum = $('#drum');
  drum.addEventListener('pointerdown', e => {
    e.preventDefault();
    if (taps.length >= n) return;
    taps.push(performance.now());
    drum.classList.remove('hit'); void drum.offsetWidth; drum.classList.add('hit');
    beep([[523, .09]], .12);
    $('#tcnt').textContent = taps.length + ' з ' + n;
    if (taps.length < n) return;
    const gaps = taps.slice(1).map((x, i) => x - taps[i]);
    const ok = shape(gaps) === want;
    if (ok){
      sfxOk(); guide(CRAB.good, false); pass(host);
    } else {
      tries++; mistakes++; sfxNo(); guide(CRAB.oops, false);
      taps = []; $('#tcnt').textContent = '0 з ' + n;
      msg.className = 'msg bad';
      if (tries === 1){
        msg.textContent = 'Майже! Послухай ще раз і спробуй';
        say([P.tryagain]); setTimeout(play, 700);
      } else {
        // З другого разу показуємо малюнок ритму очима — так само, як в
        // інших завданнях гра після двох спроб показує правильне.
        msg.innerHTML = 'Підказка: ось такий ритм — <b>' + t.label + '</b>';
        say([P.hint]); setTimeout(play, 700);
      }
    }
  });
}

// ---------- 2. КРАПКИ ПО ЧИСЛАХ
//
// Дитина натискає крапки за порядком чисел, і з них проявляється
// малюнок. Лічба тут не самоціль, а спосіб щось отримати — тому
// натиснути «3» після «2» хочеться.
// Жодна крапка не має збігатися з іншою: номери малюються в самій
// крапці, і два однакові місця ховають один номер під іншим. Перевірено
// на метелику й човнику — у них я спершу повторив початкову крапку, і
// номер 1 зник під номером 9.
const DOTS = {
  5:  [['будиночок', [[26,62],[26,86],[74,86],[74,62],[50,38]]],
       ['човник',    [[14,58],[86,58],[74,80],[26,80],[50,36]]]],
  7:  [['ялинка',    [[50,12],[72,42],[60,36],[82,72],[18,72],[40,36],[28,42]]],
       ['рибка',     [[18,52],[40,34],[64,32],[84,44],[84,62],[60,72],[36,66]]]],
  10: [['зірка',     [[50,12],[58,38],[86,38],[63,54],[72,82],[50,65],
                      [28,82],[37,54],[14,38],[42,38]]],
       ['метелик',   [[50,28],[32,12],[16,32],[30,48],[50,46],[70,48],
                      [84,32],[68,12],[50,70],[50,86]]]],
};
// Крапки мають стояти не ближче ніж на 11 одиниць одна від одної:
// номер малюється в самій крапці, і сусіди злипаються в кашу.
function dotsTask(v){
  const n = v === 1 ? 5 : v === 2 ? 7 : 10;
  const [name, pts] = DOTS[n][rnd(DOTS[n].length)];
  return {kind:'dots', prompt:`Зʼєднай крапки за порядком — від 1 до ${n}`,
    speak:[['q_dots', 'Натискай крапки за порядком чисел, і проявиться малюнок']],
    name, pts};
}
function showDots(t, host){
  const n = t.pts.length;
  host.innerHTML = `<div class="dotsz">
    <svg viewBox="0 0 100 100" class="board">
      <polyline class="line" points=""/>
      ${t.pts.map((p, i) =>
        `<g class="dot" data-i="${i}"><circle cx="${p[0]}" cy="${p[1]}" r="6"/>
         <text x="${p[0]}" y="${p[1] + 2.6}">${i + 1}</text></g>`).join('')}
    </svg>
    <p class="count"><b id="dcnt">1</b> → ${n}</p></div>`;
  const msg = $('#msg');
  const line = host.querySelector('.line');
  let next = 0, tries = 0;
  host.querySelectorAll('.dot').forEach(g => g.addEventListener('pointerdown', e => {
    e.preventDefault();
    const i = +g.dataset.i;
    if (i < next) return;
    if (i !== next){
      tries++; mistakes++; sfxNo(); guide(CRAB.oops, false);
      g.classList.remove('no'); void g.offsetWidth; g.classList.add('no');
      msg.className = 'msg bad';
      if (tries === 1){ msg.textContent = 'Не ця — шукай наступне число'; say([P.tryagain]); }
      else {
        host.querySelector(`.dot[data-i="${next}"]`).classList.add('hint');
        msg.textContent = 'Підказка: потрібна крапка блимає'; say([P.hint]);
      }
      return;
    }
    g.classList.add('got');
    g.classList.remove('hint');
    line.setAttribute('points',
      t.pts.slice(0, i + 1).map(p => p.join(',')).join(' '));
    next++;
    sfxTap();
    $('#dcnt').textContent = Math.min(next + 1, n);
    if (next === n){
      // Останній штрих: замикаємо лінію і підписуємо, що вийшло —
      // заради цього дитина й рахувала.
      line.classList.add('done');
      msg.className = 'msg good';
      msg.textContent = 'Вийшов(ла) ' + t.name + '!';
      sfxOk(); guide(CRAB.good, false); pass(host, false);
    }
  }));
}

// ---------- 3. СИМЕТРІЯ: домалюй другу половину
//
// Ліва половина сітки зафарбована, дитина має повторити її дзеркально
// праворуч. Тема «симетрія в геометричних фігурах» є в програмі
// (додаткові теми математики), і показати її інакше, ніж дією, важко.
function mirrorTask(v){
  const H = 6, Wd = 3;                       // висота й половина ширини
  const k = v === 1 ? 5 : v === 2 ? 7 : 9;   // скільки клітинок зафарбовано
  const cells = new Set();
  while (cells.size < k) cells.add(rnd(H) * Wd + rnd(Wd));
  return {kind:'mirror', prompt:'Домалюй другу половину — щоб вийшло дзеркально',
    speak:[['q_mirror', 'Домалюй другу половину так, щоб половинки були однакові']],
    h:H, w:Wd, cells:[...cells]};
}
function showMirror(t, host){
  const H = t.h, Wd = t.w, full = Wd * 2;
  const left = new Set(t.cells);
  const need = t.cells.length;
  const cell = (r, c) => {
    const mirrored = c >= Wd;
    const lc = mirrored ? full - 1 - c : c;
    const on = left.has(r * Wd + lc);
    return `<button class="cl${!mirrored && on ? ' fill' : ''}${mirrored ? ' right' : ''}${c === Wd - 1 ? ' edge' : ''}"
      data-r="${r}" data-c="${c}" data-on="${on ? 1 : 0}"
      ${mirrored ? '' : 'disabled'}></button>`;
  };
  host.innerHTML = `<div class="mirz">
    <div class="grid" style="grid-template-columns:repeat(${full},1fr)">
      ${Array.from({length:H}, (_, r) =>
        Array.from({length:full}, (_, c) => cell(r, c)).join('')).join('')}
    </div>
    
    <p class="count"><b id="mcnt">0</b> з ${need}</p></div>`;
  const msg = $('#msg');
  let got = 0, tries = 0;
  host.querySelectorAll('.cl.right').forEach(b => b.onclick = () => {
    if (b.classList.contains('fill')) return;
    if (b.dataset.on === '1'){
      b.classList.add('fill'); got++; $('#mcnt').textContent = got;
      sfxTap();
      if (got === need){ sfxOk(); guide(CRAB.good, false); pass(host); }
      else { msg.className = 'msg good'; msg.textContent = 'Так!'; }
    } else {
      tries++; mistakes++; sfxNo(); guide(CRAB.oops, false);
      b.classList.remove('no'); void b.offsetWidth; b.classList.add('no');
      msg.className = 'msg bad';
      if (tries === 1){ msg.textContent = 'Тут порожньо — подивись на ліву половину'; say([P.tryagain]); }
      else {
        const left_ = [...host.querySelectorAll('.cl.right[data-on="1"]:not(.fill)')];
        if (left_.length) left_[0].classList.add('hint');
        msg.textContent = 'Підказка: потрібна клітинка блимає'; say([P.hint]);
      }
    }
  });
}

// ---------- Куди це поставити
const RHY_BY_ISLAND = {
  rhythm: [tapTask], tempo: [tapTask],
  math: [dotsTask], num20: [dotsTask], order: [dotsTask], write: [dotsTask],
  lines: [mirrorTask, dotsTask], fig: [mirrorTask], logic: [mirrorTask],
};
for (const l of LESSONS){
  const mk = RHY_BY_ISLAND[l.id];
  if (!mk) continue;
  const base = l.gen;
  l.gen = function (v){
    const t = base(v);
    try { t[t.length - 1] = mk[rnd(mk.length)](v); } catch (e) {}
    return shuffle(t);
  };
}
