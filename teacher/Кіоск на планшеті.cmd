@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md agentiv, rozd. 1).
rem  Ukrainskyy tekst - u _kiosk.txt, adresa - u _address.txt.
rem
rem  Tsey fayl + _address.txt kopiyuyutsya na planshet. Vin vidkryvae gru
rem  v rezhymi kiosku: bez adresnogo ryadka, vkladok i menyu - dytyna ne
rem  vyyde z gry. Vykhid u vchytelya: Alt+F4.
rem ============================================================
setlocal
set "ADDR="
if exist "%~dp0_address.txt" set /p ADDR=<"%~dp0_address.txt"
if not defined ADDR set "ADDR=http://127.0.0.1:8777/"

set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"

if exist "%EDGE%" (
    start "" "%EDGE%" --kiosk "%ADDR%" --edge-kiosk-type=fullscreen --no-first-run
    exit /b 0
)
if exist "%CHROME%" (
    start "" "%CHROME%" --kiosk "%ADDR%" --no-first-run
    exit /b 0
)
echo Ne znaydeno ani Edge, ani Chrome.
echo Vidkryyte vruchnu: %ADDR%
pause
