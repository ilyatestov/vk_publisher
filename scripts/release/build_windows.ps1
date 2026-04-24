param(
  [string]$Tag = "dev"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $Root

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --onefile --name vk_publisher-windows src/main.py

$ReleaseDir = Join-Path $Root "dist/release"
New-Item -Path $ReleaseDir -ItemType Directory -Force | Out-Null

Copy-Item "dist/vk_publisher-windows.exe" "$ReleaseDir/"
Copy-Item "README.md" "$ReleaseDir/"
if (Test-Path ".env.example") {
  Copy-Item ".env.example" "$ReleaseDir/.env.example"
}

@"
@echo off
set SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%vk_publisher-windows.exe"
"@ | Set-Content -Path "$ReleaseDir/start.bat" -Encoding ASCII

$Archive = "vk_publisher-$Tag-windows.zip"
if (Test-Path $Archive) {
  Remove-Item $Archive -Force
}
Compress-Archive -Path "$ReleaseDir/*" -DestinationPath $Archive

$Hash = Get-FileHash -Algorithm SHA256 $Archive
"$($Hash.Hash)  $Archive" | Set-Content "$Archive.sha256" -Encoding ASCII

Write-Host "Built: $Archive"
