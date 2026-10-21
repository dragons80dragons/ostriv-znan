@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII.
rem  Ukrainskyy tekst zhyve poryad u _ui_1.txt i drukuyetsya
rem  cherez ui.cmd. Prychynu dyv. u CLAUDE.md agentiv, rozdil 1
rem  ("Koduvannya - golovna pastka zapuskachiv").
rem ============================================================
call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
call "%AI_SHARED%\ui.cmd" title "%~dp0_ui_1.txt"
call "%AI_SHARED%\ui.cmd" show "%~dp0_ui_1.txt"

set "PY=%AI_SHARED%\python\cpython-3.11.15-windows-x86_64-none\python.exe"
if not exist "%PY%" (
    echo Nemae spilnogo Python: "%PY%"
    pause
    exit /b 9
)

"%PY%" "%~dp0gen_images.py" %*
echo.
pause
