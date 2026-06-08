#Requires -Version 7
param(
  [string]$TaskName = "ENSITAMPlatform",
  [string]$User = "SYSTEM"
)
$ErrorActionPreference = "Stop"

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $BaseDir "start_windows.ps1"
$PsExe = (Get-Command pwsh).Source

$Action = New-ScheduledTaskAction -Execute $PsExe -Argument "-File `"$Script`""
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId $User -RunLevel Highest -LogonType ServiceAccount
$Settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
Register-ScheduledTask -TaskName $TaskName -InputObject $Task -Force
Write-Host "Tarefa '$TaskName' instalada."
