// ===== ЗБЕРИ, А НЕ ВИБЕРИ =====
//
// Чим це відрізняється від «постав у ряд» (`order`). Там усі картки
// потрібні, і дитина лише впорядковує. Тут у наборі є ЗАЙВІ частини:
// щоб скласти «МА-МА», треба і відкинути «ЛО» з «СУ», і поставити свої
// дві в правильному місці. Тобто вибір і порядок разом.
//
// Чому це важливо для першого класу: вибрати слово з трьох готових
// можна навмання, а скласти його зі складів — ні. Те саме з числом:
// «сорок сім» перестає бути картинкою й стає сорока й сімкою.
//
// Нагорода наприкінці — зібране читається вголос і показується цілим.
// Заради цього дитина й збирала.

// ---------- Загальна побудова
// parts — що має вийти, по порядку. extra — скільки зайвих підкинути.
function buildTask(prompt, speak, parts, pool, done){
  // У наборі мусить бути стільки «МА», скільки їх у слові, інакше друге
  // місце нічим заповнити.
  const tiles = parts.map((p, i) => ({id:'p' + i, html:p, need:i}))
    .concat(pool.map((p, i) => ({id:'x' + i, html:p, need:-1})));
  return {kind:'build', prompt, speak, parts, done,
    tiles: shuffle(tiles),
    options: []};
}
function showBuild(t, host){
  const n = t.parts.length;
  host.innerHTML = `<div class="build">
    <div class="strip">${t.parts.map((_, i) =>
      `<span class="cell" data-i="${i}"></span>`).join('')}</div>
    <div class="pool">${t.tiles.map(x =>
      `<button class="tile" data-id="${x.id}" data-need="${x.need}">${x.html}</button>`).join('')}</div>
    <p class="tip">Натискай частини по порядку. Зайві тут теж є.</p></div>`;
  const msg = $('#msg');
  let at = 0, tries = 0;
  host.querySelectorAll('.tile').forEach(b => b.onclick = () => {
    if (b.disabled) return;
    if (+b.dataset.need === at){
      // Частина стає на місце й більше не повертається: виправляти
      // зібране першокласнику важче, ніж не помилитися.
      const cell = host.querySelector(`.cell[data-i="${at}"]`);
      cell.textContent = b.textContent;
      cell.classList.add('fill');
      b.disabled = true; b.classList.add('used');
      at++; sfxTap();
      if (at === n){
        msg.className = 'msg good';
        msg.innerHTML = 'Вийшло: <b>' + t.done + '</b>';
        sfxOk(); guide(CRAB.good, false);
        if (t.vo) say([[t.vo, t.done]]);
        pass(host, false);
      }
    } else {
      tries++; mistakes++; sfxNo(); guide(CRAB.oops, false);
      b.classList.remove('no'); void b.offsetWidth; b.classList.add('no');
      msg.className = 'msg bad';
      if (tries === 1){ msg.textContent = 'Не ця частина — спробуй іншу'; say([P.tryagain]); }
      else {
        const right = host.querySelector(`.tile[data-need="${at}"]:not(.used)`);
        if (right) right.classList.add('hint');
        msg.textContent = 'Підказка: потрібна частина блимає'; say([P.hint]);
        if (right) guide(CRAB.hint, false, right);
      }
    }
  });
}

// ---------- 1. Слово зі складів
function bWord(v){
  const pool = v === 1 ? WORDS_READ.filter(w => w[1].split('·').length === 2)
                       : WORDS_READ;
  const [w, split] = pool[rnd(pool.length)];
  const parts = split.split('·');
  // Зайві склади беремо з тих, яких у цьому слові немає.
  const extra = pick(SYLL.map(s => s.toUpperCase()).filter(s => !parts.includes(s)),
                     v === 1 ? 2 : 3);
  const t = buildTask(`Збери слово «${w}» зі складів`,
    [['q_build_w', 'Збери слово зі складів'], [wdId(w), w]],
    parts, extra, w);
  t.vo = wdId(w);
  return t;
}

// ---------- 2. Число з десятків і одиниць
function bNum(v){
  const N = v === 1 ? 11 + rnd(9) : v === 2 ? 21 + rnd(29) : 21 + rnd(79);
  const tens = Math.floor(N / 10) * 10, ones = N % 10;
  const parts = ones ? [String(tens), String(ones)] : [String(tens)];
  const extra = [];
  while (extra.length < (v === 1 ? 2 : 3)){
    const e = rnd(2) ? String(10 * (1 + rnd(9))) : String(1 + rnd(9));
    if (!parts.includes(e) && !extra.includes(e)) extra.push(e);
  }
  return buildTask(`Збери число ${N} з десятків і одиниць`,
    [['q_build_n', 'Збери число з десятків і одиниць']],
    parts, extra, String(N));
}

// ---------- 3. Речення зі слів
function bSent(v){
  const [s, k, mark, id] = SENTS[rnd(SENTS.length)];
  const words = s.slice(0, -1).split(' ');
  const parts = words.concat([mark]);
  // Зайве — слово з іншого речення і чужий розділовий знак.
  const other = SENTS.filter(x => x[0] !== s)[rnd(SENTS.length - 1)];
  const extra = [other[0].slice(0, -1).split(' ')[0].toLowerCase()]
    .concat(['.', '?', '!'].filter(x => x !== mark).slice(0, v === 1 ? 1 : 2));
  const t = buildTask('Збери речення зі слів і постав знак у кінці',
    [['q_build_s', 'Збери речення зі слів і постав знак у кінці'], [id, s]],
    parts, extra, s);
  t.vo = id;
  return t;
}

// ---------- Куди поставити
const BUILD_BY_ISLAND = {
  syll: [bWord], read: [bWord], sound: [bWord],
  num20: [bNum], num100: [bNum], math: [bNum],
  sent: [bSent], text: [bSent], quest: [bSent],
};
for (const l of LESSONS){
  const mk = BUILD_BY_ISLAND[l.id];
  if (!mk) continue;
  const base = l.gen;
  l.gen = function (v){
    const t = base(v);
    try { t[t.length - 1] = mk[rnd(mk.length)](v); } catch (e) {}
    return shuffle(t);
  };
}
