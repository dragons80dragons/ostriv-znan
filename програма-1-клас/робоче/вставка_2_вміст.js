// ===== РОЗШИРЕННЯ ДО ПОВНОГО 1 КЛАСУ: слова, склади, нові острови =====
// Усе нижче тримається тих самих правил, що й демоверсія:
//   • картинки беруться з assets/img/<id>.png, а якщо файлу немає —
//     показується емодзі (pic() це вміє). Тому нові острови працюють
//     одразу, а малюнки доливаються потім і нічого не ламають;
//   • кожна озвучка — пара [id, текст]. Немає файлу — читає синтезатор;
//   • завдання — звичайний об'єкт {prompt, speak, stage, answer, options}.

// ---------- Слова на всі літери абетки.
// Демоверсія мала 17 слів і 19 літер — на «перший звук» цього досить, на
// повний 1 клас ні. Дописано так, щоб кожна літера, з якої українське
// слово МОЖЕ починатися, мала свою картинку.
// Дві літери сюди не входять навмисне: з «и» та «ь» слова не починаються,
// тож шукати їхній «перший звук» — вчити неправди.
WORDS.push(
  ['w_avtobus','🚌','автобус','А'], ['w_hryb','🍄','гриб','Г'],
  ['w_gava','🐦','ґава','Ґ'],       ['w_eskimo','🍦','ескімо','Е'],
  ['w_yenot','🦝','єнот','Є'],      ['w_zaiets','🐰','заєць','З'],
  ['w_indyk','🦃','індик','І'],     ['w_yizhak','🦔','їжак','Ї'],
  ['w_yohurt','🥛','йогурт','Й'],   ['w_nizh','🔪','ніж','Н'],
  ['w_olivets','✏️','олівець','О'], ['w_tort','🎂','торт','Т'],
  ['w_udav','🐍','удав','У'],       ['w_farba','🎨','фарба','Ф'],
  ['w_tsybulia','🧅','цибуля','Ц'], ['w_cherepakha','🐢','черепаха','Ч'],
  ['w_shapka','🧢','шапка','Ш'],    ['w_shchuka','🐠','щука','Щ'],
  ['w_yula','🪀','юла','Ю'],        ['w_dim','🏡','дім','Д'],
  ['w_vikno','🪟','вікно','В'],     ['w_kvitka','🌼','квітка','К'],
  ['w_more','🌊','море','М'],       ['w_ptakh','🐦‍⬛','птах','П'],
  ['w_raketa','🚀','ракета','Р'],   ['w_sumka','🎒','сумка','С'],
  ['w_litak','✈️','літак','Л'],     ['w_bananu','🍌','банан','Б'],
  ['w_zholud','🌰','жолудь','Ж'],  ['w_khmara','☁️','хмара','Х'],
);
// Перебудовуємо похідні набори: вони рахувалися до того, як слова додалися.
Object.assign(BY_ID, Object.fromEntries(WORDS.map(w => [w[0], w])));
Object.assign(EMO, Object.fromEntries(WORDS.map(w => [w[0], w[1]])));
// Літери для хибних варіантів — уже всі 33, крім тих двох.
LETTERS.length = 0;
LETTERS.push(...'АБВГҐДЕЄЖЗІЇЙКЛМНОПРСТУФХЦЧШЩЮЯ'.split(''));
// Наліпки гра збирає з WORDS нижче по файлу — тому вони самі підхоплять
// нові слова, нічого скидати не треба.

// ---------- Склади: до наявних п'яти приголосних додано решту відкритих.
SYLL.push('ра','ро','ру','та','то','ту','да','до','ду','па','по','пу',
          'ва','во','ву','ба','бо','бу','га','го','гу','за','зо','зу');
// Нові слова з відкритих складів — друга й третя хвиля читання.
WORDS_READ.push(['рука','РУ·КА'],['вода','ВО·ДА'],['дорога','ДО·РО·ГА'],
  ['гора','ГО·РА'],['коза','КО·ЗА'],['тато','ТА·ТО'],['пора','ПО·РА'],
  ['рама','РА·МА'],['губа','ГУ·БА'],['вата','ВА·ТА']);
// Скільки складів у нових словах — для Острова Звуків.
SYLW.push(['w_dim',1],['w_nizh',1],['w_tort',1],['w_ptakh',1],['w_udav',2],
  ['w_hryb',1],['w_gava',2],['w_more',2],['w_vikno',2],['w_kvitka',2],
  ['w_shapka',2],['w_farba',2],['w_khmara',2],['w_sumka',2],['w_yula',2],
  ['w_zaiets',2],['w_yizhak',2],['w_litak',2],['w_raketa',3],['w_tsybulia',3],
  ['w_olivets',3],['w_avtobus',3],['w_cherepakha',4],['w_yohurt',3]);

// ---------- Ідентифікатор кліпа з українського слова.
// Потрібен там, де id складається на льоту з того самого слова, яке
// звучить. Кирилицю в імені файлу брати не можна, а порожній id теж не
// годиться: say() такий шматок МОВЧКИ ПРОПУСКАЄ, а не читає синтезатором
// — слово просто зникло б із озвучення.
const TR = {а:'a',б:'b',в:'v',г:'h',ґ:'g',д:'d',е:'e',є:'ie',ж:'zh',з:'z',
  и:'y',і:'i',ї:'i',й:'j',к:'k',л:'l',м:'m',н:'n',о:'o',п:'p',р:'r',с:'s',
  т:'t',у:'u',ф:'f',х:'kh',ц:'c',ч:'ch',ш:'sh',щ:'shch',ь:'',ю:'iu',я:'ia'};
const uaId = s => String(s).toLowerCase().split('')
  .map(c => TR[c] !== undefined ? TR[c] : (/[a-z0-9]/.test(c) ? c : '')).join('');

// ---------- Звук для завдань на слух. Файлів не треба: ті самі два-три
// тони з WebAudio, що вже звучать на правильну відповідь. Для ритму й
// темпу цього досить, бо дитина порівнює ДОВЖИНУ й ШВИДКІСТЬ, не тембр.
const PATS = {};
function playPat(id){ const s = PATS[id]; if (s) beep(s, .12); }
window.playPat = playPat;
// Кнопка «послухати» всередині завдання. Клас не .ans — інакше гра
// порахувала б її за варіант відповіді.
const earBtn = (id, label) =>
  `<button class="say" type="button" onclick="playPat('${id}')">🔊 ${label || 'Послухати'}</button>`;
let patNo = 0;
function mkPat(seq){ const id = 'pt' + (++patNo); PATS[id] = seq; return id; }

// ============ МОРЕ ЧИСЕЛ ============

// ---------- Острів Двадцяти: десяток і одиниці. Дитина бачить саме
// десяток як ціле — звідси й картинка з рядком із десяти.
function num20Tasks(v){
  const t = [], p = pic('o_apple','🍎');
  const ten = `<span class="side">${p.repeat(10)}</span>`;
  for (let i = 0; i < 3; i++){
    const k = 1 + rnd(9), N = 10 + k;
    t.push({prompt:'Скільки тут предметів?', speak:[P.count],
      stage:`${ten}<span class="op">+</span><span class="side">${p.repeat(k)}</span>`,
      answer:String(N), options: numOpts(N, 11, 20, v===1 ? 3 : 4)});
  }
  for (let i = t.length; i < 5; i++){
    const N = 11 + rnd(9);
    // Саме число НЕ озвучуємо: воно велике на екрані, і прочитати його —
    // це і є завдання. Попри те, записів чисел понад дванадцять у грі
    // немає, і n(N) для N від 13 віддавало undefined замість тексту.
    if (v === 3){
      t.push({prompt:`Скільки одиниць у числі ${N}?`,
        speak:[['q_ones', 'Скільки одиниць у цьому числі?']],
        stage:`<span class="word">${N}</span>`,
        answer:String(N % 10), options: numOpts(N % 10, 0, 9, 4)});
    } else {
      const next = rnd(2) ? N + 1 : N - 1;
      t.push({prompt: next > N ? `Яке число йде після ${N}?` : `Яке число йде перед ${N}?`,
        speak:[[next > N ? 'q_after' : 'q_before',
                next > N ? 'Яке число йде після цього?' : 'Яке число йде перед цим?']],
        stage:`<span class="word">${N}</span>`,
        answer:String(next), options: numOpts(next, 10, 20, 3)});
    }
  }
  return shuffle(t);
}

// ---------- Острів Сотні: лічба десятками. Головне тут — побачити, що
// після 20 нічого нового не починається, усе повторюється.
const DEC = [10,20,30,40,50,60,70,80,90,100];
function num100Tasks(v){
  const t = [];
  for (let i = 0; i < 3; i++){
    const k = rnd(8), row = [DEC[k], DEC[k+1]];
    t.push({prompt:`Лічимо десятками. Що буде після ${row[1]}?`,
      speak:[['q_dec','Лічимо десятками. Яке число буде далі?']],
      stage:`<span class="word">${row[0]} · ${row[1]} · ?</span>`,
      answer:String(DEC[k+2]),
      options: shuffle([DEC[k+2], DEC[k+2]+1, DEC[k+1]])
        .map(x => ({v:String(x), html:String(x)}))});
  }
  while (t.length < 5){
    const N = v === 1 ? DEC[rnd(9)] : 21 + rnd(79);
    const tens = Math.floor(N / 10);
    t.push({prompt:`Скільки десятків у числі ${N}?`,
      speak:[['q_tens','Скільки десятків у числі?']],
      stage:`<span class="word">${N}</span>`,
      answer:String(tens), options: numOpts(tens, 1, 10, v===3 ? 4 : 3)});
  }
  return shuffle(t);
}

// ---------- Острів Великих Дій: у межах 100 без переходу через розряд.
// Це остання тема року, і вона простіша, ніж здається: десятки з
// десятками, одиниці з одиницями.
function add100Tasks(v){
  return Array.from({length:5}, () => {
    const kind = v === 1 ? 0 : v === 2 ? rnd(2) : rnd(3);
    let a, b, r, sign;
    if (kind === 0){                       // круглі десятки
      a = 10 * (1 + rnd(7)); b = 10 * (1 + rnd(9 - a/10)); sign = '+'; r = a + b;
    } else if (kind === 1){                // двоцифрове плюс одиниці
      a = 10 * (1 + rnd(8)) + rnd(5); b = 1 + rnd(9 - a % 10); sign = '+'; r = a + b;
    } else {                               // віднімання одиниць
      a = 10 * (1 + rnd(8)) + 4 + rnd(5); b = 1 + rnd(a % 10); sign = '−'; r = a - b;
    }
    return {prompt:`${a} ${sign} ${b} = ?`,
      speak:[n(Math.min(a,10)), sign === '+' ? P.plus : P.took],
      stage:`<span class="word">${a} ${sign} ${b} = ?</span>`,
      answer:String(r),
      options: numOpts(r, Math.max(0, r - 12), r + 12, v===3 ? 4 : 3)};
  });
}

// ---------- Острів Мірок: довжина, маса, місткість. Міряти по-справжньому
// планшет не вміє, тому тут інше й чесніше: ЧИМ це міряють і що більше.
const UNITS = [
  ['cm','сантиметр','u_cm','📏', ['олівець','гумка','зошит']],
  ['m','метр','u_m','📐', ['кімната','двері','паркан']],
  ['kg','кілограм','u_kg','⚖️', ['кавун','мішок картоплі','гарбуз']],
  ['l','літр','u_l','🥛', ['молоко','відро води','сік']],
];
function measureTasks(v){
  const t = [];
  for (const u of pick(UNITS, 3)){
    const k = rnd(u[4].length), thing = u[4][k];
    t.push({prompt:`У чому міряють: ${thing}?`,
      speak:[['q_unit','У чому це міряють?'], [`th_${u[0]}_${k}`, thing]],
      stage:`<span class="big">${u[3]}</span><span class="word">${thing}</span>`,
      answer:u[0],
      options: shuffle(UNITS).map(x => say1(x[0], x[1], x[2]))});
  }
  const LONG = [['w_litak','✈️',3],['w_avtobus','🚌',2],['w_olivets','✏️',1],
                ['w_derevo','🌳',3],['w_kvitka','🌼',1]];
  for (let i = t.length; i < 5; i++){
    let [a, b] = pick(LONG, 2), spin = 0;
    while (a[2] === b[2] && spin++ < 40) [a, b] = pick(LONG, 2);
    t.push({prompt:'Що довше?', speak:[['q_longer','Що довше?']], stage:'',
      answer: a[2] > b[2] ? a[0] : b[0],
      options: [a, b].map(x => ({v:x[0], html: pic(x[0], x[1])}))});
  }
  return shuffle(t);
}

// ---------- Острів Задач: проста сюжетна задача. Дитина 1 класу її не
// прочитає, тому задача звучить голосом, а на сцені — та сама історія
// картинками. Питання не «порахуй», а «що тут треба зробити».
function taskTasks(v){
  const t = [];
  const F = () => FRUIT[rnd(FRUIT.length)];
  for (let i = 0; i < 5; i++){
    const plus = v === 1 ? true : Math.random() < .5;
    const f = F(), p = pic(f[0], f[1]);
    let a = 2 + rnd(v === 1 ? 4 : 7), b = 1 + rnd(Math.min(a, 5));
    const r = plus ? a + b : a - b;
    const story = plus
      ? `Було ${a}. Принесли ще ${b}.`
      : `Було ${a}. Віддали ${b}.`;
    if (v === 3){
      // На складному рівні питають не відповідь, а дію — це і є розуміння
      // задачі, а не лічба.
      // Історія складається з уже записаних шматків (числа, «додати»,
      // «забрали»), а не одним кліпом: числа в ній щоразу інші, і один
      // запис казав би не ті, що на екрані.
      t.push({prompt: story + ' Яку дію треба виконати?',
        speak:[['s_story','Послухай задачу.'], P.was, n(a),
               plus ? P.plus : P.took, n(b),
               ['q_action','Яку дію треба виконати?']],
        stage:`<span class="side">${p.repeat(a)}</span>`,
        answer: plus ? 'add' : 'sub',
        options:[say1('add','додати','a_add'), say1('sub','відняти','a_sub')]});
    } else {
      t.push({prompt: story + ' Скільки стало?',
        speak:[['s_story','Послухай задачу.'], n(a), plus?P.plus:P.took, n(b), P.together],
        stage:`<span class="side">${p.repeat(a)}</span><span class="op">${plus?'+':'−'}</span>`
              + `<span class="side">${p.repeat(b)}</span>`,
        answer:String(r), options: numOpts(r, 0, 12, v===2 ? 4 : 3)});
    }
  }
  return t;
}

// ---------- Острів Таблиць: читання даних. Проста таблиця з двох рядків —
// рівно те, що в програмі зветься «читає дані, вміщені в таблиці».
function dataTasks(v){
  return Array.from({length:5}, () => {
    const rows = pick(FRUIT, v === 1 ? 2 : 3)
      .map(f => [f, 1 + rnd(v === 3 ? 9 : 5)]);
    const k = rnd(rows.length), [f, cnt] = rows[k];
    const most = rows.reduce((a, b) => b[1] > a[1] ? b : a);
    const askMost = v === 3 && Math.random() < .5;
    const tbl = `<table class="tbl">${rows.map(([ff, c]) =>
      `<tr><td>${pic(ff[0], ff[1])}</td><td class="n">${c}</td></tr>`).join('')}</table>`;
    return askMost
      ? {prompt:'Чого найбільше?', speak:[['q_most','Чого найбільше?']], stage:tbl,
         answer:most[0][0],
         options: rows.map(([ff]) => ({v:ff[0], html: pic(ff[0], ff[1])}))}
      : {prompt:'Скільки цього в таблиці?', speak:[['q_howmany','Скільки цього в таблиці?']],
         stage:`${tbl}<span class="big">${pic(f[0], f[1])}</span>`,
         answer:String(cnt), options: numOpts(cnt, 1, 10, v===1 ? 3 : 4)};
  });
}

// ---------- Острів Ліній: точка, пряма, промінь, відрізок, ламана, коло
// й симетрія. Малюємо просто в SVG — жодних файлів.
const LINEART = {
  dot:   '<circle cx="50" cy="30" r="4"/>',
  // У прямої НЕ МАЄ бути жодної крапки: саме крапки й відрізняють її від
  // променя (одна) і відрізка (дві). З крапкою посередині всі три на
  // екрані завбільшки з долоню зливалися в одне.
  line:  '<path d="M2 30 H98"/>',
  ray:   '<path d="M20 30 H96"/><circle cx="20" cy="30" r="4"/>',
  seg:   '<path d="M20 30 H80"/><circle cx="20" cy="30" r="4"/><circle cx="80" cy="30" r="4"/>',
  broken:'<path d="M10 48 L34 14 L58 44 L90 16"/>',
  curve: '<path d="M8 44 C28 8 72 56 92 18"/>',
  circ:  '<circle cx="50" cy="30" r="22" fill="none"/>',
};
const LINES = [['dot','точка','ln_dot'], ['line','пряма','ln_line'],
  ['ray','промінь','ln_ray'], ['seg','відрізок','ln_seg'],
  ['broken','ламана','ln_broken'], ['curve','крива','ln_curve'],
  ['circ','коло','ln_circ']];
const svgLine = k => `<svg class="ln" viewBox="0 0 100 60">${LINEART[k]}</svg>`;
// Симетрія: та сама фігура з дзеркальною половиною або без неї.
const SYM = [['🦋',true],['🌳',true],['🏠',true],['⭐',true],['🍃',false],
             ['🌙',false],['🥾',false],['🎸',false]];
function linesTasks(v){
  const t = [];
  const pool = v === 1 ? LINES.slice(0, 4) : LINES;
  for (const l of pick(pool, 3))
    t.push({prompt:`Покажи, де ${l[1]}`, speak:[P.show, [l[2], l[1]]],
      stage:'', answer:l[0],
      options: optsFrom(pool, l, v===1 ? 3 : 4, o => ({v:o[0], html: svgLine(o[0])}))});
  for (let i = t.length; i < 5; i++){
    const [emo, sym] = SYM[rnd(SYM.length)];
    t.push({prompt:'Чи можна скласти цю картинку навпіл так, щоб половинки збіглися?',
      speak:[['q_sym','Чи можна скласти цю картинку навпіл так, щоб половинки збіглися?']],
      stage:`<span class="big">${emo}</span>`,
      answer: sym ? 'yes' : 'no',
      options:[say1('yes','так','a_yes'), say1('no','ні','a_no')]});
  }
  return shuffle(t);
}

// ============ МОРЕ МОВИ ============

// ---------- Острів Наголосу. Слово показано складами, дитина обирає той,
// що вимовляється сильніше. Наголошений склад у підписі великий —
// підказка лише після помилки, тому в завданні він звичайний.
const STRESSW = [
  ['st_mama','мама',['ма','ма'],0],  ['st_voda','вода',['во','да'],1],
  ['st_ryba','риба',['ри','ба'],0],  ['st_doroha','дорога',['до','ро','га'],1],
  ['st_korova','корова',['ко','ро','ва'],1], ['st_sumka','сумка',['сум','ка'],0],
  ['st_raketa','ракета',['ра','ке','та'],1], ['st_kvitka','квітка',['квіт','ка'],0],
  ['st_moloko','молоко',['мо','ло','ко'],2], ['st_olivets','олівець',['о','лі','вець'],2],
];
// Пара слів, де наголос міняє значення — найцікавіше в темі.
const STRESSP = [
  ['замок','зáмок — де живе король','замóк — щоб замкнути двері'],
  ['мука','мýка — з неї печуть хліб','мýка — коли дуже важко'],
];
function stressTasks(v){
  const pool = v === 1 ? STRESSW.filter(w => w[2].length === 2) : STRESSW;
  return pick(pool, 5).map(([id, w, sy, k]) => ({
    prompt:'Який склад вимовляється сильніше?',
    speak:[[id, w], ['q_stress','Який склад вимовляється сильніше?']],
    stage:`<span class="word">${sy.join('·')}</span>`,
    answer:String(k),
    options: sy.map((s, i) => ({v:String(i), html:s.toUpperCase()}))}));
}

// ---------- Острів Речення: велика літера, крапка, знак питання й оклику,
// скільки слів. Читати дитина ще не вміє, тому речення й звучить.
const SENTS = [
  ['Кіт спить.', 2, '.', 's_kit'],
  ['Мама пече пиріг.', 3, '.', 's_mama'],
  ['Де мій зошит?', 3, '?', 's_de'],
  ['Яка гарна квітка!', 3, '!', 's_yaka'],
  ['Тато читає книжку.', 3, '.', 's_tato'],
  ['Хто там?', 2, '?', 's_khto'],
  ['Ура, канікули!', 2, '!', 's_ura'],
  ['Пташка летить високо.', 3, '.', 's_ptashka'],
];
function sentTasks(v){
  const t = [];
  for (const [s, k, mark, id] of pick(SENTS, 3)){
    if (v === 1){
      t.push({prompt:'Скільки слів у реченні?', speak:[[id, s], ['q_words','Скільки слів у реченні?']],
        stage:`<span class="word">${s}</span>`, answer:String(k),
        options: numOpts(k, 1, 5, 3)});
    } else {
      t.push({prompt:'Який знак має стояти в кінці?',
        speak:[[id, s], ['q_mark','Який знак має стояти в кінці?']],
        stage:`<span class="word">${s.slice(0, -1)} ?</span>`, answer:mark,
        options: shuffle(['.', '?', '!']).map(x => ({v:x, html:x}))});
    }
  }
  while (t.length < 5){
    const [s] = SENTS[rnd(SENTS.length)];
    const low = s[0].toLowerCase() + s.slice(1);
    t.push({prompt:'Яке речення записано правильно?',
      speak:[['q_cap','Яке речення записано правильно? Речення починається з великої букви.']],
      stage:'', answer:'ok',
      options: shuffle([{v:'ok', html:s}, {v:'no', html:low}])});
  }
  return shuffle(t);
}

// ---------- Острів Алфавіту: яка буква сусідня і де можна перенести слово.
const ABC = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'.split('');
const HYPH = [['ма-ма','мама'],['во-да','вода'],['ри-ба','риба'],
  ['кві-тка','квітка'],['до-ро-га','дорога'],['ра-ке-та','ракета'],
  ['су-мка','сумка'],['мо-ло-ко','молоко']];
function abcTasks(v){
  const t = [];
  for (let i = 0; i < 3; i++){
    const k = 1 + rnd(ABC.length - 2), after = rnd(2) === 1;
    const right = after ? ABC[k+1] : ABC[k-1];
    const opts = new Set([right]);
    while (opts.size < (v === 3 ? 4 : 3)) opts.add(ABC[rnd(ABC.length)]);
    t.push({prompt: after ? `Яка буква йде після ${ABC[k]}?` : `Яка буква йде перед ${ABC[k]}?`,
      speak:[[after ? 'q_lafter' : 'q_lbefore',
              after ? 'Яка буква йде після цієї?' : 'Яка буква йде перед цією?']],
      stage:`<span class="word">${ABC[k]}</span>`, answer:right,
      options: shuffle([...opts]).map(x => ({v:x, html:x}))});
  }
  for (const [split, w] of pick(HYPH, 2)){
    const wrong = w.slice(0, 1) + '-' + w.slice(1);
    t.push({prompt:'Як правильно перенести слово?',
      speak:[['q_hyph','Як правильно перенести слово? Переносимо по складах.'], ['hw_'+uaId(w), w]],
      stage:'', answer:split,
      options: shuffle([{v:split, html:split}, {v:wrong, html:wrong}])});
  }
  return shuffle(t);
}

// ---------- Острів Значень: близькі й протилежні слова, слова з двома
// значеннями. Усі варіанти озвучені — читати їх дитина ще не може.
const SYN = [['великий','здоровенний','v_zdorovennyj'],['гарний','красивий','v_krasyvyj'],
  ['швидко','хутко','v_khutko'],['сумний','невеселий','v_neveselyj'],['холодний','студений','v_studenyj']];
const ANT = [['великий','малий','v_vel','v_mal'],['високий','низький','v_vys','v_nyz'],
  ['теплий','холодний','v_tep','v_khol'],['день','ніч','v_den','v_nich'],
  ['далеко','близько','v_dal','v_bly'],['швидко','повільно','v_shv','v_pov']];
const POLY = [['ключ','🔑','🎼'],['коса','💇','🌾'],['лист','🍃','✉️'],['ручка','🖊️','🚪']];
function meanTasks(v){
  const t = [];
  for (const [a, b, vb] of pick(SYN, v === 1 ? 2 : 2)){
    const others = pick(ANT.map(x => x[1]).filter(x => x !== b), 2);
    t.push({prompt:`Яке слово означає майже те саме, що «${a}»?`,
      speak:[['q_syn','Яке слово означає майже те саме?'], ['v_'+uaId(a), a]],
      stage:`<span class="word">${a}</span>`, answer:b,
      options: shuffle([say1(b, b, vb)].concat(others.map(x => say1(x, x, 'v_'+uaId(x)))))});
  }
  for (const [a, b, va, vb] of pick(ANT, 2)){
    const others = pick(ANT.flatMap(x => [x[0], x[1]]).filter(x => x !== a && x !== b), 2);
    t.push({prompt:`Яке слово протилежне до «${a}»?`,
      speak:[['q_ant','Яке слово протилежне за значенням?'], [va, a]],
      stage:`<span class="word">${a}</span>`, answer:b,
      options: shuffle([say1(b, b, vb)].concat(others.map(x => say1(x, x, 'v_'+uaId(x)))))});
  }
  const [w, e1, e2] = POLY[rnd(POLY.length)];
  t.push({prompt:`Слово «${w}» має два значення. Покажи обидва.`,
    speak:[['q_poly','Це слово має два значення.'], ['v_'+uaId(w), w]],
    stage:`<span class="word">${w}</span>`, answer:'both',
    options: shuffle([{v:'both', html:`${e1} ${e2}`},
                      {v:'one', html:`${e1} ${FRUIT[rnd(FRUIT.length)][1]}`}])});
  return shuffle(t).slice(0, 5);
}

// ---------- Острів Груп Слів: тематична група, родова й видова назва.
const GROUPS = [
  ['меблі','g_mebli',['🪑','🛏️','🚪'],'🍎'],
  ['посуд','g_posud',['🍽️','🥄','🍵'],'🐱'],
  ['одяг','g_odiah',['👕','👖','🧥'],'🚗'],
  ['овочі','g_ovochi',['🥕','🥔','🧅'],'🦆'],
  ['фрукти','g_frukty',['🍎','🍐','🍌'],'🔨'],
  ['транспорт','g_transport',['🚌','🚂','✈️'],'🌼'],
  ['інструменти','g_instr',['🔨','🪚','🪛'],'🐟'],
  ['птахи','g_ptakhy',['🐦','🦆','🦉'],'🐘'],
];
function groupTasks(v){
  const t = [];
  for (const g of pick(GROUPS, 3)){
    const row = shuffle(g[2].concat([g[3]]));
    t.push({prompt:'Що тут зайве?', speak:[P.odd], stage:'', answer:g[3],
      options: row.map(e => ({v:e, html:`<span class="big">${e}</span>`}))});
  }
  for (const g of pick(GROUPS, 2)){
    const others = pick(GROUPS.filter(x => x[0] !== g[0]), v === 3 ? 3 : 2);
    t.push({prompt:'Як назвати це одним словом?',
      speak:[['q_gname','Як назвати це одним словом?']],
      stage:`<span class="rowpics">${g[2].map(e => `<span class="big">${e}</span>`).join('')}</span>`,
      answer:g[0],
      options: shuffle([say1(g[0], g[0], g[1])]
        .concat(others.map(x => say1(x[0], x[0], x[1]))))});
  }
  return shuffle(t);
}

// ---------- Острів Питань: хто? що? який? що робить? скільки?
// Це перший крок до частин мови, тільки без термінів.
const QW = [
  ['who','хто?','qw_who',['🐱','🐻','🦊','🦉']],
  ['what','що?','qw_what',['🏠','🍎','✏️','🎒']],
  ['which','який?','qw_which',['червоний','великий','теплий','м’який']],
  ['does','що робить?','qw_does',['біжить','співає','пише','спить']],
  ['many','скільки?','qw_many',['один','два','п’ять','десять']],
];
function qwTasks(v){
  const pool = v === 1 ? QW.slice(0, 2) : v === 2 ? QW.slice(0, 4) : QW;
  return Array.from({length:5}, () => {
    const q = pool[rnd(pool.length)], item = q[3][rnd(q[3].length)];
    const isPic = q[0] === 'who' || q[0] === 'what';
    return {prompt:`Яке питання тут підходить?`,
      speak:[['q_qw','Яке питання підходить до цього слова?'],
             ['qv_'+uaId(item), isPic ? '' : item]].filter(x => x[1] !== ''),
      stage: isPic ? `<span class="big">${item}</span>` : `<span class="word">${item}</span>`,
      answer:q[0],
      options: shuffle(pool).map(x => say1(x[0], x[1], x[2]))};
  });
}

// ---------- Острів Тексту: заголовок, скільки речень, який це жанр.
const TEXTS = [
  ['tx_kit', 'Кіт Мурчик жив у хаті. Він любив спати на печі. Щоранку Мурчик зустрічав господиню.',
   3, 'Кіт Мурчик', ['Пиріг','Дощ'], 'опов'],
  ['tx_vesna','Прийшла весна. Розтанув сніг. Защебетали пташки.',
   3, 'Весна', ['Зима','Школа'], 'опов'],
  ['tx_zahadka','Не б’є, не лає, а всі його бояться.', 1, 'Загадка', ['Казка','Вірш'], 'заг'],
];
const GENRE = [['заг','загадка','g_zah'],['kaz','казка','g_kaz'],
  ['vir','вірш','g_vir'],['опов','оповідання','g_opov'],
  ['лiч','лічилка','g_lich'],['ско','скоромовка','g_sko']];
function textTasks(v){
  const t = [];
  for (const [id, body, k, title, bad, gen] of TEXTS){
    t.push({prompt:'Скільки речень у тексті?',
      speak:[[id, body], ['q_sent','Скільки речень у тексті?']],
      stage:`<span class="word small">${body}</span>`, answer:String(k),
      options: numOpts(k, 1, 5, 3)});
    t.push({prompt:'Який заголовок підходить?',
      speak:[[id, body], ['q_title','Який заголовок підходить?']],
      stage:`<span class="word small">${body}</span>`, answer:title,
      options: shuffle([title].concat(bad)).map(x => say1(x, x, 'ti_'+uaId(x)))});
    if (v === 3)
      t.push({prompt:'Що це за твір?',
        speak:[[id, body], ['q_genre','Що це за твір?']],
        stage:`<span class="word small">${body}</span>`, answer:gen,
        options: optsFrom(GENRE, GENRE.find(g => g[0] === gen), 4,
          g => say1(g[0], g[1], g[2]))});
  }
  return shuffle(t).slice(0, 5);
}
