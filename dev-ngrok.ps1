# Starts ngrok on port 8000, sets CSRF_TRUSTED_ORIGINS from the tunnel URL, then runs Django.
# First-time ngrok: https://dashboard.ngrok.com/signup then run:
#   ngrok config add-authtoken YOUR_TOKEN
# (or set NGROK_AUTHTOKEN in the environment before running this script.)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
Set-Location $root

$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
    [System.Environment]::GetEnvironmentVariable('Path', 'User')

$ngrok = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrok) {
    Write-Error 'ngrok not found in PATH. Install it (e.g. winget install Ngrok.Ngrok) and open a new terminal.'
}

if ($env:NGROK_AUTHTOKEN) {
    & ngrok config add-authtoken $env:NGROK_AUTHTOKEN 2>$null
}

$existing = Get-NetTCPConnection -LocalPort 4040 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $existing) {
    Start-Process -FilePath 'ngrok' -ArgumentList @('http', '127.0.0.1:8000') -WindowStyle Minimized
    Start-Sleep -Seconds 3
    if (-not (Get-Process ngrok -ErrorAction SilentlyContinue)) {
        Write-Host ''
        Write-Host 'ngrok did not stay running. It needs a free account token. Run once:' -ForegroundColor Yellow
        Write-Host '  ngrok config add-authtoken YOUR_TOKEN' -ForegroundColor White
        Write-Host 'Token: https://dashboard.ngrok.com/get-started/your-authtoken' -ForegroundColor DarkGray
        Write-Host 'Or set NGROK_AUTHTOKEN and run this script again.' -ForegroundColor DarkGray
        exit 1
    }
}

$httpsUrl = $null
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline -and -not $httpsUrl) {
    try {
        $tunnels = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -TimeoutSec 2
        $httpsUrl = ($tunnels.tunnels | Where-Object { $_.proto -eq 'https' } | Select-Object -First 1).public_url
    } catch { }
    if (-not $httpsUrl) { Start-Sleep -Milliseconds 400 }
}

if (-not $httpsUrl) {
    Write-Error 'Could not read ngrok HTTPS URL from http://127.0.0.1:4040/api/tunnels. Run: ngrok config add-authtoken YOUR_TOKEN'
}

$env:CSRF_TRUSTED_ORIGINS = $httpsUrl
Write-Host "Public URL (open on your phone): $httpsUrl" -ForegroundColor Green
Write-Host "Local inspect UI: http://127.0.0.1:4040" -ForegroundColor DarkGray

& "$root\.venv\Scripts\python.exe" "$root\manage.py" runserver 0.0.0.0:8000
