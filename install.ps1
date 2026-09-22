# Selfproof one-line installer for Windows (PowerShell).
#   irm https://raw.githubusercontent.com/renker-industries/selfproof/main/install.ps1 | iex
# Downloads the latest release binary to %LOCALAPPDATA%\Programs\Selfproof and
# adds it to the user PATH. Requires the repository's releases to be reachable
# (public, or authenticated for a private repository).
$ErrorActionPreference = "Stop"

$repo = "renker-industries/selfproof"
$dest = Join-Path $env:LOCALAPPDATA "Programs\Selfproof"
$url  = "https://github.com/$repo/releases/latest/download/selfproof-windows.exe"

New-Item -ItemType Directory -Force -Path $dest | Out-Null
$exe = Join-Path $dest "selfproof.exe"

Write-Host "Downloading selfproof-windows.exe from the latest release..."
try {
    Invoke-WebRequest -Uri $url -OutFile $exe -UseBasicParsing
} catch {
    Write-Error "Download failed. If the repository is private, the release is not public yet."
    exit 1
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$dest*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$dest", "User")
    Write-Host "Added $dest to your PATH (restart the terminal to use 'selfproof')."
}
Write-Host "Installed: $exe"
Write-Host "Run 'selfproof' to open the dashboard."
