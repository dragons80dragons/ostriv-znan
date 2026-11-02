// Прохід усіх 54 рівнів без людини — перевірка, що гра взагалі
// проходиться. Досі цей скрипт жив у вікні браузера й помирав разом із
// ним; тепер лежить тут, бо після кожної правки рушія його треба
// запускати знову.
//
// Що саме перевіряється: кожен урок на кожному рівні доходить до
// кінцевого екрана й дає три зірки. Три зірки означають нуль помилок,
// тобто правильна відповідь справді визнається правильною в усіх
// п'ятдесяти чотирьох випадках. Якщо десь зірок менше — завдання
// згенерувало відповідь, якої немає серед варіантів, або навпаки.
//
// Як запустити (сторінка гри в браузері, консоль):
//     fetch('/tools/autoplay.js').then(r => r.text()).then(eval)
//     await autoplay()
//
// Повний прохід — близько 75 секунд. Якщо консоль чи інструмент
// обриває довгі виклики, пускати частинами: `autoplay({only:'math,memo'})`
// або без await, а результат забрати з обіцянки пізніше.
//
// Профіль дитини при цьому не псується: скрипт знімає знімок
// localStorage на початку й повертає його в кінці, а звіт учителю на
// час проходу вимикається — інакше в results.jsonl падає 54 вигаданих
// уроки від імені дитини.
window.autoplay = async function (opts = {}) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const only = opts.only ? String(opts.only).split(',') : null;
  const snapshot = {...localStorage};
  const keepSay = window.say, keepReport = window.report;
  window.say = () => {};                 // 54 уроки озвучення — це пів години
  window.report = () => {};              // і жодного рядка в results.jsonl
  const log = [], broken = [];

  // Обвести букву за дитину: ведемо по тих самих штрихах PEN і тим самим
  // перетворенням, яким гра кладе маску. Так перевіряється не лише те, що
  // рівень проходиться, а й що маска лягає рівно на видиму доріжку: якби
  // вона з'їхала, ідеальне обведення не зарахувалося б.
  function trace(glyph) {
    const ic = document.querySelector('canvas.ink');
    // PEN оголошено через const, а не var: на window його немає, і
    // звертатися можна лише на ім'я — звідси typeof замість window.PEN.
    const strokes = typeof PEN !== 'undefined' ? PEN[glyph] : null;
    if (!ic || !strokes) return false;
    const r = ic.getBoundingClientRect();
    // Дотик потрібен не для лінії, а щоб у showTrace() звелося painted:
    // без нього «Готово» відповідає «спершу обведи пальцем».
    ic.dispatchEvent(new PointerEvent('pointerdown', {
      bubbles: true, pointerId: 1, clientX: r.left + r.width / 2,
      clientY: r.top + r.height / 2}));
    const k = ic.getContext('2d');
    k.save();
    k.setTransform(...penMatrix(ic.width));
    k.lineWidth = 7; k.lineCap = 'round'; k.lineJoin = 'round';
    k.strokeStyle = '#e8684a';
    for (const d of strokes) k.stroke(new Path2D(d));
    k.restore();
    return true;
  }

  // Пам'ять: карти лежать парами за data-id, тож відкриваємо їх по дві.
  // Затримка між парами потрібна, бо гра дає картці домалювати перехід.
  async function memo() {
    const seen = new Set();
    for (const c of document.querySelectorAll('.card')) {
      const id = c.dataset.id;
      if (seen.has(id)) continue;
      seen.add(id);
      const both = [...document.querySelectorAll(`.card[data-id="${CSS.escape(id)}"]`)];
      both[0].click(); await sleep(40);
      both[1].click(); await sleep(140);
    }
  }

  async function step(t) {
    if (t.kind === 'memo') { await memo(); return; }
    if (t.kind === 'trace') {
      if (!trace(t.glyph)) return broken.push(`${L.id}/${lvl}: нічим обвести «${t.glyph}»`);
      document.querySelector('#check').click();
      return;
    }
    const btn = [...document.querySelectorAll('.ans')]
      .find(b => b.dataset.v === String(t.answer));
    if (!btn) return broken.push(
      `${L.id}/${lvl}: відповіді «${t.answer}» немає серед варіантів`);
    btn.click();
  }

  for (const les of LESSONS) {
    if (only && !only.includes(les.id)) continue;
    for (const v of [1, 2, 3]) {
      start(les.id, v);
      await sleep(60);
      // Кроків завжди п'ять, але беремо запас: якщо гра застрягне на
      // завданні, цикл має впертися в межу, а не крутитися вічно.
      for (let guard = 0; guard < 40; guard++) {
        if (document.querySelector('.finish')) break;
        await step(tasks[idx]);
        await sleep(60);
        const nx = document.querySelector('.next');
        if (nx) { nx.click(); await sleep(60); }
      }
      const got = (kid().stars[les.id] || {})[v] || 0;
      log.push({урок: les.id, рівень: v, зірки: got});
      if (got < 3) broken.push(`${les.id}/${v}: ${got} зірки замість трьох`);
    }
  }

  window.say = keepSay; window.report = keepReport;
  localStorage.clear();
  for (const [k, val] of Object.entries(snapshot)) localStorage.setItem(k, val);
  const three = log.filter(r => r.зірки === 3).length;
  console.table(log);
  return {рівнів: log.length, 'на три зірки': three, негаразди: broken};
};
