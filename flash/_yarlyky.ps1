# Робить на робочому столі цього комп'ютера ярлики на гру.
# Запускати на КОЖНОМУ комп'ютері, куди принесли цю папку: іконка в
# ярлику зберігається абсолютним шляхом, тому готовий ярлик, скопійований
# з іншої машини, лишається без картинки. Скрипт кладе іконки в
# %LOCALAPPDATA%\OstrivZnan (шлях без кирилиці) і посилається вже туди.
#
# Офлайн-ярлики — .lnk, а не .url: ярлик .url з адресою file:/// Windows
# відкриває ненадійно, часто просто нічого не стається.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$desk = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell

$iconDir = Join-Path $env:LOCALAPPDATA 'OstrivZnan'
if (-not (Test-Path $iconDir)) { New-Item -ItemType Directory -Path $iconDir | Out-Null }
foreach ($n in 'gra.ico', 'zvit.ico') {
    $s = Join-Path (Join-Path $here 'icons') $n
    if (Test-Path $s) { Copy-Item $s (Join-Path $iconDir $n) -Force }
}

function New-Lnk($name, $target, $workDir, $icon, $note, $hidden) {
    $sc = $ws.CreateShortcut((Join-Path $desk ($name + '.lnk')))
    $sc.TargetPath = $target
    $sc.WorkingDirectory = $workDir
    $sc.Description = $note
    # Згорнуте вікно для ярликів на .cmd: інакше перед грою блимає чорне
    # вікно консолі, і дитина думає, що щось зламалося.
    if ($hidden) { $sc.WindowStyle = 7 }
    if (Test-Path $icon) { $sc.IconLocation = "$icon,0" }
    $sc.Save()
    Write-Host ('  створено: ' + $name)
}

Write-Host ''
Write-Host '  Острів Знань — ярлики на робочому столі'
Write-Host '  ---------------------------------------'

$html = Join-Path $here 'Острів Знань.html'
if (Test-Path $html) {
    New-Lnk 'Острів Знань (без інтернету)' $html $here (Join-Path $iconDir 'gra.ico') `
            'Гра, працює без інтернету'
    $old = Join-Path $desk 'Острів Знань (без інтернету).url'
    if (Test-Path $old) { Remove-Item -LiteralPath $old -Force }
} else {
    Write-Host '  УВАГА: поруч немає «Острів Знань.html» — ярлик не створено.'
}

$teach = Join-Path (Join-Path $here 'teacher') 'Режим вчителя.cmd'
if (Test-Path $teach) {
    New-Lnk 'Острів Знань — режим вчителя' $teach (Split-Path -Parent $teach) `
            (Join-Path $iconDir 'zvit.ico') 'Роздає гру планшетам по Wi-Fi і збирає звіт'
}

# Кіоск — те, що потрібно на планшеті: гра на весь екран, без адресного
# рядка, вкладок і меню. Адресу ярлик у собі не тримає, її читає сам .cmd
# із teacher\_address.txt, тож коли ПК учителя змінить адресу, правити
# треба один рядок, а не ярлик.
$kiosk = Join-Path (Join-Path $here 'teacher') 'Кіоск на планшеті.cmd'
if (Test-Path $kiosk) {
    New-Lnk 'Острів Знань — на весь екран' $kiosk (Split-Path -Parent $kiosk) `
            (Join-Path $iconDir 'gra.ico') `
            'Гра на весь екран із ПК вчителя. Вихід - Alt+F4' $true
}

# Онлайн-посилання: .url, увесь текст латиницею
$url = Join-Path $desk 'Острів Знань (онлайн).url'
$text = "[InternetShortcut]`r`nURL=https://claude.ai/artifact/DS9fsW2AHQGPfV67L7GvCJ`r`nIconFile=" +
        (Join-Path $iconDir 'gra.ico') + "`r`nIconIndex=0`r`n"
[System.IO.File]::WriteAllText($url, $text, [System.Text.Encoding]::ASCII)
Write-Host '  створено: Острів Знань (онлайн)'

Write-Host ''
Write-Host '  Готово. Ярлики на робочому столі.'
Write-Host ''
