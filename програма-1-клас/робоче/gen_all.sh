#!/usr/bin/env bash
# Ланцюг генерації ресурсів для повного 1 класу.
#
# ЩО ТУТ ІДЕ ПАРАЛЕЛЬНО, А ЩО НІ — І ЧОМУ
#
# Відеокарта одна (GTX 1080 Ti, 11 ГБ), і два великі генератори на неї не
# влізуть: SDXL бере близько 8 ГБ, ACE-Step — 9,5 ГБ. Запустити їх разом
# означає або падіння з нестачі памʼяті, або тихий переїзд на процесор,
# після якого годинна робота стає добовою (CLAUDE.md парку, розділ 1).
# Тому голос, картинки й музика йдуть ПО ЧЕРЗІ.
#
# Зате вирізання фону (rembg) — єдиний крок, який цілком пристойно
# рахується на процесорі: 20 с на картинку проти 18 с на відеокарті,
# різниці майже немає. Тому він іде ПАРАЛЕЛЬНО з малюванням картинок і
# ніщо в нього не впирається. Перевірено 9 листопада 2026: onnxruntime
# тут працює без AVX2, попри застереження в CLAUDE.md.
#
# Кожен крок пропускає те, що вже зроблено, тому після вимкнення світла
# скрипт можна просто запустити знову.
set -u
LOG="G:/ostriv-znan/програма-1-клас/робоче/_генерація.log"
say(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

VOICE_PY="G:/LOCAL AI AGENTS/02_VOICE/StyleTTS2-UA/.venv/Scripts/python.exe"
COMFY_PY="G:/LOCAL AI AGENTS/01_IMAGE/ComfyUI/.venv/Scripts/python.exe"
MUSIC_PY="G:/LOCAL AI AGENTS/05_MUSIC/ACE-Step/.venv/Scripts/python.exe"
BG_PY="G:/LOCAL AI AGENTS/11_BGREMOVE/.venv/Scripts/python.exe"
T="G:/ostriv-znan/tools"

say "=== ПОЧАТОК. Відеокарта:"
nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader | tee -a "$LOG"

say "--- 1/3 ГОЛОС (StyleTTS2, відеокарта)"
cd "G:/LOCAL AI AGENTS/02_VOICE/StyleTTS2-UA" \
  && PYTHONIOENCODING=utf-8 "$VOICE_PY" "$T/gen_voice.py" --skip-existing >>"$LOG" 2>&1
say "голос: код виходу $?"

say "--- 2/3 КАРТИНКИ (ComfyUI SDXL, відеокарта) + ВИРІЗАННЯ ФОНУ (rembg, процесор) разом"
# Вирізання запускаємо фоном: воно живиться вже намальованими картинками,
# а нові доганяє другим проходом нижче.
( cd "$T" && PYTHONIOENCODING=utf-8 "$BG_PY" "$T/cut_bg.py" --cpu --skip-existing >>"$LOG" 2>&1 ) &
BGPID=$!
cd "$T" && PYTHONIOENCODING=utf-8 "$COMFY_PY" "$T/gen_images.py" >>"$LOG" 2>&1
say "картинки: код виходу $?"
wait $BGPID
say "фон (перший прохід): завершено"
# Другий прохід — для тих картинок, які домалювалися вже після старту першого.
cd "$T" && PYTHONIOENCODING=utf-8 "$BG_PY" "$T/cut_bg.py" --cpu --skip-existing >>"$LOG" 2>&1
say "фон (другий прохід): код виходу $?"

say "--- 3/3 МУЗИКА (ACE-Step, відеокарта)"
cd "G:/LOCAL AI AGENTS/05_MUSIC/ACE-Step" \
  && PYTHONIOENCODING=utf-8 "$MUSIC_PY" "$T/gen_island_music.py" --skip-existing >>"$LOG" 2>&1
say "музика: код виходу $?"

say "=== ГОТОВО"
ls "G:/ostriv-znan/assets/voice" | wc -l | xargs -I{} echo "кліпів голосу: {}" | tee -a "$LOG"
ls "G:/ostriv-znan/assets/img"   | wc -l | xargs -I{} echo "картинок: {}"     | tee -a "$LOG"
ls "G:/ostriv-znan/assets/music" | wc -l | xargs -I{} echo "мелодій: {}"      | tee -a "$LOG"
