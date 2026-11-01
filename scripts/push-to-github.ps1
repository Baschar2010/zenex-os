param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteUrl,
    [string]$Branch = "main",
    [string]$CommitMessage = "Prepare ZENEX source and CI bundle"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git wurde nicht gefunden. Installiere Git for Windows und starte das Skript erneut."
}

if (-not (Test-Path -LiteralPath (Join-Path $repo ".git"))) {
    git init --initial-branch=$Branch
    if ($LASTEXITCODE -ne 0) { throw "git init fehlgeschlagen" }
}

$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0 -and $existingRemote -and $existingRemote -ne $RemoteUrl) {
    throw "Origin zeigt bereits auf '$existingRemote'. Prüfe das Repository, bevor du den Remote änderst."
}
if (-not $existingRemote) {
    git remote add origin $RemoteUrl
    if ($LASTEXITCODE -ne 0) { throw "Origin konnte nicht gesetzt werden" }
}

git add --all
if ($LASTEXITCODE -ne 0) { throw "git add fehlgeschlagen" }

$pending = git status --porcelain
if ($pending) {
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) { throw "git commit fehlgeschlagen" }
}

git push -u origin $Branch
if ($LASTEXITCODE -ne 0) {
    throw "Push fehlgeschlagen. Prüfe GitHub-Remote, Anmeldung und Branch-Berechtigung."
}

Write-Host "ZENEX wurde nach $RemoteUrl (Branch $Branch) gepusht."
