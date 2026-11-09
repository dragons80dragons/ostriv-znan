
// ===== ДОМАШНЄ ЗАВДАННЯ: писати букву в рядок =====
//
// Навіщо окремий режим, а не ще один острів. Острів дає пʼять РІЗНИХ
// завдань і зірку — це урок. Домашнє завдання з каліграфії влаштоване
// навпаки: одна буква, багато повторень, рядок за рядком. Саме так це
// виглядає в зошиті, і саме цього в грі не було: на острові Прописів
// дитина обводила букву ОДИН раз і йшла далі, а рука ставиться
// повторенням.
//
// Що тут свідомо зроблено інакше, ніж у прописах на острові:
//   * зразок стоїть ПЕРШИМ у рядку й лишається видимим до кінця — дитина
//     весь час має на що дивитися, як у зошиті;
//   * написане НЕ стирається після перевірки: рядок наповнюється, і видно
//     поступ — це головна нагорода тут;
//   * спроб не рахуємо й нічим не карaємо. Домашнє — це тренування, а не
//     оцінювання; острів для оцінки вже є;
//   * перевірка не на кнопку, а сама, через 900 мс після того, як палець
//     піднявся. Кнопку «Готово» шестирічка на кожну букву тиснути не
//     буде, а миттєва перевірка ламала б букви з двох штрихів (т, ж):
//     дитина підняла палець, щоб почати другий, — а їй уже «не вийшло».

const HW_ROWS = 3;          // рядків у завданні
const HW_CELLS = 4;         // скільки разів написати в рядку, крім зразка
const HW_S = 220;           // внутрішній розмір клітинки

// Букви беремо ті, які вже вчили: чверть визначає межу. Велика літера —
// з третьої чверті, бо до того її в прописах не дають.
function hwPick(){
  const t = term();
  const upto = t === 0 ? 7 : Math.min(7, 1 + t * 2);
  const low = (t === 0 ? ALL_LOW : LET_GROUPS.slice(0, upto).flat()).filter(c => PEN[c]);
  const up = (t === 0 || t >= 3) ? ALL_UP.filter(c => PEN[c]) : [];
  const pool = low.concat(up);
  return pick(pool, Math.min(HW_ROWS, pool.length));
}

let HWSET = [], HWI = 0;

// Лінійки в косу — ті самі, що на острові Прописів, щоб зошит був один
// і той самий. Числа не виношу в змінні: це малюнок, не налаштування.
function hwRules(){
  return [18, 35, 72, 90].map(y =>
      `<line class="rl" x1="2" y1="${y}" x2="98" y2="${y}"/>`).join('')
    + [10, 26, 42, 58, 74, 90].map(x =>
      `<line class="sl" x1="${x}" y1="90" x2="${x + 10}" y2="18"/>`).join('');
}

function hwGlyphSvg(glyph, model){
  const strokes = PEN[glyph] || [];
  const lay = cls => strokes.map(d => `<path class="${cls}" d="${d}"/>`).join('');
  // Зразок: доріжка, пунктир і сама буква. Клітинка для письма — лише
  // доріжка з пунктиром, букви в ній немає, бо її й треба написати.
  return `<svg class="glyph" viewBox="${PEN_VB.join(' ')}" aria-hidden="true">
    ${hwRules()}
    <g class="let" style="--road:12">
      ${lay('road')}${lay('dash')}${model ? lay('pen') : ''}
    </g></svg>`;
}

function startHw(){
  HWSET = hwPick();
  HWI = 0;
  if (!HWSET.length) return home();
  hwRow();
}

function hwRow(){
  const ch = HWSET[HWI];
  const name = LET_NAME[ch.toLowerCase()] || ch;
  const big = ch !== ch.toLowerCase();
  const prompt = `Напиши ${big ? 'велику букву' : 'букву'} ${ch} в рядок`;
  scene('lesson');
  $('#app').innerHTML = `<section class="lesson">
    <div class="bar"><button class="back" id="back">← Карта</button>
      <div class="progress">${HWSET.map((_, i) =>
        `<span class="${i < HWI ? 'done' : i === HWI ? 'now' : ''}"></span>`).join('')}</div></div>
    <div class="q"><h3>${prompt}</h3>
      <button class="say" id="say" aria-label="Послухати ще раз">🔊</button></div>
    <div id="body"><div class="hw">
      <div class="hwline">
        <div class="cell model">${hwGlyphSvg(ch, true)}<span class="tag">зразок</span></div>
        ${Array.from({length: HW_CELLS}, (_, i) =>
          `<div class="cell" data-i="${i}">${hwGlyphSvg(ch, false)}
            <canvas class="ink"></canvas></div>`).join('')}
      </div>
      <div class="row"><button class="back" id="undo">Стерти останню</button></div>
    </div></div>
    <p class="msg" id="msg" aria-live="polite"></p></section>`;

  const line = [['q_hwrow', 'Напиши букву в рядок, як зразок'],
                [big ? letVoUp(ch.toLowerCase()) : letVo(ch.toLowerCase()), name]];
  $('#say').onclick = () => say(line);
  say(line);
  $('#back').onclick = home;

  const cells = [...document.querySelectorAll('.hw .cell[data-i]')];
  let done = 0, order = [];
  cells.forEach(c => hwCell(c, ch, () => {
    done++; order.push(c);
    if (done < cells.length) return;
    const msg = $('#msg');
    msg.className = 'msg good'; msg.textContent = 'Рядок готовий!';
    sfxOk(); say([['q_hwdone', 'Рядок готовий!']]);
    guide(CRAB.good, false);
    setTimeout(() => { HWI++; HWI < HWSET.length ? hwRow() : hwFin(); }, 1400);
  }));
  $('#undo').onclick = () => {
    const c = order.pop();
    if (!c){ const msg = $('#msg'); msg.className = 'msg'; msg.textContent = 'Ще нічого не написано'; return; }
    done--; c.classList.remove('ok'); c._hwReset();
  };
}

// Одна клітинка: обведення пальцем і самоперевірка. Міряємо тим самим
// способом, що й прописи на острові, — двома масками поза екраном.
function hwCell(cell, glyph, onOk){
  const S = HW_S, strokes = PEN[glyph] || [];
  const ic = cell.querySelector('canvas.ink');
  ic.width = ic.height = S;
  const k = ic.getContext('2d');
  k.lineWidth = 18; k.lineCap = 'round'; k.lineJoin = 'round'; k.strokeStyle = '#e8684a';

  const mask = document.createElement('canvas'); mask.width = mask.height = S;
  const m = mask.getContext('2d');
  m.setTransform(...penMatrix(S));
  m.lineCap = 'round'; m.lineJoin = 'round'; m.strokeStyle = '#000';
  const paint = w => { m.lineWidth = w; for (const d of strokes) m.stroke(new Path2D(d)); };
  paint(5);
  const strict = m.getImageData(0, 0, S, S).data;
  paint(20);                              // доріжка плюс товщина пальця
  const wide = m.getImageData(0, 0, S, S).data;

  let drawing = false, last = null, painted = false, locked = false, wait = null;
  const pt = e => { const r = ic.getBoundingClientRect();
    return [(e.clientX - r.left) * S / r.width, (e.clientY - r.top) * S / r.height]; };
  const clear = () => { k.clearRect(0, 0, S, S); painted = false; };
  cell._hwReset = () => { locked = false; clear(); };

  ic.addEventListener('pointerdown', e => {
    if (locked) return;
    try { ic.setPointerCapture(e.pointerId); } catch(err){}
    if (wait){ clearTimeout(wait); wait = null; }
    drawing = true; last = pt(e); painted = true;
    k.beginPath(); k.moveTo(last[0], last[1]); k.lineTo(last[0] + 0.1, last[1]); k.stroke();
  });
  ic.addEventListener('pointermove', e => {
    if (!drawing || locked) return;
    const p = pt(e);
    k.beginPath(); k.moveTo(last[0], last[1]); k.lineTo(p[0], p[1]); k.stroke(); last = p;
  });
  const stop = () => {
    if (!drawing) return;
    drawing = false;
    // Пауза перед перевіркою: буква може бути з двох штрихів.
    if (wait) clearTimeout(wait);
    wait = setTimeout(check, 900);
  };
  ic.addEventListener('pointerup', stop);
  ic.addEventListener('pointercancel', stop);

  function check(){
    wait = null;
    if (locked || !painted) return;
    const ink = k.getImageData(0, 0, S, S).data;
    let hit = 0, need = 0, stray = 0, all = 0;
    for (let i = 3; i < ink.length; i += 4){
      const on = ink[i] > 40;
      if (strict[i] > 40){ need++; if (on) hit++; }
      if (on){ all++; if (wide[i] <= 40) stray++; }
    }
    const cover = need ? hit / need : 0, out = all ? stray / all : 1;
    const msg = $('#msg');
    // М'якше, ніж на острові: домашнє — тренування руки, а не залік.
    if (cover >= .5 && out <= .45){
      locked = true;
      cell.classList.add('ok');
      sfxOk();
      msg.className = 'msg good'; msg.textContent = 'Гарно!';
      onOk();
    } else {
      cell.classList.add('no');
      setTimeout(() => cell.classList.remove('no'), 420);
      sfxNo();
      msg.className = 'msg bad';
      msg.textContent = cover < .5 ? 'Веди по пунктиру — від крапки'
                                   : 'Старайся не виходити за доріжку';
      clear();
    }
  }
}

function hwFin(){
  const k = kid();
  k.hw = today();
  k.hwn = (k.hwn || 0) + 1;
  // award повертає [наліпка, чи вона нова]; сама наліпка — [id, емодзі].
  const [st] = award(k);
  save();
  scene('lesson'); playTune('theme');
  $('#app').innerHTML = `<section class="lesson">
    <h3 style="font-family:var(--display);margin:0">Домашнє завдання виконано</h3>
    <p class="lead">Написано ${HWSET.length} ${HWSET.length === 1 ? 'рядок' : 'рядки'}:
      ${HWSET.map(c => `<b>${c}</b>`).join(', ')}</p>
    ${st ? `<p class="lead">Наліпка в альбом:
      <span class="big">${pic(st[0], st[1])}</span></p>` : ''}
    <div class="row"><button class="next" id="more">Ще рядок</button>
      <button class="back" id="toMap">На карту</button></div></section>`;
  say([['q_hwfin', 'Домашнє завдання виконано. Молодець!']]);
  guide(CRAB.fin3, false);
  $('#more').onclick = startHw;
  $('#toMap').onclick = home;
}
