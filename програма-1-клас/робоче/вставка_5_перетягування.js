// ===== ПЕРЕТЯГУВАННЯ: зʼєднай пари, розклади по кошиках, постав у ряд =====
//
// Навіщо. У грі було 97 % завдань одного вигляду: натисни один варіант із
// кількох. Жест один, і скільки б островів не додавати, рука дитини робить
// те саме. Тут зʼявляються три нові жести. Матеріал для них уже є: в Oak
// National Academy 1 213 завдань типу `match` і 297 типу `order`.
//
// Як це працює на планшеті (HP Elite x2, пальці шестирічки):
//   • тягнути МОЖНА, але НЕ ОБОВʼЯЗКОВО — те саме робиться двома
//     дотиками: торкнувся фішки, торкнувся місця. Частина дітей тягне
//     погано, і без другого способу завдання було б для них непрохідним;
//   • події вказівника (pointer events), а не миші — інакше на сенсорному
//     екрані не працює зовсім;
//   • фішка під пальцем — це КОПІЯ, що летить над сторінкою. Рухати
//     оригінал не можна: він лежить у сітці, і сітка стрибала б;
//   • палець затуляє те, що тягне, тому копія підведена вгору на 28 px;
//   • помилка повертає фішку назад і працює так само, як у звичайних
//     завданнях: перша — «спробуй ще», друга — підказує правильне місце.

// ---------- Побудова завдань
// Спільний вигляд: items — що тягнемо, slots — куди. У кожної фішки `to`
// каже, в яке місце вона має лягти.
function dragTask(kind, prompt, speak, slots, items, extra){
  return Object.assign({kind, prompt, speak, slots, items,
    // options потрібні, щоб кнопка 🔊 вгорі прочитала всі підписи:
    // show() збирає її саме з options.
    options: items.concat(slots).filter(x => x.vo && x.tx)}, extra || {});
}
// Пари: ліворуч нерухомі картки з порожнім місцем, праворуч купка фішок.
// Ліній пальцем не малюємо — на планшеті це найважчий жест із можливих.
const pairTask = (prompt, speak, rows) =>
  dragTask('drag', prompt, speak,
    shuffle(rows).map(r => ({id:'s_' + r.key, html:r.left, vo:r.leftVo, tx:r.leftTx})),
    shuffle(rows).map(r => ({id:'i_' + r.key, html:r.right, vo:r.rightVo, tx:r.rightTx,
                             to:'s_' + r.key})),
    {layout:'pair'});
// Кошики: 2–3 підписані місця, кожне вміщає кілька фішок.
const basketTask = (prompt, speak, baskets, items) =>
  dragTask('drag', prompt, speak,
    baskets.map(b => ({id:'s_' + b.id, html:b.name, vo:b.vo, tx:b.name, many:true})),
    shuffle(items).map(x => ({id:'i_' + x.id, html:x.html, vo:x.vo, tx:x.tx,
                              to:'s_' + x.to})),
    {layout:'basket'});
// Ряд: порожні клітинки по порядку. `seq` подається вже правильно.
const orderTask = (prompt, speak, seq) =>
  dragTask('drag', prompt, speak,
    seq.map((x, i) => ({id:'s_' + i, html:String(i + 1), num:true})),
    shuffle(seq.map((x, i) => Object.assign({}, x, {id:'i_' + i, to:'s_' + i}))),
    {layout:'order'});

// ---------- Показ і перевірка
function showDrag(t, host){
  const lay = t.layout || 'pair';
  const slot = s => `<div class="slot${s.many ? ' many' : ''}${s.num ? ' num' : ''}" `
    + `data-id="${s.id}"><span class="lab">${s.html}</span><span class="drop"></span></div>`;
  const chip = i => `<button class="chip" data-id="${i.id}" data-to="${i.to}">`
    + `${i.html}${i.vo && i.tx && [...String(i.html)].length > 2 ? '<b class="sp">🔊</b>' : ''}</button>`;
  host.innerHTML = `<div class="drag ${lay}">
    <div class="slots">${t.slots.map(slot).join('')}</div>
    <div class="pool">${t.items.map(chip).join('')}</div>
    <p class="tip">Перетягни або торкнись двічі: спершу картки, потім місця.</p></div>`;

  const msg = $('#msg');
  let left = t.items.length, picked = null, tries = {};

  const chips = () => [...host.querySelectorAll('.chip')];
  const slotEl = id => host.querySelector(`.slot[data-id="${CSS.escape(id)}"]`);

  function select(c){
    if (picked === c){ picked.classList.remove('pick'); picked = null; return; }
    if (picked) picked.classList.remove('pick');
    picked = c; c.classList.add('pick');
    const it = t.items.find(x => x.id === c.dataset.id);
    if (it && it.vo) say([[it.vo, it.tx || '']]);
  }

  function drop(c, sEl){
    if (!c || !sEl) return;
    const ok = sEl.dataset.id === c.dataset.to;
    if (ok){
      sEl.querySelector('.drop').appendChild(c);
      c.classList.add('done', 'pick');
      c.classList.remove('pick');
      c.disabled = true;
      picked = null;
      sfxOk();
      if (--left === 0){ guide(CRAB.good, false); pass(host); }
      else { msg.className = 'msg good'; msg.textContent = 'Так!'; }
      return;
    }
    // Помилка — та сама логіка, що у звичайних завданнях: спершу «спробуй
    // ще», і лише з другого разу гра показує, куди саме.
    const k = c.dataset.id;
    tries[k] = (tries[k] || 0) + 1;
    mistakes++;
    sfxNo();
    sEl.classList.remove('no'); void sEl.offsetWidth; sEl.classList.add('no');
    guide(CRAB.oops, false);
    if (tries[k] === 1){
      msg.className = 'msg bad'; msg.textContent = 'Не сюди — спробуй ще';
      say([P.tryagain]);
    } else {
      const right = slotEl(c.dataset.to);
      if (right) right.classList.add('hint');
      msg.className = 'msg bad'; msg.textContent = 'Підказка: потрібне місце обведено';
      say([P.hint]);
      if (right) guide(CRAB.hint, false, right);
    }
  }

  // --- два дотики
  host.querySelectorAll('.chip').forEach(c => {
    c.addEventListener('click', e => {
      if (c.disabled) return;
      if (e.target.closest('.sp')){
        const it = t.items.find(x => x.id === c.dataset.id);
        if (it && it.vo) say([[it.vo, it.tx || '']]);
        return;
      }
      if (!c.dataset.moved) select(c);
      delete c.dataset.moved;
    });
  });
  host.querySelectorAll('.slot').forEach(s => {
    s.addEventListener('click', () => { if (picked) drop(picked, s); });
  });

  // --- тягнення
  let ghost = null, from = null, startX = 0, startY = 0, moved = false;
  host.addEventListener('pointerdown', e => {
    const c = e.target.closest('.chip');
    if (!c || c.disabled || e.target.closest('.sp')) return;
    from = c; moved = false; startX = e.clientX; startY = e.clientY;
    c.setPointerCapture(e.pointerId);
  });
  host.addEventListener('pointermove', e => {
    if (!from) return;
    if (!moved && Math.hypot(e.clientX - startX, e.clientY - startY) < 8) return;
    if (!moved){
      moved = true;
      const r = from.getBoundingClientRect();
      ghost = from.cloneNode(true);
      ghost.className = 'chip ghost';
      ghost.style.width = r.width + 'px';
      ghost.style.height = r.height + 'px';
      document.body.appendChild(ghost);
      from.classList.add('taken');
      if (picked){ picked.classList.remove('pick'); picked = null; }
    }
    // Палець затуляє фішку, тому вона летить вище за точку дотику.
    ghost.style.left = (e.clientX - ghost.offsetWidth / 2) + 'px';
    ghost.style.top = (e.clientY - ghost.offsetHeight / 2 - 28) + 'px';
    const under = document.elementFromPoint(e.clientX, e.clientY - 28);
    host.querySelectorAll('.slot.over').forEach(s => s.classList.remove('over'));
    const s = under && under.closest && under.closest('.slot');
    if (s) s.classList.add('over');
  });
  const end = e => {
    if (!from) return;
    const c = from; from = null;
    if (!moved){ return; }
    c.dataset.moved = '1';
    c.classList.remove('taken');
    const x = e.clientX, y = e.clientY - 28;
    if (ghost){ ghost.remove(); ghost = null; }
    host.querySelectorAll('.slot.over').forEach(s => s.classList.remove('over'));
    const under = document.elementFromPoint(x, y);
    const s = under && under.closest && under.closest('.slot');
    if (s) drop(c, s);
  };
  host.addEventListener('pointerup', end);
  host.addEventListener('pointercancel', e => {
    if (ghost){ ghost.remove(); ghost = null; }
    if (from) from.classList.remove('taken');
    from = null;
  });
}

// ============ ЗАВДАННЯ-ПЕРЕТЯГУВАННЯ ПО ОСТРОВАХ ============
// Кожна функція віддає ОДНЕ завдання. Нижче вони домішуються до наявних
// генераторів, а не замінюють їх: за один захід дитина має побачити і
// звичні питання, і перетягування.

const emo = e => `<span class="big">${e}</span>`;

// — пари: тварина і група
const dAnimals = v => {
  const grp = pick(AGROUP, v === 1 ? 2 : 3);
  const rows = grp.map(([g, vo]) => {
    const pool = ANIM.filter(a => a[1] === g);
    const a = pool[rnd(pool.length)];
    return {key:g, left:g, leftVo:vo, leftTx:g, right:emo(a[0]), rightVo:vo, rightTx:g};
  });
  return pairTask('Постав кожну тварину до своєї групи',
    [['q_agroup', 'До якої групи належить ця тварина?']], rows);
};
// — кошики: дикі й свійські
const dTame = v => basketTask('Розклади тварин: дикі й свійські',
  [['q_tamewild', 'Розклади тварин: дикі й свійські']],
  [{id:'wild', name:'дикі', vo:'a_wild'}, {id:'tame', name:'свійські', vo:'a_tame'}],
  pick(ANIM, v === 1 ? 4 : 6).map((a, i) =>
    ({id:'a' + i, html:emo(a[0]), to:a[2] ? 'tame' : 'wild'})));
// — кошики: жива, нежива, рукотворна
const dAlive = v => {
  const kinds = v === 1 ? ['жива', 'нежива'] : ['жива', 'нежива', 'рукотворна'];
  return basketTask('Розклади по кошиках',
    [P.alive],
    kinds.map(k => ({id:uaId(k), name:k, vo:'nt_' + uaId(k)})),
    pick(NATURE.filter(x => kinds.includes(x[1])), kinds.length * 2)
      .map((x, i) => ({id:'n' + i, html:emo(x[0]), to:uaId(x[1])})));
};
// — кошики: скільки складів у слові
const dSyl = v => {
  const pool = v === 1 ? SYLW.filter(w => w[1] <= 2) : SYLW.filter(w => w[1] <= 3);
  const ns = [...new Set(pool.map(w => w[1]))].sort();
  return basketTask('Розклади слова: скільки в них частин',
    [P.parts],
    ns.map(n2 => ({id:'n' + n2, name:String(n2), vo:'n' + n2, tx:NUM[n2]})),
    pick(pool, Math.min(6, ns.length * 2)).map(([id, k], i) =>
      ({id:'w' + i, html: pic(id, BY_ID[id][1]), vo:id, tx:BY_ID[id][2], to:'n' + k})));
};
// — кошики: з чого зроблено
const dMat = v => {
  const ms = pick(MAT, v === 1 ? 2 : 3);
  return basketTask('Розклади речі за матеріалом', [['q_mat', 'З чого це зроблено?']],
    ms.map(m => ({id:m[0], name:m[1], vo:m[2]})),
    ms.flatMap(m => pick(m[4], 2).map((e, i) =>
      ({id:m[0] + i, html:emo(e), to:m[0]}))));
};
// — пари: професія і справа
const dJobs = v => pairTask('Хто що робить?', [['q_job', 'Хто це робить?']],
  pick(JOBS, v === 1 ? 3 : 4).map(j =>
    ({key:j[0], left:emo(j[3]), leftVo:j[2], leftTx:j[1],
      right:j[4], rightVo:'jd_' + j[0], rightTx:j[4]})));
// — пари: інструмент і що ним роблять
const dTools = v => pairTask('Чим що роблять?', [['q_tool', 'Чим це роблять?']],
  pick(TOOLS, v === 1 ? 3 : 4).map(o =>
    ({key:o[0], left:emo(o[3]), leftVo:o[2], leftTx:o[1],
      right:o[4], rightVo:'tu_' + o[0], rightTx:o[4]})));
// — пари: протилежні слова
const dAnt = v => pairTask('Зʼєднай протилежні слова',
  [['q_ant', 'Яке слово протилежне за значенням?']],
  pick(ANT, v === 1 ? 3 : 4).map(([a, b, va, vb]) =>
    ({key:uaId(a), left:a, leftVo:va, leftTx:a, right:b, rightVo:vb, rightTx:b})));
// — пари: буква й картинка слова
const dLetter = v => {
  const used = new Set(), rows = [];
  for (const w of shuffle(WORDS)){
    if (used.has(w[3])) continue;
    used.add(w[3]);
    rows.push({key:w[3], left:w[3], right: pic(w[0], w[1]), rightVo:w[0], rightTx:w[2]});
    if (rows.length === (v === 1 ? 3 : 4)) break;
  }
  return pairTask('Постав картинку до її букви',
    [['p_letter', 'З якої букви починається слово']], rows);
};
// — ряд: постав числа по порядку
const dNumRow = v => {
  const start = v === 1 ? 1 + rnd(5) : v === 2 ? 8 + rnd(8) : 10 * (1 + rnd(7));
  const step = v === 3 ? 10 : 1;
  const seq = Array.from({length: v === 1 ? 4 : 5}, (_, i) =>
    ({html:String(start + i * step)}));
  return orderTask('Постав числа по порядку, від меншого',
    [['q_row', 'Постав числа по порядку, від меншого до більшого']], seq);
};
// — ряд: кроки справи
const dSteps = v => {
  const [what, steps, id] = PLANS[rnd(PLANS.length)];
  return orderTask(`Що за чим: ${what}`,
    [[id, 'Щоб ' + what], ['q_order', 'Постав по порядку, що за чим робимо']],
    steps.slice(0, v === 1 ? 3 : 4).map(e => ({html:emo(e)})));
};
// — ряд: пори року від осені
const dSeason = () => {
  const S = [['🍂','осінь','a_autumn'],['❄️','зима','a_winter'],
             ['🌷','весна','a_spring'],['☀️','літо','a_summer']];
  return orderTask('Постав пори року по порядку, від осені',
    [['q_seasons', 'Постав пори року по порядку, починай з осені']],
    S.map(([e, n2, vo]) => ({html:emo(e), vo, tx:n2})));
};
// — ряд: букви за алфавітом
const dAbc = v => {
  const k = rnd(ABC.length - 5);
  return orderTask('Постав букви за алфавітом',
    [['q_abcrow', 'Постав букви за абеткою']],
    ABC.slice(k, k + (v === 1 ? 3 : 4)).map(c => ({html:c})));
};
// — кошики: правда чи вигадка
const dTrue = v => basketTask('Розклади: правда і вигадка',
  [['q_true', 'Це правда чи вигадка?']],
  [{id:'yes', name:'правда', vo:'a_pravda'}, {id:'no', name:'вигадка', vo:'a_vyhadka'}],
  pick(FACTS, v === 1 ? 4 : 6).map(([s, ok, fid], i) =>
    ({id:'f' + i, html:s, vo:fid, tx:s, to: ok ? 'yes' : 'no'})));
// — кошики: яке це запитання
const dQw = v => {
  const qs = pick(QW.slice(0, v === 1 ? 2 : 3), v === 1 ? 2 : 3);
  return basketTask('Розклади слова за питанням',
    [['q_qw', 'Яке питання підходить до цього слова?']],
    qs.map(q => ({id:q[0], name:q[1], vo:q[2]})),
    // Озвучку чіпляємо лише до словесних фішок. У «хто?» і «що?» фішка —
    // це емодзі, і uaId() від нього дає порожній хвіст: усі такі фішки
    // дістали б один id `qv_` і читали б одне й те саме.
    qs.flatMap(q => pick(q[3], 2).map((it, i) => {
      const word = /[Ѐ-ӿ]/.test(it);
      return {id:q[0] + i, html: word ? it : emo(it), to:q[0],
              vo: word ? 'qv_' + uaId(it) : undefined, tx: word ? it : undefined};
    })));
};
// — кошики: види інформації
const dInfo = v => {
  const is = pick(INFO, v === 1 ? 2 : 3);
  return basketTask('Чим це сприймають?', [['q_info', 'Яка це інформація?']],
    is.map(i => ({id:i[0], name:i[1], vo:i[2]})),
    is.flatMap(i => i[4].slice(0, 2).map((th, k) =>
      ({id:i[0] + k, html:th, vo:`in_${i[0]}_${k}`, tx:th, to:i[0]}))));
};
// — пари: чуття і річ
const dSense = v => pairTask('Чим ми це відчуваємо?', [['q_sense', 'Чим ми це відчуваємо?']],
  pick(SENSE, v === 1 ? 3 : 4).map(s =>
    ({key:s[0], left:emo(s[3]), leftVo:s[2], leftTx:s[1],
      right:s[4][0], rightVo:`sx_${s[0]}_0`, rightTx:s[4][0]})));
// — пари: фігура й назва
const dFig = v => pairTask('Постав фігуру до її назви', [P.show],
  pick(FIG, v === 1 ? 3 : 4).map(f => {
    const c = FIGCOL[rnd(FIGCOL.length)];
    return {key:f[0], left:f[1], leftVo:f[2], leftTx:f[1],
            right: pic(`f_${f[0]}_${c[0]}`, '🔷')};
  }));
// — пари: лінія й назва
const dLines = v => pairTask('Постав малюнок до його назви', [P.show],
  pick(LINES, v === 1 ? 3 : 4).map(l =>
    ({key:l[0], left:l[1], leftVo:l[2], leftTx:l[1],
      right: svgLine(l[0]), rightVo:l[2], rightTx:l[1]})));
// — кошики: тематичні групи
const dGroup = v => {
  const gs = pick(GROUPS, v === 1 ? 2 : 3);
  return basketTask('Розклади по групах', [['q_gname', 'Як назвати це одним словом?']],
    gs.map(g => ({id:uaId(g[0]), name:g[0], vo:g[1]})),
    gs.flatMap(g => g[2].slice(0, 2).map((e, i) =>
      ({id:uaId(g[0]) + i, html:emo(e), to:uaId(g[0])}))));
};
// — пари: синоніми
const dSyn = v => pairTask('Зʼєднай слова, що означають майже те саме',
  [['q_syn', 'Яке слово означає майже те саме?']],
  pick(SYN, v === 1 ? 3 : 4).map(([a, b, vb]) =>
    ({key:uaId(a), left:a, leftVo:'v_' + uaId(a), leftTx:a,
      right:b, rightVo:vb, rightTx:b})));
// — пари: частина рослини і її назва
const dPlant = v => pairTask('Постав частину рослини до її назви', [P.show],
  pick(PLANT, v === 1 ? 3 : 4).map(p =>
    ({key:p[0], left:p[1], leftVo:p[2], leftTx:p[1], right:emo(p[3])})));
// — кошики: у який контейнер
const dBin = () => basketTask('Розклади сміття по контейнерах',
  [['q_bin', 'У який контейнер це викинути?']],
  BIN.map(([e, name]) => ({id:uaId(name), name, vo:'bn_' + uaId(name)})),
  BIN.map(([e, name], i) => ({id:'b' + i, html:emo(e), to:uaId(name)})));
// — пари: велика й мала буква.
// Ключ — НОМЕР букви в абетці, не транслітерація: uaId() дає і для «І»,
// і для «Ї» однакове «i», і дві картки злилися б в одну.
const dCase = v => pairTask('Постав малу букву до великої',
  [['q_case', 'Постав малу букву до великої']],
  pick(ABC.filter(c => c !== 'Ь'), v === 1 ? 3 : 4).map(c =>
    ({key:'c' + ABC.indexOf(c), left:c, right:c.toLowerCase()})));
// — пари: десяток і одиниці дають число
const dTens = v => pairTask('Склади число з десятків і одиниць',
  [['q_tens2', 'Яке число виходить із десятків і одиниць?']],
  pick([11,12,13,14,15,16,17,18,19], v === 1 ? 3 : 4).map(N =>
    ({key:'n' + N, left:'10 + ' + (N % 10), right:String(N)})));
// — пари: погода й одяг до неї. Саме пари, а не кошики: у WEA на кожну
// погоду припадає рівно одна річ, і кошики з однією фішкою — не завдання.
const dWear = v => pairTask('Що вдягнути в таку погоду?',
  [['q_wear2', 'Постав одяг до погоди']],
  pick(WEA, v === 1 ? 3 : 4).map(w =>
    ({key:w[1], left: pic(w[0], w[4]), leftVo:w[3], leftTx:w[2],
      right: pic(w[5], w[6])})));
// — кошики: фігури за формою
const dFigBasket = v => {
  const fs = pick(FIG, v === 1 ? 2 : 3);
  return basketTask('Розклади фігури за формою', [P.show],
    fs.map(f => ({id:f[0], name:f[1], vo:f[2]})),
    fs.flatMap(f => pick(FIGCOL, 2).map((c, i) =>
      ({id:f[0] + i, html: pic(`f_${f[0]}_${c[0]}`, '🔷'), to:f[0]}))));
};
// — пари: предмет і назва його групи
const dGroupPair = v => pairTask('Постав предмет до його групи',
  [['q_gname', 'Як назвати це одним словом?']],
  pick(GROUPS, v === 1 ? 3 : 4).map(g =>
    ({key:uaId(g[0]), left:g[0], leftVo:g[1], leftTx:g[0], right:emo(g[2][0])})));
// — ряд: склади в слові
const dWordRow = v => {
  const [w, split] = WORDS_READ[rnd(WORDS_READ.length)];
  return orderTask(`Склади слово «${w}»`,
    [['p_word', 'Яке слово ти чуєш?'], [wdId(w), w]],
    split.split('·').map(s => ({html:s})));
};

// ============ ДОМІШУВАННЯ ДО ОСТРОВІВ ============
// Не замінюємо генератори, а підмішуємо: одне-два з пʼяти завдань стають
// перетягуванням. Так кожен захід на острів інший, і жоден із наявних
// генераторів не довелося переписувати.
function mixDrag(base, makers, howMany){
  return function (v){
    const t = base(v);
    const k = Math.min(howMany, t.length - 1);
    // Якщо різних розкладів менше, ніж треба завдань, той самий беремо
    // двічі: вміст він щоразу набирає інший, а от форма повториться —
    // тому вище в таблиці майже всюди дано ДВА різні розклади.
    const use = [];
    while (use.length < k) use.push(...pick(makers, Math.min(k - use.length, makers.length)));
    for (let i = 0; i < k; i++){
      try { t[i] = use[i](v); } catch (e) { /* лишаємо звичайне завдання */ }
    }
    return shuffle(t);
  };
}
// Для кожного острова — два РІЗНІ розклади, щоб два перетягування за
// захід не виявилися однаковими на вигляд.
const DRAG_BY_ISLAND = {
  animals: [dAnimals, dTame],
  alive:   [dAlive, dPlant],
  sound:   [dSyl, dWordRow],
  stuff:   [dMat, dBin],
  jobs:    [dJobs, dTools],
  card:    [dTools, dSteps],
  mean:    [dAnt, dSyn],
  read:    [dLetter, dCase],
  num20:   [dNumRow, dTens],
  num100:  [dNumRow, dTens],
  order:   [dSteps, dSeason],
  plan:    [dSteps, dSeason],
  weather: [dSeason, dWear],
  abc:     [dAbc, dCase],
  true:    [dTrue, dInfo],
  quest:   [dQw, dGroupPair],
  info:    [dInfo, dSense],
  body:    [dSense, dInfo],
  fig:     [dFig, dFigBasket],
  lines:   [dLines, dFig],
  group:   [dGroup, dGroupPair],
  syll:    [dWordRow, dSyl],
};
for (const l of LESSONS){
  const mk = DRAG_BY_ISLAND[l.id];
  if (mk) l.gen = mixDrag(l.gen, mk, 2);
}
