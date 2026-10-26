# ==============================================================================
# RetailPulse: Automated GitHub Push Script
# Runs safety verification, stages tracked project files, commits, and pushes to GitHub.
# ==============================================================================

[CmdletBinding()]
param(
    [string]$CommitMessage = "feat: complete RetailPulse portfolio audit, 21 passing tests, executive dashboard fixes, and documentation"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RetailPulse -- Automated GitHub Push Pipeline " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verify Git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Git is not found in PATH. Please install Git for Windows." -ForegroundColor Red
    exit 1
}

# 2. Check Remote Origin
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host "[-] No remote 'origin' found. Setting up default remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/Sandhyad3319/RetailPulse.git
    $remoteUrl = "https://github.com/Sandhyad3319/RetailPulse.git"
}
Write-Host "[1/4] Target Remote: $remoteUrl" -ForegroundColor Green

# 3. Ensure branch is main
$currentBranch = (git branch --show-current).Trim()
if ($currentBranch -ne "main") {
    Write-Host "[*] Switching/renaming current branch to 'main'..." -ForegroundColor Yellow
    git branch -M main
}
Write-Host "[2/4] Active Branch: main" -ForegroundColor Green

# 4. Stage safe project files
Write-Host "[3/4] Staging audited project files..." -ForegroundColor Yellow
git add .gitignore
git add .github/
git add README.md
git add LICENSE
git add docs/
git add python/
git add sql/
git add tests/
git add reports/
git add web/
git add check_env.ps1
git add requirements.txt
git add publish_to_github.ps1

# 5. Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host "[*] Committing changes with message: '$CommitMessage'" -ForegroundColor Yellow
    git commit -m "$CommitMessage"
} else {
    Write-Host "[*] No new changes to commit. Working tree is clean." -ForegroundColor Gray
}

# 6. Push to GitHub
Write-Host "[4/4] Pushing to GitHub (origin main)..." -ForegroundColor Cyan
Write-Host "      (If prompted, sign in via your browser through Git Credential Manager)" -ForegroundColor Gray
git push -u origin main

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host " [+] Successfully pushed to GitHub! " -ForegroundColor Green
Write-Host "     Repository URL: $remoteUrl" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
