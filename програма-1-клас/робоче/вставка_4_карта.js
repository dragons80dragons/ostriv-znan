// ===== КАРТА ПОВНОГО 1 КЛАСУ: 52 острови, пʼять морів, чотири чверті =====
// Поле `per` — чверть, у якій тема починається за програмою (§6 ОСТРОВИ.md).
// Острів не варто показувати раніше, ніж тема почалася в класі: дитина
// побачить завдання, якого ще не вчили, і вирішить, що гра зламана.
// Тому карта показує чверті до поточної включно, а перемикач стоїть у
// вчительському куті екрана.
LESSONS.length = 0;
LESSONS.push(
  // ---- Море Чисел
  {id:'math', img:'i_math', ico:'🧮', vo:'nm_math', per:1, name:'Острів Лічби', about:'Лічба до 10, додавання і віднімання', gen:mathTasks},
  {id:'compare', img:'i_compare', ico:'⚖️', vo:'nm_compare', per:1, name:'Острів Порівнянь', about:'Де більше, де менше, де порівну', gen:compareTasks},
  {id:'order', img:'i_order', ico:'🔢', vo:'nm_order', per:1, name:'Острів Порядку', about:'Яка картинка перша, яка третя', gen:orderTasks},
  {id:'num', img:'i_num', ico:'➕', vo:'nm_num', per:2, name:'Острів Чисел', about:'Скільки треба додати', gen:numTasks},
  {id:'num20', img:'i_num20', ico:'🔟', vo:'nm_num20', per:2, name:'Острів Двадцяти', about:'Десяток і одиниці, числа 11–20', gen:num20Tasks},
  {id:'money', img:'i_money', ico:'🪙', vo:'nm_money', per:2, name:'Острів Гривні', about:'Порахуй гроші', gen:moneyTasks},
  {id:'time', img:'i_time', ico:'🕒', vo:'nm_time', per:3, name:'Острів Часу', about:'Котра година і коли це буває', gen:timeTasks},
  {id:'measure', img:'i_measure', ico:'📏', vo:'nm_measure', per:3, name:'Острів Мірок', about:'Сантиметр, кілограм, літр', gen:measureTasks},
  {id:'lines', img:'i_lines', ico:'📐', vo:'nm_lines', per:3, name:'Острів Ліній', about:'Пряма, відрізок, ламана, симетрія', gen:linesTasks},
  {id:'num100', img:'i_num100', ico:'💯', vo:'nm_num100', per:4, name:'Острів Сотні', about:'Лічба десятками до ста', gen:num100Tasks},
  {id:'add100', img:'i_add100', ico:'🧾', vo:'nm_add100', per:4, name:'Острів Великих Дій', about:'Додаю й віднімаю в межах 100', gen:add100Tasks},
  {id:'task', img:'i_task', ico:'💡', vo:'nm_task', per:4, name:'Острів Задач', about:'Послухай задачу й розвʼяжи', gen:taskTasks},
  {id:'data', img:'i_data', ico:'📊', vo:'nm_data', per:4, name:'Острів Таблиць', about:'Читаю дані з таблиці', gen:dataTasks},
  // ---- Море Мови
  {id:'sound', img:'i_sound', ico:'👏', vo:'nm_sound', per:1, name:'Острів Звуків', about:'Скільки частин у слові', gen:soundTasks},
  {id:'stress', img:'i_stress', ico:'🥁', vo:'nm_stress', per:1, name:'Острів Наголосу', about:'Який склад вимовляється сильніше', gen:stressTasks},
  {id:'read', img:'i_read', ico:'🔤', vo:'nm_read', per:1, name:'Острів Букв', about:'Перший звук і буква у слові', gen:readTasks},
  {id:'write', img:'i_write', ico:'✏️', vo:'nm_write', per:1, name:'Острів Письма', about:'Обведи пальцем букву й цифру', gen:traceTasks},
  {id:'syll', img:'i_syll', ico:'🔊', vo:'nm_syll', per:2, name:'Острів Читання', about:'Склади і перші слова на слух', gen:syllTasks},
  {id:'sent', img:'i_sent', ico:'❗', vo:'nm_sent', per:2, name:'Острів Речення', about:'Велика літера, крапка, знак питання', gen:sentTasks},
  {id:'abc', img:'i_abc', ico:'🔡', vo:'nm_abc', per:3, name:'Острів Алфавіту', about:'Порядок букв і перенос слова', gen:abcTasks},
  {id:'mean', img:'i_mean', ico:'💬', vo:'nm_mean', per:3, name:'Острів Значень', about:'Близькі й протилежні слова', gen:meanTasks},
  {id:'group', img:'i_group', ico:'🧺', vo:'nm_group', per:3, name:'Острів Груп Слів', about:'Назви одним словом', gen:groupTasks},
  {id:'quest', img:'i_quest', ico:'❓', vo:'nm_quest', per:4, name:'Острів Питань', about:'Хто? що? який? що робить?', gen:qwTasks},
  {id:'text', img:'i_text', ico:'📖', vo:'nm_text', per:4, name:'Острів Тексту', about:'Заголовок, речення, жанр', gen:textTasks},
  {id:'en', img:'i_english', ico:'🗣️', vo:'nm_en', per:1, name:'Острів Англійської', about:'Послухай слово і вибери картинку', gen:enTasks},
  // ---- Море Світу
  {id:'body', img:'i_body', ico:'👁️', vo:'nm_body', per:1, name:'Острів Тіла', about:'Чим я пізнаю світ', gen:bodyTasks},
  {id:'safe', img:'i_safe', ico:'🚦', vo:'nm_safe', per:1, name:'Острів Безпеки', about:'Що небезпечно і що робити', gen:safeTasks},
  {id:'weather', img:'i_weather', ico:'🌦️', vo:'nm_weather', per:1, name:'Острів Погоди', about:'Погода, одяг і пори року', gen:weatherTasks},
  {id:'place', img:'i_place', ico:'📍', vo:'nm_place', per:1, name:'Острів Напрямків', about:'Вгорі, внизу, поруч', gen:placeTasks},
  {id:'jobs', img:'i_jobs', ico:'👷', vo:'nm_jobs', per:2, name:'Острів Професій', about:'Хто що робить', gen:jobsTasks},
  {id:'signs', img:'i_signs', ico:'⛔', vo:'nm_signs', per:2, name:'Острів Знаків', about:'Застережні знаки й сигнали', gen:signsTasks},
  {id:'country', img:'i_country', ico:'🇺🇦', vo:'nm_country', per:3, name:'Острів Країни', about:'Київ, прапор, герб, символи', gen:countryTasks},
  {id:'world', img:'i_world', ico:'🌍', vo:'nm_world', per:3, name:'Острів Природи', about:'Хто де живе і що тут зайве', gen:worldTasks},
  {id:'alive', img:'i_alive', ico:'🌱', vo:'nm_alive', per:3, name:'Острів Живого', about:'Жива й нежива природа, частини рослини', gen:aliveTasks2},
  {id:'fig', img:'i_fig', ico:'🔷', vo:'nm_fig', per:3, name:'Острів Фігур', about:'Фігури й кольори на слух', gen:figTasks},
  {id:'animals', img:'i_animals', ico:'🦋', vo:'nm_animals', per:4, name:'Острів Тварин', about:'Комахи, риби, птахи, звірі', gen:animalsTasks},
  {id:'stuff', img:'i_stuff', ico:'🪵', vo:'nm_stuff', per:4, name:'Острів Матеріалів', about:'З чого це зроблено', gen:stuffTasks},
  {id:'invent', img:'i_invent', ico:'🛞', vo:'nm_invent', per:4, name:'Острів Винаходів', about:'Що полегшило життя людині', gen:inventTasks},
  // ---- Море Уваги
  {id:'memo', img:'i_memo', ico:'🧠', vo:'nm_memo', per:1, name:'Острів Памʼяті', about:'Знайди однакові картинки', gen:memoTasks},
  {id:'logic', img:'i_logic', ico:'🧩', vo:'nm_logic', per:1, name:'Острів Візерунків', about:'Знайди закономірність', gen:logicTasks},
  {id:'shadow', img:'i_shadow', ico:'🌑', vo:'nm_shadow', per:1, name:'Острів Тіней', about:'Упізнай предмет за тінню', gen:shadowTasks},
  {id:'info', img:'i_info', ico:'👂', vo:'nm_info', per:1, name:'Острів Відчуттів', about:'Яка це інформація', gen:infoTasks},
  {id:'ask', img:'i_ask', ico:'🙋', vo:'nm_ask', per:2, name:'Острів Запитань', about:'Яке це запитання і що шукати', gen:askTasks},
  {id:'card', img:'i_card', ico:'🗂️', vo:'nm_card', per:3, name:'Острів Інструкцій', about:'З чого почати і чим це роблять', gen:cardTasks},
  {id:'code', img:'i_code', ico:'🟢', vo:'nm_code', per:4, name:'Острів Шифру', about:'Так і ні: нулем, кольором, жестом', gen:codeTasks},
  {id:'true', img:'i_true', ico:'⚖️', vo:'nm_true', per:4, name:'Острів Правди', about:'Правда це чи вигадка', gen:trueTasks},
  {id:'plan', img:'i_plan', ico:'🪜', vo:'nm_plan', per:4, name:'Острів Кроків', about:'Порядок дій: що спершу', gen:planTasks},
  // ---- Море Мистецтва
  {id:'rhythm', img:'i_rhythm', ico:'🪘', vo:'nm_rhythm', per:2, name:'Острів Ритму', about:'Послухай плескання і повтори', gen:rhythmTasks},
  {id:'tempo', img:'i_tempo', ico:'🎚️', vo:'nm_tempo', per:2, name:'Острів Темпу', about:'Швидко чи повільно, високо чи низько', gen:tempoTasks},
  {id:'instr', img:'i_instr', ico:'🎻', vo:'nm_instr', per:3, name:'Острів Інструментів', about:'Який це інструмент', gen:instrTasks},
  {id:'ornament', img:'i_ornament', ico:'🪆', vo:'nm_ornament', per:3, name:'Острів Орнаменту', about:'Витинанка, писанка, візерунок', gen:ornamentTasks},
  {id:'notes', img:'i_notes', ico:'🎼', vo:'nm_notes', per:3, name:'Острів Нот', about:'Нотний стан і ноти', gen:notesTasks},
);
Object.keys(BY_LES).forEach(k => delete BY_LES[k]);
Object.assign(BY_LES, Object.fromEntries(LESSONS.map(l => [l.id, l])));

SEAS.length = 0;
SEAS.push(
  {id:'snum',  ico:'🔢', vo:'sea_num',  name:'Море Чисел',
   ls:['math','compare','order','num','num20','money','time','measure','lines','num100','add100','task','data']},
  {id:'slang', ico:'🔤', vo:'sea_lang', name:'Море Мови',
   ls:['sound','stress','read','write','syll','sent','abc','mean','group','quest','text','en']},
  {id:'sworld',ico:'🌍', vo:'sea_world',name:'Море Світу',
   ls:['body','safe','weather','place','jobs','signs','country','world','alive','fig','animals','stuff','invent']},
  {id:'smind', ico:'🧠', vo:'sea_mind', name:'Море Уваги',
   ls:['memo','logic','shadow','info','ask','card','code','true','plan']},
  {id:'sart',  ico:'🎵', vo:'sea_art',  name:'Море Мистецтва',
   ls:['rhythm','tempo','instr','ornament','notes']},
);

// ---------- Чверть. Зберігається в профілі дитини, тому в одному класі
// один планшет може стояти і в першокласника, і в того, хто наздоганяє.
// 0 — показати все (так зручно вчителеві й тому, хто грає влітку).
function term(){ const k = kid(); return k && k.term != null ? k.term : 1; }
function setTerm(t){
  const k = kid(); if (!k) return;
  k.term = t; save(); home();
}
const inTerm = l => { const t = term(); return t === 0 || (l.per || 1) <= t; };
