@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md, rozd. 1).
rem  Ukrainskyy tekst - u _ui_5.txt.
rem ============================================================
call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
call "%AI_SHARED%\ui.cmd" title "%~dp0_ui_5.txt"
call "%AI_SHARED%\ui.cmd" show "%~dp0_ui_5.txt"

set "PY=%AI_SHARED%\python\cpython-3.11.15-windows-x86_64-none\python.exe"
"%PY%" "%~dp0check_assets.py" %*
echo.
pause
