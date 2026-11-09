// ===== ЗАГЛИБЛЕННЯ: нитка на кілька днів крізь кілька островів =====
//
// Навіщо. Острів дає пʼять не повʼязаних між собою завдань і зірку.
// Заглиблення дає ПРИЧИНУ їх робити: дитина не «проходить Острів Тварин»,
// а розгадує, хто ходив по снігу. На цьому збігаються всі шість систем,
// які ми дивилися (`РІЗНОМАНІТТЯ.md`): вальдорфська «епоха», тематичні
// блоки «Освіти. Діти. Майбутнє», домени Core Knowledge.
//
// Три речі, які тут зроблено свідомо:
//
// 1. **Крок починається з учорашнього.** Перші одне-два завдання кроку
//    беруться з островів ПОПЕРЕДНЬОГО кроку. Це вальдорфська пауза через
//    ніч: «узагальнення матеріалу та якісний крок у вивченні теми
//    відбувається наступного дня». Без цього заглиблення було б просто
//    списком уроків.
// 2. **Один крок на день.** Гра не дає пройти наступний крок того самого
//    дня — інакше нитка на тиждень збігає за двадцять хвилин і сенс
//    паузи зникає. Учитель може зняти обмеження в налаштуваннях профілю.
// 3. **Блок-карта наприкінці.** Назва з програми «Світ чекає крилатих»:
//    «путівник учня за вивченою темою». Кожен крок дає одну картку, і
//    наприкінці дитина має зібраний путівник, який можна показати.
//
// Нових островів НЕ додається: заглиблення бере завдання з наявних.

const DEEP = [
 {id:'school', per:1, ico:'🎒', img:'d_school', vo:'dn_school',
  name:'Я йду до школи', about:'Перші дні: дорога, клас, я сам',
  story:['dst_school', 'Перший тиждень на острові. Краб Клац покаже дорогу до школи й те, що треба знати дорогою.'],
  steps:[
   {ico:'🚦', name:'Дорога до школи', from:['safe', 'place', 'signs'], n:4},
   {ico:'🎒', name:'Що в моїй сумці',  from:['read', 'math', 'write'],  n:4},
   {ico:'👁️', name:'Чим я пізнаю світ', from:['body', 'info', 'sound'], n:4},
   {ico:'🧍', name:'Моє тіло',          from:['body', 'alive', 'memo'], n:4},
   {ico:'⛔', name:'Небезпечно — не чіпай', from:['signs', 'safe', 'true'], n:4},
  ]},
 {id:'autumn', per:1, ico:'🍂', img:'d_autumn', vo:'dn_autumn',
  name:'Осінь на острові', about:'Що змінилося навколо',
  story:['dst_autumn', 'Листя пожовкло, птахи збираються в дорогу. Подивимось, що осінь зробила з островом.'],
  steps:[
   {ico:'🌦️', name:'Яка нині погода', from:['weather', 'place', 'logic'], n:4},
   {ico:'🍁', name:'Листя і дерева',   from:['alive', 'logic', 'fig'],   n:4},
   {ico:'🐦', name:'Хто відлітає',     from:['animals', 'sound', 'shadow'], n:4},
   {ico:'🍎', name:'Урожай: порахуй',  from:['math', 'compare', 'num'],  n:4},
   {ico:'🎨', name:'Кольори осені',    from:['fig', 'ornament', 'logic'],  n:4},
  ]},
 {id:'home', per:2, ico:'🏡', img:'d_home', vo:'dn_home',
  name:'Дім і сімʼя', about:'Хто поруч і хто що робить',
  story:['dst_home', 'У кожного на острові є дім. Поглянемо, хто в ньому живе і хто яку справу робить.'],
  steps:[
   {ico:'👨‍👩‍👧', name:'Моя сімʼя',     from:['sent', 'quest', 'mean'],  n:4},
   {ico:'👷', name:'Хто що робить',    from:['jobs', 'card', 'group'],   n:4},
   {ico:'🪑', name:'Що є в домі',      from:['group', 'stuff', 'memo'], n:4},
   {ico:'🔢', name:'Полічимо все вдома', from:['num', 'num20', 'compare'], n:4},
   {ico:'🪙', name:'Ідемо по покупки', from:['money', 'task', 'data'],  n:4},
  ]},
 {id:'winter', per:2, ico:'❄️', img:'d_winter', vo:'dn_winter',
  name:'Зима і сліди', about:'Хто ходив по снігу',
  story:['dst_winter', 'На снігу хтось лишив сліди. Підемо по них і дізнаємось, хто тут був.'],
  steps:[
   {ico:'🐾', name:'Чиї це сліди',     from:['animals', 'shadow', 'world'], n:4},
   {ico:'🏠', name:'Хто де зимує',     from:['animals', 'alive', 'place'],  n:4},
   {ico:'❄️', name:'Зимова погода',    from:['weather', 'true', 'info'],   n:4},
   {ico:'🔤', name:'Сніг, лід, слід',  from:['syll', 'read', 'write'],      n:4},
   {ico:'🪘', name:'Як стукає дятел',  from:['rhythm', 'tempo', 'instr'],   n:4},
  ]},
 {id:'country', per:3, ico:'🇺🇦', img:'d_country', vo:'dn_country',
  name:'Моя країна', about:'Київ, símволи, рідний край',
  story:['dst_country', 'Острів — частина великої країни. Дізнаємось, як вона зветься і що її впізнає.'],
  steps:[
   {ico:'🏛️', name:'Київ і прапор',   from:['country', 'true', 'text'],   n:4},
   {ico:'🌻', name:'Що росте в нас',  from:['alive', 'group', 'world'],    n:4},
   {ico:'🪆', name:'Народні візерунки', from:['ornament', 'fig', 'lines'], n:4},
   {ico:'🔡', name:'Абетка рідної мови', from:['abc', 'write', 'read'],   n:4},
   {ico:'📖', name:'Казка мого краю', from:['text', 'mean', 'quest'],      n:4},
  ]},
 {id:'water', per:3, ico:'💧', img:'d_water', vo:'dn_water',
  name:'Жива вода', about:'Звідки вона і кому потрібна',
  story:['dst_water', 'Довкола острова — вода. Без неї тут не росло б нічого. Подивимось, чому.'],
  steps:[
   {ico:'💧', name:'Яка буває вода',  from:['alive', 'stuff', 'info'],    n:4},
   {ico:'🌱', name:'Рослина пʼє воду', from:['alive', 'plan', 'order'],    n:4},
   {ico:'🐟', name:'Хто живе у воді', from:['animals', 'world', 'shadow'],  n:4},
   {ico:'📏', name:'Скільки води',    from:['measure', 'data', 'num100'],   n:4},
   {ico:'📐', name:'Хвилі і лінії',   from:['lines', 'logic', 'fig'],    n:4},
  ]},
 {id:'workshop', per:4, ico:'🔨', img:'d_workshop', vo:'dn_workshop',
  name:'Майстерня винаходів', about:'З чого зроблено і хто придумав',
  story:['dst_workshop', 'У майстерні краба повно речей. Кожну хтось колись вигадав. Розберемось, із чого вони.'],
  steps:[
   {ico:'🪵', name:'З чого це зроблено', from:['stuff', 'group', 'card'],   n:4},
   {ico:'🛞', name:'Хто це вигадав',     from:['invent', 'true', 'ask'],   n:4},
   {ico:'🗂️', name:'Читаю інструкцію',  from:['card', 'plan', 'order'],     n:4},
   {ico:'💡', name:'Задачі майстра',     from:['task', 'add100', 'data'],   n:4},
   {ico:'♻️', name:'Друге життя речей',  from:['stuff', 'quest', 'code'],   n:4},
  ]},
 {id:'world', per:4, ico:'🌍', img:'d_world', vo:'dn_world',
  name:'Великий світ', about:'За островом є ще багато',
  story:['dst_world', 'Острів не один. За морем є інші землі, інші тварини й дуже великі числа.'],
  steps:[
   {ico:'🗺️', name:'Інші країни',     from:['country', 'en', 'ask'],      n:4},
   {ico:'🦋', name:'Тварини світу',   from:['animals', 'alive', 'group'],   n:4},
   {ico:'💯', name:'Великі числа',    from:['num100', 'add100', 'num20'],   n:4},
   {ico:'📊', name:'Що кажуть таблиці', from:['data', 'measure', 'task'],  n:4},
   {ico:'⚖️', name:'Правда чи вигадка', from:['true', 'ask', 'code'],      n:4},
  ]},
];
const BY_DEEP = Object.fromEntries(DEEP.map(d => [d.id, d]));

// ---------- Поступ дитини. Живе в тому самому профілі, що й зірки.
function deepState(did){
  const k = kid(); if (!k) return {step:0, cards:[], day:''};
  k.deep = k.deep || {};
  return (k.deep[did] = k.deep[did] || {step:0, cards:[], day:''});
}
// Чи можна починати наступний крок. Обмеження «один крок на день» — не
// каприз: без нього нитка на тиждень збігає за двадцять хвилин, і пауза,
// заради якої все й робилося, зникає.
function deepReady(did){
  const k = kid(), st = deepState(did);
  if (k && k.noWait) return true;                 // вчитель зняв обмеження
  return st.day !== today();
}
const deepDone = did => deepState(did).step >= BY_DEEP[did].steps.length;

// ---------- Запуск кроку
let DEEPID = null;
function startDeep(did){
  const d = BY_DEEP[did], st = deepState(did);
  const i = Math.min(st.step, d.steps.length - 1);
  const s = d.steps[i];
  DEEPID = did; DAILY = false;
  L = {id:'deep_' + did, name:d.name, vo:d.vo};
  lvl = 0; idx = 0; mistakes = 0; tasks = [];

  // Складність росте разом із кроком: перші кроки — легкий рівень.
  const v = i < 2 ? 1 : i < 4 ? 2 : 3;
  // Острови в кроці перемішуємо, інакше завдання йдуть парами з одного
  // острова підряд («чия це тінь» двічі), і крок виглядає як два уроки,
  // склеєні докупи. Однакові питання відсіюємо.
  const seen = new Set();
  const take = (ids, howMany) => {
    const pool = [];
    while (pool.length < howMany) pool.push(...shuffle(ids));
    for (let n = 0; n < howMany; n++){
      const l = BY_LES[pool[n]];
      if (!l) continue;
      try {
        const got = shuffle(l.gen(v));
        const t = got.find(x => !seen.has(String(x.prompt))) || got[0];
        seen.add(String(t.prompt));
        tasks.push(t);
      } catch (e) { /* острів не дав завдання — пропускаємо */ }
    }
  };
  // Спершу — одне-два завдання з учорашнього кроку.
  if (i > 0) take(d.steps[i - 1].from, 2);
  take(s.from, s.n);
  playTune(did in BY_DEEP ? (s.from[0] || 'theme') : 'theme');
  guide(['dst_' + did, d.story[1], 'swim'], true, null, 'swim');
  show();
}

// ---------- Кінець кроку: картка в путівник і наступний крок
function deepFinish(){
  const d = BY_DEEP[DEEPID], st = deepState(DEEPID), k = kid();
  const i = Math.min(st.step, d.steps.length - 1);
  const s = d.steps[i];
  if (!st.cards.includes(i)) st.cards.push(i);
  st.step = Math.min(i + 1, d.steps.length);
  st.day = today();
  save();
  return {step:s, i, last: st.step >= d.steps.length};
}

// ---------- Екран заглиблення: шлях із кроків і зібраний путівник
function deepScreen(did){
  const d = BY_DEEP[did], st = deepState(did);
  scene('map'); playTune('theme');
  const ready = deepReady(did), done = deepDone(did);
  $('#app').innerHTML = `<section class="lesson deep">
    <div class="bar"><button class="back" id="back">← Карта</button></div>
    <h3>${d.ico} ${d.name}</h3>
    <p class="lead">${d.about}</p>
    <div class="path">${d.steps.map((s, i) => {
      const got = st.cards.includes(i);
      const now = i === st.step;
      return `<div class="st${got ? ' got' : ''}${now ? ' now' : ''}">
        <span class="ico">${got ? s.ico : now ? s.ico : '🔒'}</span>
        <b>${i + 1}. ${s.name}</b></div>`;
    }).join('')}</div>
    ${done
      ? `<p class="lead big-ok">Путівник зібрано! ${d.steps.map(s => s.ico).join(' ')}</p>`
      : ready
        ? `<button class="next" id="go">Крок ${st.step + 1}: ${d.steps[st.step].name}</button>`
        : `<p class="lead wait">Цей крок уже пройдено сьогодні.<br>
             Наступний буде завтра — так краще запамʼятовується.</p>`}
    </section>`;
  $('#back').onclick = home;
  const go = $('#go'); if (go) go.onclick = () => startDeep(did);
}

// ---------- Блок карти: нитки поточної чверті
function deepCard(d){
  const st = deepState(d.id);
  const n = d.steps.length;
  return `<button class="island deep" data-deep="${d.id}">
    <span class="ico">${pic(d.img, d.ico)}</span>
    <h2>${d.name}</h2><p>${d.about}</p>
    <span class="got">${'●'.repeat(st.cards.length)}<i>${'●'.repeat(n - st.cards.length)}</i></span>
  </button>`;
}
function deepBlock(){
  const list = DEEP.filter(d => term() === 0 || d.per <= term());
  if (!list.length) return '';
  return `<div class="seahead"><span class="ico">🧭</span>Заглиблення
      <b>${list.filter(d => deepDone(d.id)).length} / ${list.length} ✓</b></div>
    <div class="map">${list.map(deepCard).join('')}</div>`;
}
