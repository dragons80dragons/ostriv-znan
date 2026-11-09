// ============ МОРЕ СВІТУ ============

// ---------- Острів Тіла: органи чуття й частини тіла. Нічого «медичного»:
// рівно те, що в програмі — «чим я пізнаю світ».
const SENSE = [
  ['eye','очі','sn_eye','👁️', ['веселка','зірки','малюнок','колір']],
  ['ear','вуха','sn_ear','👂', ['пісня','грім','дзвінок','шепіт']],
  ['nose','ніс','sn_nose','👃', ['квітка','хліб','дим','парфуми']],
  ['tongue','язик','sn_tongue','👅', ['цукерка','лимон','сіль','мед']],
  ['hand','шкіра','sn_hand','✋', ['тепло','холод','колючка','м’яке']],
];
const BODY = [['head','голова','bd_head','🧠'],['hand2','рука','bd_hand','✋'],
  ['leg','нога','bd_leg','🦵'],['eye2','око','bd_eye','👁️'],
  ['ear2','вухо','bd_ear','👂'],['tooth','зуб','bd_tooth','🦷']];
function bodyTasks(v){
  const t = [];
  for (const s of pick(SENSE, 3)){
    const k = rnd(s[4].length), thing = s[4][k];
    // Ідентифікатор кліпа складаємо з латинської назви чуття й номера
    // речі, а не з самого українського слова: id з кирилицею не збігся б
    // з жодним файлом, і гра щоразу читала б це синтезатором.
    t.push({prompt:`Чим ми це відчуваємо: ${thing}?`,
      speak:[['q_sense','Чим ми це відчуваємо?'], [`sx_${s[0]}_${k}`, thing]],
      stage:`<span class="word">${thing}</span>`, answer:s[0],
      // Варіанти добираємо через optsFrom: він кладе правильну відповідь
      // першою і тільки потім добирає решту. Самописний «перемішати й
      // обрізати» цього не гарантує — правильна відповідь інколи випадала
      // зі списку, і завдання ставало без відповіді.
      options: optsFrom(SENSE, s, v===1 ? 3 : 4,
        x => ({v:x[0], html:`<span class="big">${x[3]}</span>`}))});
  }
  for (const b of pick(BODY, 2))
    t.push({prompt:`Покажи, де ${b[1]}`, speak:[P.show, [b[2], b[1]]], stage:'',
      answer:b[0],
      options: optsFrom(BODY, b, v===3 ? 4 : 3,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  return shuffle(t);
}

// ---------- Острів Безпеки. Теми звідси діти проходять раз на рік і
// забувають; у грі їх можна повторювати скільки завгодно.
const DANGER = [
  ['🔥','вогонь',true],['🔪','ніж',true],['💊','ліки',true],['🔌','розетка',true],
  ['🧴','хімія',true],['🧸','ведмедик',false],['📗','книжка',false],
  ['🥕','морква',false],['✏️','олівець',false],['⚽','мʼяч',false]];
const RULES = [
  ['Загорівся вогонь удома. Що робити?','sf_fire','вийти й покликати дорослих',
   ['погасити самому','сховатися під ліжко']],
  ['Незнайомець кличе сісти в машину. Що робити?','sf_stranger','відмовитись і відійти',
   ['сісти й поїхати','розповісти йому адресу']],
  ['Ти побачив незнайомий предмет на вулиці. Що робити?','sf_object','не чіпати й сказати дорослим',
   ['узяти додому','розібрати, що всередині']],
  ['Світлофор горить червоним. Що робити?','sf_light','стояти й чекати',
   ['швидко перебігти','іти повільно']],
];
function safeTasks(v){
  const t = [];
  for (const d of pick(DANGER, 3)){
    const pair = DANGER.filter(x => x[2] !== d[2]);
    const other = pair[rnd(pair.length)];
    t.push({prompt:'Що тут небезпечне?', speak:[['q_danger','Що тут небезпечне?']],
      stage:'', answer: d[2] ? d[0] : other[0],
      options: shuffle([d, other]).map(x => ({v:x[0], html:`<span class="big">${x[0]}</span>`}))});
  }
  for (const [q, id, right, bad] of pick(RULES, 2))
    t.push({prompt:q, speak:[[id, q]], stage:'', answer:right,
      options: shuffle([right].concat(bad)).map(x => say1(x, x, 'sa_' + uaId(x).slice(0, 10)))});
  return shuffle(t);
}

// ---------- Острів Знаків. Застережні знаки й сигнали — пряма вимога
// програми (СЗО 3.2, СЗО 4.7), і, на жаль, не навчальна абстракція.
const SIGNS = [
  ['stop','Прохід заборонено','sg_stop','⛔'],
  ['alarm','Повітряна тривога','sg_alarm','🚨'],
  ['mine','Обережно: міни','sg_mine','☠️'],
  ['cross','Пішохідний перехід','sg_cross','🚸'],
  ['exit','Вихід','sg_exit','🚪'],
  ['nowater','Воду не пити','sg_nowater','🚱'],
  ['elec','Небезпечно: електрика','sg_elec','⚡'],
  ['first','Перша допомога','sg_first','🏥'],
];
const SIGN_DO = [
  ['alarm','Почув сирену повітряної тривоги. Куди йти?','в укриття',['на подвірʼя','до вікна']],
  ['mine','Побачив знак «Обережно: міни». Що робити?','не заходити туди',['обійти по краю','подивитися зблизька']],
  ['cross','Бачиш знак «Пішохідний перехід». Що він означає?','тут можна переходити дорогу',
   ['тут можна гратися','тут зупинка']],
];
function signsTasks(v){
  const t = [];
  const pool = v === 1 ? SIGNS.slice(0, 5) : SIGNS;
  for (const s of pick(pool, 3))
    t.push({prompt:`Покажи знак «${s[1]}»`, speak:[P.show, [s[2], s[1]]], stage:'',
      answer:s[0],
      options: optsFrom(pool, s, v===1 ? 3 : 4,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  for (const [key, q, right, bad] of pick(SIGN_DO, 2)){
    const s = SIGNS.find(x => x[0] === key);
    t.push({prompt:q, speak:[['sq_'+key, q]],
      stage:`<span class="big">${s[3]}</span>`, answer:right,
      options: shuffle([right].concat(bad)).map(x => say1(x, x, 'sr_' + uaId(x).slice(0, 10)))});
  }
  return shuffle(t);
}

// ---------- Острів Країни: назва, столиця, символи держави.
const COUNTRY = [
  ['flag','прапор України','cn_flag','🇺🇦'],
  ['kyiv','Київ','cn_kyiv','🏛️'],
  ['tryzub','герб — тризуб','cn_tryzub','🔱'],
  ['kalyna','калина','cn_kalyna','🌺'],
  ['sonyash','соняшник','cn_sonyash','🌻'],
  ['vyshyv','вишиванка','cn_vyshyv','👚'],
];
const NOTOURS = [['🇵🇱','Польща'],['🇩🇪','Німеччина'],['🇫🇷','Франція'],['🇬🇧','Британія']];
function countryTasks(v){
  const t = [];
  for (const c of pick(COUNTRY, 3))
    t.push({prompt:`Покажи: ${c[1]}`, speak:[P.show, [c[2], c[1]]], stage:'', answer:c[0],
      options: optsFrom(COUNTRY, c, v===1 ? 3 : 4,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  t.push({prompt:'Де прапор України?', speak:[['q_flag','Де прапор України?']], stage:'',
    answer:'ua',
    options: shuffle([{v:'ua', html:'<span class="big">🇺🇦</span>'}]
      .concat(pick(NOTOURS, 2).map(([e]) => ({v:e, html:`<span class="big">${e}</span>`}))))});
  t.push({prompt:'Як називається столиця України?',
    speak:[['q_capital','Як називається столиця України?']], stage:'', answer:'Київ',
    options: shuffle(['Київ','Львів','Одеса']).map(x => say1(x, x, 'ct_' + uaId(x)))});
  return shuffle(t);
}

// ---------- Острів Професій: хто що робить. Теми «світ професій» є і в
// ЯДС, і в «Дизайні і технологіях» — острів обслуговує обидві.
const JOBS = [
  ['likar','лікар','jb_likar','👩‍⚕️','лікує людей'],
  ['uchytel','учитель','jb_uchytel','👩‍🏫','навчає дітей'],
  ['pekar','пекар','jb_pekar','👨‍🍳','пече хліб'],
  ['vodii','водій','jb_vodii','🚌','возить людей'],
  ['pozhezh','пожежник','jb_pozhezh','🧑‍🚒','гасить пожежі'],
  ['budiv','будівельник','jb_budiv','👷','будує будинки'],
  ['fermer','фермер','jb_fermer','🧑‍🌾','вирощує овочі'],
  ['poshtar','поштар','jb_poshtar','📮','розносить листи'],
];
function jobsTasks(v){
  return Array.from({length:5}, () => {
    const j = JOBS[rnd(JOBS.length)];
    const byPic = v === 1 || Math.random() < .5;
    return byPic
      ? {prompt:`Хто ${j[4]}?`, speak:[['q_job','Хто це робить?'], ['jd_'+j[0], j[4]]],
         stage:`<span class="word">${j[4]}</span>`, answer:j[0],
         options: optsFrom(JOBS, j, v===3 ? 4 : 3,
           o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))}
      : {prompt:'Що робить ця людина?', speak:[['q_jobdo','Що робить ця людина?']],
         stage:`<span class="big">${j[3]}</span>`, answer:j[4],
         options: optsFrom(JOBS, j, v===3 ? 4 : 3, o => say1(o[4], o[4], 'jd_'+o[0]))};
  });
}

// ---------- Острів Живого: жива й нежива природа, рукотворне, частини
// рослини. Демоверсія вміла «живе чи ні» — тут додано частини рослини й
// третю групу, рукотворну: без неї діти записують у «неживе» і камінь, і стіл.
const NATURE = [
  ['🌳','жива'],['🐱','жива'],['🐝','жива'],['🌼','жива'],['🐟','жива'],['🍄','жива'],
  ['☁️','нежива'],['🌞','нежива'],['🪨','нежива'],['💧','нежива'],['⛰️','нежива'],
  ['🏠','рукотворна'],['🚌','рукотворна'],['✏️','рукотворна'],['🪑','рукотворна'],
];
const PLANT = [['korin','корінь','pl_korin','🪴'],['steblo','стебло','pl_steblo','🌿'],
  ['lystok','листок','pl_lystok','🍃'],['kvitka','квітка','pl_kvitka','🌸'],
  ['plid','плід','pl_plid','🍎'],['nasinnia','насіння','pl_nasinnia','🌰']];
function aliveTasks2(v){
  const t = [];
  const kinds = v === 1 ? ['жива','нежива'] : ['жива','нежива','рукотворна'];
  for (const [emo, kind] of pick(NATURE.filter(x => kinds.includes(x[1])), 3))
    t.push({prompt:'Це жива природа, нежива чи зроблена людиною?',
      speak:[P.alive], stage:`<span class="big">${emo}</span>`, answer:kind,
      options: kinds.map(k => say1(k, k, 'nt_' + uaId(k)))});
  for (const p of pick(PLANT, 2))
    t.push({prompt:`Покажи, де ${p[1]}`, speak:[P.show, [p[2], p[1]]], stage:'',
      answer:p[0],
      options: optsFrom(PLANT, p, v===3 ? 4 : 3,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  return shuffle(t);
}

// ---------- Острів Тварин: групи (комахи, риби, птахи, звірі) і дикі
// проти свійських.
const ANIM = [
  ['🐝','комаха',false],['🦋','комаха',false],['🐜','комаха',false],
  ['🐟','риба',false],['🐠','риба',false],
  ['🦆','птах',true],['🐔','птах',true],['🦉','птах',false],['🐦','птах',false],
  ['🐱','звір',true],['🐶','звір',true],['🐄','звір',true],
  ['🦊','звір',false],['🐻','звір',false],['🐘','звір',false],['🐭','звір',false],
];
const AGROUP = [['комаха','an_komakha'],['риба','an_ryba'],['птах','an_ptakh'],['звір','an_zvir']];
function animalsTasks(v){
  const t = [];
  for (const [emo, grp] of pick(ANIM, 3))
    t.push({prompt:'До якої групи належить ця тварина?',
      speak:[['q_agroup','До якої групи належить ця тварина?']],
      stage:`<span class="big">${emo}</span>`, answer:grp,
      options: AGROUP.map(([g, vo]) => say1(g, g, vo))});
  for (let i = t.length; i < 5; i++){
    const home = rnd(2) === 1;
    const right = ANIM.filter(a => a[2] === home)[rnd(ANIM.filter(a => a[2] === home).length)];
    const other = ANIM.filter(a => a[2] !== home)[rnd(ANIM.filter(a => a[2] !== home).length)];
    t.push({prompt: home ? 'Яка тварина свійська?' : 'Яка тварина дика?',
      speak:[[home ? 'q_tame' : 'q_wild', home ? 'Яка тварина свійська?' : 'Яка тварина дика?']],
      stage:'', answer:right[0],
      options: shuffle([right, other]).map(a => ({v:a[0], html:`<span class="big">${a[0]}</span>`}))});
  }
  return shuffle(t);
}

// ---------- Острів Матеріалів: з чого це зроблено. Сюди ж вторинна
// переробка — у програмі це ТЕО 3.2.
const MAT = [
  ['derevo','дерево','mt_derevo','🪵',['🪑','✏️','🪆']],
  ['papir','папір','mt_papir','📄',['📗','📰','🗒️']],
  ['metal','метал','mt_metal','🔩',['🔑','🔨','🥄']],
  ['sklo','скло','mt_sklo','🪟',['🫙','🍷','🔍']],
  ['tkanyna','тканина','mt_tkanyna','🧵',['👕','🧦','🧣']],
  ['plastyk','пластик','mt_plastyk','🧴',['🪣','🧃','🩴']],
];
const BIN = [['📄','папір'],['🫙','скло'],['🧴','пластик'],['🍌','органіка']];
function stuffTasks(v){
  const t = [];
  for (const m of pick(MAT, 3)){
    const thing = m[4][rnd(m[4].length)];
    t.push({prompt:'З чого це зроблено?', speak:[['q_mat','З чого це зроблено?']],
      stage:`<span class="big">${thing}</span>`, answer:m[0],
      options: optsFrom(MAT, m, v===1 ? 3 : 4, o => say1(o[0], o[1], o[2]))});
  }
  for (const [emo, bin] of pick(BIN, 2))
    t.push({prompt:'У який контейнер це викинути?',
      speak:[['q_bin','У який контейнер це викинути?']],
      stage:`<span class="big">${emo}</span>`, answer:bin,
      options: shuffle(BIN.map(b => b[1])).map(x => say1(x, x, 'bn_' + uaId(x)))});
  return shuffle(t);
}

// ---------- Острів Винаходів: що полегшило життя людині. Пара «було —
// стало» показує саму ідею винаходу, а не дату.
const INVENT = [
  ['колесо','🛞','тягти вантаж','🪵'],
  ['лампа','💡','свічка','🕯️'],
  ['холодильник','🧊','льох','🕳️'],
  ['телефон','📱','лист','✉️'],
  ['літак','✈️','кінь','🐴'],
  ['книжка','📗','усна розповідь','🗣️'],
];
function inventTasks(v){
  return Array.from({length:5}, () => {
    const i = INVENT[rnd(INVENT.length)];
    return {prompt:`Що люди мали ДО того, як зʼявився ${i[0]}?`,
      speak:[['q_inv','Що люди мали раніше, до цього винаходу?'], ['iv_'+uaId(i[0]), i[0]]],
      stage:`<span class="big">${i[1]}</span><span class="word">${i[0]}</span>`,
      answer:i[2],
      options: optsFrom(INVENT, i, v===3 ? 4 : 3,
        o => ({v:o[2], html:`<span class="big">${o[3]}</span>`}))};
  });
}

// ============ МОРЕ УВАГИ ============
// Сюди зібрано інформатичні теми: окремого предмета «інформатика» в
// 1 класі немає в жодній типовій програмі, і за Шияном вона розчинена
// в «Я досліджую світ». У грі їй найкраще саме тут.

// ---------- Острів Відчуттів: яка це інформація — зорова, слухова,
// дотикова, нюхова, смакова.
const INFO = [
  ['zor','зорова','if_zor','👁️',['малюнок','колір','світлофор','усмішка']],
  ['slukh','слухова','if_slukh','👂',['пісня','дзвінок','грім','голос']],
  ['dotyk','дотикова','if_dotyk','✋',['гаряче','шорстке','мʼяке','холодне']],
  ['niukh','нюхова','if_niukh','👃',['запах хліба','дим','квіти']],
  ['smak','смакова','if_smak','👅',['солодке','кисле','солоне']],
];
function infoTasks(v){
  const pool = v === 1 ? INFO.slice(0, 3) : INFO;
  return Array.from({length:5}, () => {
    const i = pool[rnd(pool.length)], k = rnd(i[4].length), thing = i[4][k];
    return {prompt:'Яка це інформація?',
      speak:[['q_info','Яка це інформація?'], [`in_${i[0]}_${k}`, thing]],
      stage:`<span class="word">${thing}</span>`, answer:i[0],
      options: optsFrom(pool, i, v===1 ? 3 : 4, x => say1(x[0], x[1], x[2]))};
  });
}

// ---------- Острів Запитань: питання «так / ні», відкрите, уточнювальне,
// і ключове слово для пошуку.
const ASKQ = [
  ['Ти любиш яблука?','yesno','aq_yabluka'], ['Це кіт?','yesno','aq_kit'], ['У тебе є брат?','yesno','aq_brat'],
  ['Що ти робив улітку?','open','aq_lito'], ['Як звати твого друга?','open','aq_druh'],
  ['Чому восени падає листя?','open','aq_lystia'],
  ['А котра саме година?','utoch','aq_hodyna'], ['Ти сказав про велику чи малу?','utoch','aq_velyka'],
];
const ASKT = [['yesno','можна відповісти «так» або «ні»','ak_yesno'],
  ['open','треба відповісти словами','ak_open'],
  ['utoch','уточнює те, що вже сказали','ak_utoch']];
const KEYW = [
  ['Хочу дізнатися, чим живляться їжаки','їжак','izhak',['ліс','зима']],
  ['Хочу дізнатися, коли цвіте вишня','вишня','vysh',['садок','весна']],
  ['Хочу дізнатися, як збудувати шпаківню','шпаківня','shpak',['дошка','птах']],
];
function askTasks(v){
  const t = [];
  for (const [q, kind, qid] of pick(ASKQ, 3))
    t.push({prompt:'Яке це запитання?', speak:[[qid, q]],
      stage:`<span class="word">${q}</span>`, answer:kind,
      options: ASKT.map(([k, name, vo]) => say1(k, name, vo))});
  for (const [want, key, id, bad] of pick(KEYW, 2))
    t.push({prompt:'Яке слово шукати?', speak:[['kw_'+id, want]],
      stage:`<span class="word small">${want}</span>`, answer:key,
      options: shuffle([key].concat(bad)).map(x => say1(x, x, 'kv_'+uaId(x)))});
  return shuffle(t);
}

// ---------- Острів Шифру: «так — ні» як 0 і 1, як колір, як жест.
// Перше в житті кодування, і воно справді таке просте.
const CODE = [
  ['Зелений — це…','🟢','так','ні','cd_green'],
  ['Червоний — це…','🔴','ні','так','cd_red'],
  ['Один — це…','1️⃣','так','ні','cd_one'],
  ['Нуль — це…','0️⃣','ні','так','cd_zero'],
  ['Кивок головою — це…','🙂','так','ні','cd_nod'],
];
function codeTasks(v){
  const t = [];
  for (const [q, emo, right, wrong, id] of pick(CODE, 3))
    t.push({prompt:q, speak:[[id, q]], stage:`<span class="big">${emo}</span>`,
      answer:right,
      options: shuffle([right, wrong]).map(x => say1(x, x, 'a_'+uaId(x)))});
  // Зворотний бік: закодувати відповідь самому.
  for (let i = t.length; i < 5; i++){
    const yes = rnd(2) === 1;
    t.push({prompt: yes ? 'Закодуй «так» кольором' : 'Закодуй «ні» кольором',
      speak:[[yes ? 'q_code_yes' : 'q_code_no', yes ? 'Закодуй «так» кольором' : 'Закодуй «ні» кольором']],
      stage:'', answer: yes ? '🟢' : '🔴',
      options: shuffle(['🟢','🔴']).map(x => ({v:x, html:`<span class="big">${x}</span>`}))});
  }
  return shuffle(t);
}

// ---------- Острів Правди: факт чи вигадка, правильне чи хибне
// твердження. Межа між «буває» і «не буває» — це вже логіка.
const FACTS = [
  ['Узимку йде сніг', true, 'tr_snih'],
  ['Корова дає молоко', true, 'tr_korova'],
  ['У риби є хвіст', true, 'tr_ryba'],
  ['Два плюс два буде чотири', true, 'tr_dva'],
  ['Кіт уміє літати', false, 'tr_kit'],
  ['Сонце світить уночі', false, 'tr_sonce'],
  ['Дерево ходить у школу', false, 'tr_derevo'],
  ['П’ять менше за три', false, 'tr_piat'],
];
function trueTasks(v){
  const pool = v === 1 ? FACTS.filter(f => !/плюс|менше/.test(f[0])) : FACTS;
  return pick(pool, 5).map(([s, ok, id]) => ({
    prompt:'Це правда чи вигадка?',
    speak:[['q_true','Це правда чи вигадка?'], [id, s]],
    stage:`<span class="word">${s}</span>`, answer: ok ? 'yes' : 'no',
    options:[say1('yes','правда','a_pravda'), say1('no','вигадка','a_vyhadka')]}));
}

// ---------- Острів Кроків: порядок дій. Те саме, що потім назветься
// алгоритмом, тільки на звичних справах.
const PLANS = [
  ['посадити квітку', ['🕳️','🌰','💧','🌱'], 'pn_kvitka'],
  ['зібратися до школи', ['⏰','🍽️','🎒','🚶'], 'pn_shkola'],
  ['намалювати малюнок', ['📄','✏️','🎨','🖼️'], 'pn_malunok'],
  ['приготувати чай', ['🫖','💧','🔥','🍵'], 'pn_chai'],
  ['перейти дорогу', ['🛑','👀','🚦','🚶'], 'pn_doroha'],
];
function planTasks(v){
  const t = [];
  for (const [what, steps, id] of pick(PLANS, 3)){
    const k = v === 1 ? 0 : rnd(steps.length);
    t.push({prompt:`Щоб ${what}: що робимо ${k === 0 ? 'перш за все' : ORD[k] + ' дією'}?`,
      speak:[[id, 'Щоб ' + what], [k === 0 ? 'q_step1' : 'q_stepn', k === 0 ? 'Що робимо перш за все?' : 'Що робимо далі?']],
      stage: k === 0 ? '' :
        `<span class="rowpics">${steps.slice(0, k).map(e => `<span class="big">${e}</span>`).join('')}</span>`,
      answer: steps[k],
      options: shuffle(steps).map(e => ({v:e, html:`<span class="big">${e}</span>`}))});
  }
  // Помилка в послідовності: що тут стоїть не на своєму місці.
  for (const [what, steps, id] of pick(PLANS, 2)){
    const bad = shuffle(steps.slice());
    const k = bad.findIndex((e, i) => e !== steps[i]);
    t.push({prompt:`Щоб ${what}. Що тут зайве на початку?`,
      speak:[[id, 'Щоб ' + what], ['q_wrongstep','Що тут стоїть не на своєму місці?']],
      stage:`<span class="rowpics">${bad.map(e => `<span class="big">${e}</span>`).join('')}</span>`,
      answer: bad[0] === steps[0] ? bad[k < 0 ? 1 : k] : bad[0],
      options: bad.map(e => ({v:e, html:`<span class="big">${e}</span>`}))});
  }
  return shuffle(t).slice(0, 5);
}

// ---------- Острів Інструкцій: читання картки з малюнками. Це єдина
// частина «Дизайну і технологій», яку планшет справді може перевірити.
const CARDS = [
  ['зробити ліхтарик із паперу', ['📄','✂️','📏','🖇️'], 'cd_likht'],
  ['склеїти хатинку', ['📦','✏️','✂️','🩹'], 'cd_khata'],
  ['зліпити пташку', ['🧱','🤲','🐦','🎨'], 'cd_ptashka'],
];
const TOOLS = [['nozhytsi','ножиці','tl_nozh','✂️','різати'],
  ['liniika','лінійка','tl_lin','📏','міряти й креслити'],
  ['pensel','пензлик','tl_pen','🖌️','малювати фарбами'],
  ['klei','клей','tl_klei','🩹','склеювати'],
  ['olivets','олівець','tl_oliv','✏️','розмічати']];
function cardTasks(v){
  const t = [];
  for (const [what, steps, id] of pick(CARDS, 2))
    t.push({prompt:`Картка: ${what}. З чого почати?`,
      speak:[[id, what], ['q_card','З чого почати?']],
      stage:'', answer: steps[0],
      options: shuffle(steps).map(e => ({v:e, html:`<span class="big">${e}</span>`}))});
  for (const tool of pick(TOOLS, 3))
    t.push({prompt:`Чим ${tool[4]}?`, speak:[['q_tool','Чим це роблять?'], ['tu_'+tool[0], tool[4]]],
      stage:`<span class="word">${tool[4]}</span>`, answer:tool[0],
      options: optsFrom(TOOLS, tool, v===3 ? 4 : 3,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  return shuffle(t).slice(0, 5);
}

// ============ МОРЕ МИСТЕЦТВА ============
// Музична частина — найігровіша в усьому мистецтві, бо вся на слух.
// Звук беремо з того самого WebAudio, що вже є в грі: файлів не треба,
// а дитина порівнює довжину, швидкість і висоту — для 1 класу цього досить.

const TONE = 523;                             // до першої октави
const long_ = [TONE, .34], short_ = [TONE, .14];
const RHY = [
  ['♩ ♩',       [long_, long_]],
  ['♩ ♪♪',      [long_, short_, short_]],
  ['♪♪ ♩',      [short_, short_, long_]],
  ['♪♪ ♪♪',     [short_, short_, short_, short_]],
  ['♩ ♪♪ ♩',    [long_, short_, short_, long_]],
];
function rhythmTasks(v){
  const m = v === 1 ? 2 : v === 2 ? 3 : 4;
  return Array.from({length:5}, () => {
    const r = RHY[rnd(RHY.length)], id = mkPat(r[1]);
    return {prompt:'Послухай плескання. Який запис підходить?',
      speak:[['q_rhythm','Послухай плескання. Який запис підходить?']],
      stage: earBtn(id, 'Плескання'),
      answer:r[0],
      // Нотні значки — у span.big: інакше гра вважає їх підписом і друкує
      // дрібним текстом, а ♩ від ♪ тоді не відрізнити.
      options: optsFrom(RHY, r, m,
        o => ({v:o[0], html:`<span class="big">${o[0]}</span>`}))};
  });
}

// Темп, гучність і регістр — три різні ознаки звуку, і плутають їх
// постійно. Тому завдання питає щоразу лише про одну.
function tempoTasks(v){
  const t = [];
  const beat = (f, d, n_, gap) => Array.from({length:n_}, () => [f, d]);
  for (let i = 0; i < 2; i++){
    const fast = rnd(2) === 1;
    t.push({prompt:'Швидко чи повільно?', speak:[['q_tempo','Швидко чи повільно?']],
      stage: earBtn(mkPat(beat(TONE, fast ? .08 : .3, 5))),
      answer: fast ? 'fast' : 'slow',
      options:[say1('fast','швидко','a_fast'), say1('slow','повільно','a_slow')]});
  }
  for (let i = 0; i < 2; i++){
    const high = rnd(2) === 1, f = high ? TONE * 2 : TONE / 2;
    t.push({prompt:'Високо чи низько?', speak:[['q_pitch','Високо чи низько?']],
      stage: earBtn(mkPat([[f, .3],[f, .3]])),
      answer: high ? 'high' : 'low',
      options:[say1('high','високо','a_high'), say1('low','низько','a_low')]});
  }
  if (v >= 2){
    const up = rnd(2) === 1;
    const seq = up ? [[262,.2],[330,.2],[392,.2],[523,.3]] : [[523,.2],[392,.2],[330,.2],[262,.3]];
    t.push({prompt:'Мелодія йде вгору чи вниз?',
      speak:[['q_dir','Мелодія йде вгору чи вниз?']],
      stage: earBtn(mkPat(seq)), answer: up ? 'up' : 'down',
      options:[say1('up','вгору','a_up'), say1('down','вниз','a_down')]});
  } else {
    t.push({prompt:'Гучно чи тихо?', speak:[['q_loud','Гучно чи тихо?']],
      stage: earBtn(mkPat([[TONE,.3]])), answer:'loud',
      options:[say1('loud','гучно','a_loud'), say1('quiet','тихо','a_quiet')]});
  }
  return shuffle(t).slice(0, 5);
}

// ---------- Острів Інструментів: упізнати інструмент за назвою й за тим,
// як із нього добувають звук. Тембр без записів не передати чесно, тому
// про тембр тут не питають — питають про інструмент.
const INSTR = [
  ['trykutnyk','трикутник','is_tryk','🔺','бʼють паличкою'],
  ['buben','бубон','is_buben','🪘','бʼють рукою'],
  ['baraban','барабан','is_baraban','🥁','бʼють паличками'],
  ['sopilka','сопілка','is_sopilka','🪈','дмухають'],
  ['ksylofon','ксилофон','is_ksylofon','🎹','бʼють молоточками'],
  ['bandura','бандура','is_bandura','🪕','смикають струни'],
  ['skrypka','скрипка','is_skrypka','🎻','водять смичком'],
];
function instrTasks(v){
  const t = [];
  for (const i of pick(INSTR, 3))
    t.push({prompt:`Покажи: ${i[1]}`, speak:[P.show, [i[2], i[1]]], stage:'', answer:i[0],
      options: optsFrom(INSTR, i, v===1 ? 3 : 4,
        o => ({v:o[0], html:`<span class="big">${o[3]}</span>`}))});
  for (const i of pick(INSTR, 2))
    t.push({prompt:'Як добувають звук із цього інструмента?',
      speak:[['q_how','Як добувають звук із цього інструмента?']],
      stage:`<span class="big">${i[3]}</span>`, answer:i[4],
      options: optsFrom(INSTR, i, v===3 ? 4 : 3, o => say1(o[4], o[4], 'ih_'+o[0]))});
  return shuffle(t);
}

// ---------- Острів Нот: нотний стан, скрипковий ключ, ноти першої октави.
// Ноти малюються в SVG — ще один острів без жодного файлу.
const NOTE_Y = {'до':64,'ре':58,'мі':52,'фа':46,'соль':40,'ля':34,'сі':28};
const NOTE_LIST = Object.keys(NOTE_Y);
function staveSvg(name, withKey){
  const y = NOTE_Y[name];
  const lines = [28,37,46,55,64].map(ly =>
    `<line x1="6" y1="${ly}" x2="114" y2="${ly}" stroke="#44464d" stroke-width="1.4"/>`).join('');
  const ledger = y > 64 ? `<line x1="58" y1="${y}" x2="86" y2="${y}" stroke="#44464d" stroke-width="1.4"/>` : '';
  return `<svg class="stave" viewBox="0 0 120 80">${lines}${ledger}`
    + (withKey ? '<text x="10" y="62" font-size="46" fill="#2f6fa8">\u{1D11E}</text>' : '')
    + `<ellipse cx="72" cy="${y}" rx="7" ry="5" fill="#2f6fa8"/>`
    + `<line x1="79" y1="${y}" x2="79" y2="${y-26}" stroke="#2f6fa8" stroke-width="2"/></svg>`;
}
function notesTasks(v){
  const t = [];
  const pool = v === 1 ? ['до','ре','мі'] : v === 2 ? ['до','ре','мі','фа','соль'] : NOTE_LIST;
  for (const nm of pick(pool, 3))
    t.push({prompt:'Яка це нота?', speak:[['q_note','Яка це нота?']],
      stage: staveSvg(nm, true), answer:nm,
      options: optsFrom(pool, nm, v===1 ? 3 : 4, o => say1(o, o, 'no_'+uaId(o)))});
  t.push({prompt:'Скільки ліній у нотному стані?',
    speak:[['q_stave','Скільки ліній у нотному стані?']],
    stage: staveSvg('соль', true), answer:'5', options: numOpts(5, 3, 7, 3)});
  t.push({prompt:'Як називається цей знак на початку нотного стану?',
    speak:[['q_key','Як називається цей знак на початку нотного стану?']],
    stage:'<span class="big">\u{1D11E}</span>', answer:'скрипковий ключ',
    options: shuffle(['скрипковий ключ','нота','пауза'])
      .map(x => say1(x, x, 'ky_' + uaId(x).slice(0, 10)))});
  return shuffle(t).slice(0, 5);
}

// ---------- Острів Орнаменту: витинанка, писанка, народний розпис.
// Візерунки малюються в SVG, тож і цей острів не чекає на картинки.
const ORN = [
  ['vytynanka','витинанка','or_vyt',
   '<g fill="#2f6fa8"><circle cx="50" cy="30" r="9"/><circle cx="26" cy="30" r="6"/>'
   + '<circle cx="74" cy="30" r="6"/><circle cx="50" cy="8" r="6"/><circle cx="50" cy="52" r="6"/></g>'],
  ['pysanka','писанка','or_pys',
   '<g><ellipse cx="50" cy="30" rx="18" ry="24" fill="#f6c453" stroke="#8c5a1d" stroke-width="2"/>'
   + '<path d="M32 30 H68 M50 10 V50" stroke="#8c1d16" stroke-width="2.4"/></g>'],
  ['rozpys','розпис','or_roz',
   '<g fill="none" stroke="#2f6fa8" stroke-width="3"><path d="M10 40 C24 16 38 52 52 28 C66 6 80 44 92 24"/></g>'],
  ['smuzhka','стрічковий візерунок','or_smu',
   '<g fill="#2f6fa8"><rect x="8" y="24" width="12" height="12"/><rect x="28" y="24" width="12" height="12"/>'
   + '<rect x="48" y="24" width="12" height="12"/><rect x="68" y="24" width="12" height="12"/></g>'],
];
const ornSvg = body => `<svg class="orn" viewBox="0 0 100 60">${body}</svg>`;
function ornamentTasks(v){
  const t = [];
  for (const o of pick(ORN, 3))
    t.push({prompt:`Покажи: ${o[1]}`, speak:[P.show, [o[2], o[1]]], stage:'', answer:o[0],
      options: optsFrom(ORN, o, v===1 ? 3 : 4, x => ({v:x[0], html: ornSvg(x[3])}))});
  // Продовж візерунок — те саме, що на Острові Візерунків, але народними
  // мотивами: тема «стрічковий візерунок» у програмі саме про це.
  const MOT = ['🌻','🌺','🍃','🔶','🔷'];
  for (let i = t.length; i < 5; i++){
    const [a, b] = pick(MOT, 2), len = v === 1 ? 4 : 6;
    const row = Array.from({length:len}, (_, k) => k % 2 ? b : a);
    const next = len % 2 ? b : a;
    t.push({prompt:'Що буде далі у візерунку?', speak:[P.pattern],
      stage:`<span class="rowpics">${row.map(e => `<span class="big">${e}</span>`).join('')}`
            + '<span class="big">?</span></span>',
      answer:next,
      options: shuffle([a, b]).map(e => ({v:e, html:`<span class="big">${e}</span>`}))});
  }
  return shuffle(t);
}
