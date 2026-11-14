$ErrorActionPreference = "Stop"
$ScriptDir  = $PSScriptRoot
$ScriptPath = Join-Path $ScriptDir "transcriber.py"
$TaskName   = "NotasFaladas-Transcriber"
$Pythonw    = Join-Path $ScriptDir "..\whisper-transcriber\venv\Scripts\pythonw.exe"
$Pythonw    = (Resolve-Path $Pythonw).Path

if (-not (Test-Path $Pythonw)) {
    Write-Error "pythonw.exe nao encontrado: $Pythonw"
    exit 1
}

Write-Host "Python: $Pythonw"

# Verifica faster-whisper
$check = & $Pythonw -c "import faster_whisper" 2>&1
if ($LASTEXITCODE -ne 0) {
    $Pip = Join-Path (Split-Path $Pythonw) "pip.exe"
    Write-Host "Instalando faster-whisper..."
    & $Pip install faster-whisper --quiet
}

# Remove tarefa anterior se existir
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Cria tarefa agendada (RepetitionDuration de 9999 dias = pratico infinito)
$action    = New-ScheduledTaskAction -Execute $Pythonw -Argument "`"$ScriptPath`""
$trigger   = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 9999)
$settings  = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 25) -MultipleInstances IgnoreNew -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host ""
Write-Host "Tarefa agendada com sucesso!"
Write-Host "  Nome      : $TaskName"
Write-Host "  Frequencia: a cada 30 minutos (sem janela)"
Write-Host "  Script    : $ScriptPath"
Write-Host ""
Write-Host "Para rodar agora (teste):"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "Para ver o log:"
Write-Host "  Get-Content '$ScriptDir\transcriber.log' -Tail 30"
Write-Host ""
Write-Host "Para remover:"
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
