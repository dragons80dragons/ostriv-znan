
// ===== ГОЛОС ДЛЯ КОЖНОЇ ФІШКИ =====
//
// Проблема, яку це закриває. У грі два шари озвучення: ЗАВДАННЯ (що
// спитали) і ФІШКИ (що намальовано). Перший був повний, другий — ні.
// У перетягуванні, «знайди на картині» та складанках дитина тицяла в
// картинку й не чула нічого: say() шматок із порожнім id мовчки пропускає.
// Для шести-семирічного це втрачений сенс завдання — він бачить 🪑 і не
// знає, що це «стілець», а слово якраз і треба почути.
//
// Чому окремим шаром, а не правками в генераторах. Генераторів фішок
// близько тридцяти, і в половині з них назви предмета просто немає: у
// даних лежить лише емодзі (ANIM — [емодзі, група], GROUPS — список
// емодзі). Довелося б розширювати десяток таблиць і не забути жодного
// нового генератора. Натомість тут один хук поверх усіх: після того як
// острів зібрав завдання, фішки без голосу отримують його за тим, ЩО
// намальовано. Новий генератор отримає озвучення сам собою.
//
// Порядок має значення: цей шар мусить іти ПОСЛІДНІМ, після mixDrag,
// mixFind і mixBuild, бо ті підмінюють l.gen і загорнули б хук у себе.

// --- назви картинок, яких у даних гри не було
const EMV = {
  '📄': ['em_papir', 'папір'],         '🍽️': ['em_tarilka', 'тарілка'],
  '⏰': ['em_budylnyk', 'будильник'],  '💧': ['em_kraplia', 'крапля'],
  '🕳️': ['em_yama', 'яма'],           '🫖': ['em_chajnyk', 'чайник'],
  '🔥': ['em_vohon', 'вогонь'],        '🚦': ['em_svitlofor', 'світлофор'],
  '👀': ['em_ochi', 'очі'],            '🛑': ['em_stop', 'знак «стоп»'],
  '🍵': ['em_chashka', 'чашка'],       '🖼️': ['em_kartyna', 'картина'],
  '🚶': ['em_pishokhid', 'пішохід'],   '🌱': ['em_rostok', 'росток'],
  '🪑': ['em_stilets', 'стілець'],     '🥔': ['em_kartoplia', 'картопля'],
  '🛏️': ['em_lizhko', 'ліжко'],       '🥕': ['em_morkva', 'морква'],
  '👖': ['em_shtany', 'штани'],        '🔨': ['em_molotok', 'молоток'],
  '👕': ['em_futbolka', 'футболка'],   '🪚': ['em_pylka', 'пилка'],
  '🧥': ['em_kurtka', 'куртка'],       '🍐': ['em_hrushka', 'грушка'],
  '🚪': ['em_dveri', 'двері'],         '🚂': ['em_potiah', 'потяг'],
  '🪛': ['em_vykrutka', 'викрутка'],   '🥄': ['em_lozhka', 'ложка'],
  '🔌': ['em_rozetka', 'розетка'],     '🧴': ['em_pliashka', 'пляшка'],
  '📗': ['em_knyzhka', 'книжка'],      '🧸': ['em_vedmedyk', 'ведмедик'],
  '💊': ['em_tabletky', 'таблетки'],   '⚽': ['em_miach', "м'яч"],
  '⛰️': ['em_hora', 'гора'],           '🪨': ['em_kamin', 'камінь'],
  '🌸': ['em_kvitka', 'квітка'],       '🪴': ['em_vazon', 'вазон'],
  '🍃': ['em_lystok', 'листок'],       '🌿': ['em_steblo', 'стебло'],
  '🦋': ['em_metelyk', 'метелик'],     '🐶': ['em_pesyk', 'песик'],
  '🐜': ['em_murashka', 'мурашка'],    '🐔': ['em_kurka', 'курка'],
  '🐄': ['em_korova', 'корова'],       '🩴': ['em_kaptsi', 'капці'],
  '🪣': ['em_vidro', 'відро'],         '🔍': ['em_lupa', 'лупа'],
  '📰': ['em_hazeta', 'газета'],       '🧃': ['em_sik', 'сік'],
  '🧣': ['em_sharf', 'шарф'],          '🧦': ['em_shkarpetky', 'шкарпетки'],
  '🔑': ['em_kliuch', 'ключ'],         '🍷': ['em_sklianka', 'склянка'],
  '🫙': ['em_banka', 'банка'],         '🗒️': ['em_bloknot', 'блокнот'],
  '🪆': ['em_lialka', 'лялька'],
};
// Емодзі, які вже мають записане слово (острів Слів), беремо звідти — не
// плодимо другий кліп на те саме.
for (const w of WORDS) if (!EMV[w[1]]) EMV[w[1]] = [w[0], w[2]];
// Решта таблиць гри назву має — зводимо їх до того самого вигляду.
for (const a of [BODY, PLANT, TOOLS, JOBS, SENSE])
  for (const r of a) if (r[3] && !EMV[r[3]]) EMV[r[3]] = [r[2], r[1]];
for (const m of MAT) if (!EMV[m[3]]) EMV[m[3]] = [m[2], m[1]];
for (const b of BIN) if (!EMV[b[0]]) EMV[b[0]] = ['bn_' + uaId(b[1]), b[1]];

// --- намальовані картинки без емодзі в розмітці
const IMGV = {
  we_jacket:   ['em_kurtka', 'куртка'],
  we_panama:   ['em_panamka', 'панамка'],
  we_scarf:    ['em_sharf', 'шарф'],
  we_umbrella: ['em_parasolka', 'парасолька'],
};
// Фігури: f_<форма>_<колір>.png. Колір не промовляємо — завдання про форму.
const FIGV = {};
for (const f of FIG) FIGV[f[0]] = [f[2], f[1]];
FIGV.rect = FIGV.rect || ['sh_rect', 'прямокутник'];

// --- слова з речень, яких не було серед записаних
const WSV = {};
for (const [id, w] of [['ws_vysoko', 'високо'], ['ws_harna', 'гарна'],
  ['ws_zoshyt', 'зошит'], ['ws_kanikuly', 'канікули'], ['ws_knyzhku', 'книжку'],
  ['ws_letyt', 'летить'], ['ws_mij', 'мій'], ['ws_peche', 'пече'],
  ['ws_pyrih', 'пиріг'], ['ws_spyt', 'спить'], ['ws_tam', 'там'],
  ['ws_chytaie', 'читає'], ['ws_murchyk', 'мурчик']]) WSV[w] = [id, w];
// Слова, які вже звучать в інших островах.
for (const [w, id] of [['кіт', 'w_kit'], ['мама', 'wd_mama'], ['тато', 'wd_tato'],
  ['квітка', 'w_kvitka'], ['пташка', 's_ptashka'], ['хто', 's_khto'],
  ['де', 's_de'], ['яка', 's_yaka'], ['ура', 's_ura']]) WSV[w] = [id, w];

const PUNCTV = {'.': ['pq_dot', 'крапка'], '?': ['pq_quest', 'знак питання'],
                '!': ['pq_excl', 'знак оклику']};

// --- числа словами. Було тільки до дванадцяти (NUM), а острови дають до ста.
const N_ONES = ['', 'один', 'два', 'три', 'чотири', "п'ять", 'шість', 'сім',
                'вісім', "дев'ять"];
const N_TEENS = {11: 'одинадцять', 12: 'дванадцять', 13: 'тринадцять',
  14: 'чотирнадцять', 15: "п'ятнадцять", 16: 'шістнадцять', 17: 'сімнадцять',
  18: 'вісімнадцять', 19: "дев'ятнадцять"};
const N_TENS = {10: 'десять', 20: 'двадцять', 30: 'тридцять', 40: 'сорок',
  50: "п'ятдесят", 60: 'шістдесят', 70: 'сімдесят', 80: 'вісімдесят',
  90: "дев'яносто", 100: 'сто'};
function numWord(n){
  if (n === 0) return 'нуль';
  if (n === 110) return 'сто десять';
  if (N_TEENS[n]) return N_TEENS[n];
  if (N_TENS[n]) return N_TENS[n];
  if (n < 10) return N_ONES[n];
  const t = Math.floor(n / 10) * 10, o = n % 10;
  return o ? N_TENS[t] + ' ' + N_ONES[o] : N_TENS[t];
}

// --- текст усередині розмітки фішки. Без DOM не обійтися: html буває
// <span class="big">🪑</span>, <img …>, <svg…> або просто «МА».
const chipBox = document.createElement('div');
function chipText(html){
  chipBox.innerHTML = String(html);
  return (chipBox.textContent || '').trim();
}

// --- головне: що озвучити для цієї фішки. null — не озвучувати.
function chipVoice(html){
  const h = String(html);
  // 1. намальована картинка
  const m = h.match(/img\/([a-z0-9_]+)\.png/);
  if (m){
    const id = m[1];
    if (IMGV[id]) return IMGV[id];
    const f = id.match(/^f_([a-z]+)_/);
    if (f && FIGV[f[1]]) return FIGV[f[1]];
    if (BY_ID[id]) return [id, BY_ID[id][2]];        // картинка слова: w_kit
  }
  // 2. емодзі — або з data-e (підміна для картинки), або просто в тексті
  const de = h.match(/data-e="([^"]+)"/);
  const body = de ? de[1] : chipText(h);
  if (!body) return null;
  if (EMV[body]) return EMV[body];
  // 3. число
  if (/^\d{1,3}$/.test(body)){
    const n = +body;
    return n <= 110 ? ['n' + n, numWord(n)] : null;
  }
  // 4. склад (дві великі літери): МА -> sy_ma
  if (/^[А-ЯІЇЄҐ]{2}$/.test(body)) return ['sy_' + uaId(body), body];
  // 5. окрема літера — промовляємо НАЗВУ літери, як в абетці
  if (/^[а-яіїєґьА-ЯІЇЄҐЬ]$/.test(body)){
    const low = body.toLowerCase();
    if (LET_ID[low] === undefined) return null;
    return [body === low ? letVo(low) : letVoUp(low), body];
  }
  // 6. знак у кінці речення
  if (PUNCTV[body]) return PUNCTV[body];
  // 7. слово з речення (кому й велику літеру відкидаємо)
  const w = body.toLowerCase().replace(/[.,!?;:]+$/, '');
  if (WSV[w]) return WSV[w];
  return null;
}

// --- хук: добираємо голос фішкам, які його не мають
function voiceChips(tasks){
  for (const t of (tasks || [])){
    if (!t || typeof t !== 'object') continue;
    for (const key of ['items', 'tiles']){
      for (const it of (t[key] || [])){
        if (!it || it.vo) continue;
        const v = chipVoice(it.html);
        if (v){ it.vo = v[0]; it.tx = v[1]; }
      }
    }
    // Перетягування складає options із фішок ще до того, як вони отримали
    // голос, — перескладаємо, інакше кнопки «послухати» не з'явилися б.
    if (t.kind === 'drag')
      t.options = (t.items || []).concat(t.slots || []).filter(x => x.vo && x.tx);
  }
  return tasks;
}

for (const l of LESSONS){
  const base = l.gen;
  l.gen = function (v){ return voiceChips(base(v)); };
}
window.chipVoice = chipVoice;      // для перевірок
