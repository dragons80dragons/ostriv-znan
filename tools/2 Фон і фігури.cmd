@echo off
rem ============================================================
rem  UVAGA: TSEY FAYL MUSYT BUTY CHYSTYY ASCII (CLAUDE.md, rozd. 1).
rem  Ukrainskyy tekst - u _ui_2.txt.
rem ============================================================
call "G:\LOCAL AI AGENTS\00_SHARED\env.cmd"
call "%AI_SHARED%\ui.cmd" title "%~dp0_ui_2.txt"
call "%AI_SHARED%\ui.cmd" show "%~dp0_ui_2.txt"

cd /d "G:\LOCAL AI AGENTS\11_BGREMOVE"
if not exist ".venv\Scripts\python.exe" (
    call "%AI_SHARED%\ui.cmd" show "%AI_SHARED%\msg_novenv.txt"
    pause
    exit /b 9
)

rem  onnxruntime-gpu shukaye cuDNN/cuBLAS DLL u PATH - vony lezhat
rem  u pip-paketakh nvidia-* vseredyni venv. Bez tsogo provayder CUDA
rem  tykho ne zavantazhytsya i rembg pide na CPU (CLAUDE.md, rozd. 4).
set "SP=%CD%\.venv\Lib\site-packages\nvidia"
set "PATH=%SP%\cudnn\bin;%SP%\cublas\bin;%SP%\cuda_runtime\bin;%PATH%"

.venv\Scripts\python.exe "%~dp0draw_shapes.py"
.venv\Scripts\python.exe "%~dp0cut_bg.py" %*
echo.
pause
