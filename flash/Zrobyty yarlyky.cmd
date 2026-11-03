@echo off
rem ============================================================
rem  TSEY FAYL MUSYT BUTY CHYSTYY ASCII.
rem  Ukrainskyy tekst zhyve v _yarlyky.ps1 (UTF-8 z BOM) ta ChYTATY.txt.
rem  Prychyna: cmd.exe perechytuye batnik po baytovomu zmishchenni i
rem  pislya pershogo bagatobaytnogo symvolu vse ide v smittya.
rem ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_yarlyky.ps1"
pause
