@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md agentiv, rozd. 1).
rem  Ukrainskyy tekst - u _ui.txt, _nopy.txt i v samomu server.py.
rem
rem  Fayl robochyy i na tsiy mashyni, i na chuzhiy (z fleshky):
rem  spilne seredovyshche pidklyuchaetsya, LYShE yakshcho vono e.
rem ============================================================
chcp 65001 >nul
if exist "G:\LOCAL AI AGENTS\00_SHARED\env.cmd" call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
if defined AI_SHARED if exist "%AI_SHARED%\ui.cmd" call "%AI_SHARED%\ui.cmd" title "%~dp0_ui.txt"

set "PY=%AI_SHARED%\python\cpython-3.11.15-windows-x86_64-none\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" --version >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0_nopy.txt" type "%~dp0_nopy.txt"
    echo.
    pause
    exit /b 9
)

"%PY%" "%~dp0server.py"
echo.
pause
