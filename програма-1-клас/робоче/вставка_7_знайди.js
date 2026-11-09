// ===== ЗНАЙДИ НА КАРТИНІ: одна сцена, багато натискань =====
//
// Навіщо. В усіх інших завданнях дитина вибирає ОДНУ відповідь і йде
// далі. Тут вона переглядає сцену й знаходить УСЕ, що підходить: усе
// кругле, усе живе, усе на «м». Жест ніби той самий — натиснути, — але
// робота інша: не впізнати один предмет, а обвести очима ціле поле й
// нічого не проґавити. Це «знайди на картині» з `РІЗНОМАНІТТЯ.md`.
//
// Чому це вигідно: одна сцена дає десятки різних завдань, бо умова
// щоразу інша. Малюнок живе довго.
//
// Про картинку сцени. Поки її немає, тло малюється кольором (CSS), а
// предмети лежать поверх. Коли ComfyUI намалює `sc_*`, вона стане на
// місце сама — як і всюди в грі, через онопомилку в <img>.

// Сітка з тремтінням. Рівний ряд предметів перетворив би пошук на
// читання по порядку, а купа без сітки дає накладання, і дитина не може
// влучити пальцем. Тому сітка є, але кожен предмет зсунуто випадково.
function scatter(n){
  const cols = n <= 6 ? 3 : n <= 9 ? 3 : 4;
  const rows = Math.ceil(n / cols);
  const out = [];
  for (let i = 0; i < n; i++){
    const c = i % cols, r = Math.floor(i / cols);
    out.push({
      x: Math.round((c + 0.5) / cols * 100 + (rnd(17) - 8)),
      y: Math.round((r + 0.5) / rows * 100 + (rnd(15) - 7)),
    });
  }
  return shuffle(out);
}

// Завдання: items — усе, що на сцені; ті, у кого hit, треба знайти.
function findTask(prompt, speak, scene, items){
  const pos = scatter(items.length);
  return {kind:'find', prompt, speak, scn:scene,
    items: items.map((it, i) => Object.assign({}, it, pos[i])),
    // options — щоб кнопка 🔊 вгорі прочитала умову й підписи
    options: items.filter(x => x.vo && x.tx)};
}

function showFind(t, host){
  const need = t.items.filter(x => x.hit).length;
  // Малюнок сцени кладемо окремим <img> під предметами, а не фоном у CSS:
  // так він може не завантажитись і тихо зникнути, лишивши колір. Фон у
  // CSS такого запасу не має — була б порожня пляма.
  host.innerHTML = `<div class="find scn-${t.scn}">
    <div class="field"><img class="bg" src="${asset('img/sc_' + t.scn + '.png')}" alt=""
        onerror="this.remove()">${t.items.map((it, i) =>
      `<button class="obj" data-i="${i}" data-hit="${it.hit ? 1 : 0}"
        style="left:${it.x}%;top:${it.y}%">${it.html}</button>`).join('')}</div>
    <p class="count"><b id="cnt">0</b> з ${need}</p></div>`;
  const msg = $('#msg');
  let got = 0, miss = 0;
  host.querySelectorAll('.obj').forEach(b => b.onclick = () => {
    if (b.classList.contains('got') || b.disabled) return;
    if (b.dataset.hit === '1'){
      b.classList.add('got'); got++;
      $('#cnt').textContent = got;
      sfxOk();
      const it = t.items[+b.dataset.i];
      if (it.vo) say([[it.vo, it.tx || '']]);
      if (got === need){ guide(CRAB.good, false); pass(host); }
      else { msg.className = 'msg good'; msg.textContent = 'Є!'; }
    } else {
      // Зайвий предмет не ховаємо: дитина має бачити, що він лишився на
      // місці, інакше сцена порожніє й шукати стає нічого.
      miss++; mistakes++;
      b.classList.remove('no'); void b.offsetWidth; b.classList.add('no');
      sfxNo(); guide(CRAB.oops, false);
      msg.className = 'msg bad';
      if (miss === 1){ msg.textContent = 'Це не підходить — шукай далі'; say([P.tryagain]); }
      else {
        const left = [...host.querySelectorAll('.obj[data-hit="1"]:not(.got)')];
        if (left.length) left[0].classList.add('hint');
        msg.textContent = 'Підказка: один із потрібних блимає';
        say([P.hint]);
        if (left.length) guide(CRAB.hint, false, left[0]);
      }
    }
  });
}

// ---------- Умови пошуку. Усі зібрані з таблиць, які вже є в грі.
const bigE = e => `<span class="big">${e}</span>`;
// Скільки предметів на сцені й скільки з них потрібні
const findSize = v => v === 1 ? [6, 3] : v === 2 ? [9, 4] : [12, 5];

// — усе живе
const fAlive = v => {
  const [n, k] = findSize(v);
  const yes = pick(NATURE.filter(x => x[1] === 'жива'), k);
  const no = pick(NATURE.filter(x => x[1] !== 'жива'), n - k);
  return findTask('Знайди все живе',
    [['f_alive', 'Знайди на картині все живе']], 'forest',
    shuffle(yes.map(x => ({html:bigE(x[0]), hit:true}))
      .concat(no.map(x => ({html:bigE(x[0]), hit:false})))));
};
// — усе, що починається на певну букву
const fLetter = v => {
  const [n, k] = findSize(v);
  const byL = {};
  for (const w of WORDS) (byL[w[3]] = byL[w[3]] || []).push(w);
  const good = Object.keys(byL).filter(L2 => byL[L2].length >= k);
  const L2 = good[rnd(good.length)];
  const yes = pick(byL[L2], k);
  const no = pick(WORDS.filter(w => w[3] !== L2), n - k);
  return findTask(`Знайди все, що починається на «${L2}»`,
    [['f_letter', 'Знайди на картині все, що починається на букву'], ['let_' + LET_ID[L2.toLowerCase()], LET_NAME[L2.toLowerCase()]]],
    'room',
    shuffle(yes.map(w => ({html: pic(w[0], w[1]), hit:true, vo:w[0], tx:w[2]}))
      .concat(no.map(w => ({html: pic(w[0], w[1]), hit:false, vo:w[0], tx:w[2]})))));
};
// — тварини однієї групи
const fAnimals = v => {
  const [n, k] = findSize(v);
  const g = AGROUP[rnd(AGROUP.length)];
  const pool = ANIM.filter(a => a[1] === g[0]);
  if (pool.length < 3) return fAlive(v);
  const yes = pick(pool, Math.min(k, pool.length));
  const no = pick(ANIM.filter(a => a[1] !== g[0]), n - yes.length);
  return findTask(`Знайди всіх, хто це: ${g[0]}`,
    [['f_group', 'Знайди на картині всіх, хто належить до групи'], [g[1], g[0]]],
    'forest',
    shuffle(yes.map(a => ({html:bigE(a[0]), hit:true}))
      .concat(no.map(a => ({html:bigE(a[0]), hit:false})))));
};
// — усе небезпечне
const fDanger = v => {
  const [n, k] = findSize(v);
  const yes = pick(DANGER.filter(d => d[2]), Math.min(k, 5));
  const no = pick(DANGER.filter(d => !d[2]), n - yes.length);
  return findTask('Знайди все небезпечне',
    [['f_danger', 'Знайди на картині все, що небезпечне']], 'room',
    shuffle(yes.map(d => ({html:bigE(d[0]), hit:true}))
      .concat(no.map(d => ({html:bigE(d[0]), hit:false})))));
};
// — усе з одного матеріалу
const fMat = v => {
  const [n, k] = findSize(v);
  const m = MAT[rnd(MAT.length)];
  const yes = m[4].map(e => ({html:bigE(e), hit:true}));
  const rest = MAT.filter(x => x[0] !== m[0]).flatMap(x => x[4]);
  const no = pick(rest, Math.max(2, n - yes.length)).map(e => ({html:bigE(e), hit:false}));
  return findTask(`Знайди все, що з такого матеріалу: ${m[1]}`,
    [['f_mat', 'Знайди на картині все, що зроблено з цього матеріалу'], [m[2], m[1]]],
    'room', shuffle(yes.concat(no)));
};
// — фігури однієї форми
const fFig = v => {
  const [n, k] = findSize(v);
  const f = FIG[rnd(FIG.length)];
  const yes = pick(FIGCOL, Math.min(k, FIGCOL.length))
    .map(c => ({html: pic(`f_${f[0]}_${c[0]}`, '🔷'), hit:true}));
  const others = FIG.filter(x => x[0] !== f[0]);
  const no = [];
  while (no.length < n - yes.length){
    const f2 = others[rnd(others.length)], c = FIGCOL[rnd(FIGCOL.length)];
    no.push({html: pic(`f_${f2[0]}_${c[0]}`, '🔶'), hit:false});
  }
  return findTask(`Знайди всі фігури: ${f[1]}`,
    [['f_fig', 'Знайди на картині всі такі фігури'], [f[2], f[1]]],
    'sea', shuffle(yes.concat(no)));
};
// — числа, більші за задане
const fNum = v => {
  const [n, k] = findSize(v);
  const hi = v === 1 ? 10 : v === 2 ? 20 : 100;
  const edge = v === 1 ? 3 + rnd(4) : v === 2 ? 8 + rnd(8) : 20 + rnd(50);
  const yes = [], no = [];
  while (yes.length < k) yes.push(edge + 1 + rnd(Math.max(1, hi - edge - 1)));
  while (no.length < n - k) no.push(1 + rnd(edge));
  return findTask(`Знайди всі числа, більші за ${edge}`,
    [['f_num', 'Знайди на картині всі числа, більші за це']], 'sea',
    shuffle(yes.map(x => ({html:`<span class="big">${x}</span>`, hit:true}))
      .concat(no.map(x => ({html:`<span class="big">${x}</span>`, hit:false})))));
};
// — слова з певною кількістю складів
const fSyl = v => {
  const [n, k] = findSize(v);
  const want = v === 1 ? 2 : 1 + rnd(3);
  const pool = SYLW.filter(w => w[1] === want);
  if (pool.length < 3) return fLetter(v);
  const yes = pick(pool, Math.min(k, pool.length));
  const no = pick(SYLW.filter(w => w[1] !== want), n - yes.length);
  const card = ([id]) => ({html: pic(id, BY_ID[id][1]), vo:id, tx:BY_ID[id][2]});
  return findTask(`Знайди слова, у яких ${want} частини`,
    [['f_syl', 'Знайди на картині слова, у яких стільки частин'], n(want)], 'room',
    shuffle(yes.map(w => Object.assign(card(w), {hit:true}))
      .concat(no.map(w => Object.assign(card(w), {hit:false})))));
};
// — усе з однієї тематичної групи
const fGroup = v => {
  const [n] = findSize(v);
  const g = GROUPS[rnd(GROUPS.length)];
  const yes = g[2].map(e => ({html:bigE(e), hit:true}));
  const rest = GROUPS.filter(x => x[0] !== g[0]).flatMap(x => x[2]);
  const no = pick(rest, Math.max(3, n - yes.length)).map(e => ({html:bigE(e), hit:false}));
  return findTask(`Знайди все, що це: ${g[0]}`,
    [['f_grp', 'Знайди на картині все, що належить до групи'], [g[1], g[0]]],
    'room', shuffle(yes.concat(no)));
};

// ---------- Куди це поставити.
// Домішуємо так само, як перетягування: по одному завданню з пʼяти, щоб
// у заході було три види роботи — вибір, перетягування і пошук.
const FIND_BY_ISLAND = {
  read:    [fLetter],
  sound:   [fSyl],
  alive:   [fAlive],
  animals: [fAnimals],
  safe:    [fDanger],
  stuff:   [fMat],
  fig:     [fFig],
  group:   [fGroup],
  math:    [fNum],
  num20:   [fNum],
  num100:  [fNum],
  compare: [fNum],
  world:   [fAlive],
  signs:   [fDanger],
};
function mixFind(base, makers){
  return function (v){
    const t = base(v);
    try { t[t.length - 1] = makers[rnd(makers.length)](v); } catch (e) {}
    return shuffle(t);
  };
}
for (const l of LESSONS){
  const mk = FIND_BY_ISLAND[l.id];
  if (mk) l.gen = mixFind(l.gen, mk);
}
