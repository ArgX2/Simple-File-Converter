$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$build = Join-Path $root 'build'
$archive = Join-Path $build 'rhwp-v0.9.0-windows-x86_64.zip'
$target = Join-Path $build 'rhwp'
$expected = '72A0C7122A07C46BD67872688057F99FF60C5240333C72CA8B4C5C5B6884EF6F'
New-Item -ItemType Directory -Force -Path $build | Out-Null
Invoke-WebRequest -Uri 'https://github.com/edwardkim/rhwp/releases/download/v0.9.0/rhwp-v0.9.0-windows-x86_64.zip' -OutFile $archive
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $expected) { throw 'rhwp archive checksum mismatch.' }
Expand-Archive -LiteralPath $archive -DestinationPath $build -Force
if (-not (Test-Path -LiteralPath (Join-Path $target 'rhwp.exe'))) { throw 'rhwp executable missing.' }
Write-Host 'rhwp 0.9.0 is ready.'
