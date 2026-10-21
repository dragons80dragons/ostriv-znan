@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md, rozd. 1).
rem  Ukrainskyy tekst - u _ui_4.txt.
rem ============================================================
call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
call "%AI_SHARED%\ui.cmd" title "%~dp0_ui_4.txt"
call "%AI_SHARED%\ui.cmd" show "%~dp0_ui_4.txt"

cd /d "G:\LOCAL AI AGENTS\05_MUSIC\ACE-Step"
if not exist ".venv\Scripts\python.exe" (
    call "%AI_SHARED%\ui.cmd" show "%AI_SHARED%\msg_novenv.txt"
    pause
    exit /b 9
)

rem  Na Pascal float16 daye NaN-latenty ("Float16 overflow on pre-Ampere
rem  GPU"). Tsey zhe prapor stoyit u yarlyku agenta 05_MUSIC.
set "ACESTEP_DTYPE=float32"

.venv\Scripts\python.exe "%~dp0gen_music.py" %*
echo.
pause
