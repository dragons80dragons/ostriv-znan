@echo off
rem Pidnimaye lancyug generaciyi resursiv gry "Ostriv Znan".
rem Zapuskaetsya zaplanovanym zavdannyam OstrivZnan-GenAssets
rem pry vhodi v systemu i dali shchogodyny.
rem
rem UVAGA: cey fayl musyt' buty CHYSTYM ASCII. Kyrylycya v .cmd lamaye
rem parser cmd.exe (dyv. CLAUDE.md parku, rozdil pro koduvannya).
rem Usya logika - v ostriv_gen_loop.sh, vin same i vyrishuye,
rem chy lyshylosya shcho robyty.
start "" /b "C:\Program Files\Git\bin\bash.exe" -c "/c/Users/User/.claude/ostriv_gen_loop.sh"
