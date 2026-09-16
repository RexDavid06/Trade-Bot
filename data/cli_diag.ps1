param(
    [string]$Instrument = "eurgbp",
    [string]$From = "2025-01-01",
    [string]$To = "2026-01-01",
    [string]$OutDir = "data\temp_range_test"
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Write-Output "=== Running CLI ==="
Write-Output "npx dukascopy-node -i $Instrument -from $From -to $To -t m5 -p bid -f csv -v -vu units -dir '$OutDir'"
$outFile = Join-Path $PSScriptRoot "cli_stdout.txt"
$errFile = Join-Path $PSScriptRoot "cli_stderr.txt"
$p = Start-Process -FilePath "npx.cmd" -ArgumentList @("dukascopy-node","-i",$Instrument,"-from",$From,"-to",$To,"-t","m5","-p","bid","-f","csv","-v","-vu","units","-dir",$OutDir) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $outFile -RedirectStandardError $errFile
Write-Output "ExitCode: $($p.ExitCode)"
Write-Output "=== STDOUT ==="
if (Test-Path $outFile) { Get-Content $outFile }
Write-Output "=== STDERR ==="
if (Test-Path $errFile) { Get-Content $errFile }
Write-Output "=== FILES ==="
if (Test-Path $OutDir) { Get-ChildItem $OutDir | Select-Object Name, Length }