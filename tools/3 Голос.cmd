@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md, rozd. 1).
rem  Ukrainskyy tekst - u _ui_3.txt, imya golosu - v manifest.json
rem  (pole voice.speaker), same tomu, shcho syudy yogo pysaty ne mozhna.
rem ============================================================
call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
call "%AI_SHARED%\ui.cmd" title "%~dp0_ui_3.txt"
call "%AI_SHARED%\ui.cmd" show "%~dp0_ui_3.txt"

cd /d "G:\LOCAL AI AGENTS\02_VOICE\StyleTTS2-UA"
if not exist ".venv\Scripts\python.exe" (
    call "%AI_SHARED%\ui.cmd" show "%AI_SHARED%\msg_novenv.txt"
    pause
    exit /b 9
)

.venv\Scripts\python.exe "%~dp0gen_voice.py" %*
echo.
pause
