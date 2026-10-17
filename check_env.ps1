# RetailPulse Environment Verification Script
# Run this script in PowerShell to check your environment setup

# Ensure current process PATH includes User and Machine PATH entries
$env:Path = [Environment]::GetEnvironmentVariable("Path","User") + ";" + [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + $env:Path

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " RetailPulse -- Environment and Setup Diagnostic " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Operating System
$os = (Get-CimInstance Win32_OperatingSystem).Caption
Write-Host "[1/6] Operating System: $os" -ForegroundColor Yellow

# 2. Check Python
Write-Host "[2/6] Checking Python installation..." -ForegroundColor Yellow
$pythonInstalled = $false
try {
    $pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $pyVersion = (& python.exe --version 2>&1 | Out-String).Trim()
        if ($pyVersion -match "Python \d+\.\d+") {
            Write-Host "      SUCCESS: $pyVersion found at $($pyCmd.Source)" -ForegroundColor Green
            $pythonInstalled = $true
        } else {
            Write-Host "      WARNING: 'python' command returned: $pyVersion" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "      WARNING: 'python' not found in PATH." -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "      WARNING: Could not execute python command." -ForegroundColor DarkYellow
}

# 3. Check Pip
Write-Host "[3/6] Checking pip package manager..." -ForegroundColor Yellow
$pipCmd = Get-Command pip.exe -ErrorAction SilentlyContinue
if ($pipCmd) {
    $pipVer = (& pip.exe --version 2>&1 | Out-String).Trim()
    Write-Host "      SUCCESS: $pipVer" -ForegroundColor Green
} else {
    Write-Host "      NOTE: pip will be available once Python is installed." -ForegroundColor Gray
}

# 4. Check Git
Write-Host "[4/6] Checking Git..." -ForegroundColor Yellow
$gitCmd = Get-Command git.exe -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitVer = (& git.exe --version 2>&1 | Out-String).Trim()
    Write-Host "      SUCCESS: $gitVer" -ForegroundColor Green
} else {
    Write-Host "      OPTIONAL: Git is not yet in PATH (optional for local data processing, recommended for GitHub portfolio)." -ForegroundColor Gray
}

# 5. Check Dataset Connectivity
Write-Host "[5/6] Checking UCI Machine Learning Repository connectivity..." -ForegroundColor Yellow
$datasetUrl = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
try {
    $req = [System.Net.WebRequest]::Create($datasetUrl)
    $req.Method = "HEAD"
    $req.Timeout = 10000
    $res = $req.GetResponse()
    $status = [int]$res.StatusCode
    $res.Close()
    if ($status -eq 200) {
        Write-Host "      SUCCESS: UCI Online Retail dataset is reachable (HTTP 200 OK)." -ForegroundColor Green
    } else {
        Write-Host "      WARNING: Unexpected response code: $status" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "      WARNING: Could not connect to UCI dataset URL: $($_.Exception.Message)" -ForegroundColor DarkYellow
}

# 6. Check Project Directories
Write-Host "[6/6] Verifying project directories..." -ForegroundColor Yellow
$requiredDirs = @(
    "data\raw",
    "data\processed",
    "python",
    "sql",
    "powerbi",
    "reports\figures",
    "docs",
    "tests"
)
$allDirsExist = $true
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "      [OK] $dir" -ForegroundColor Green
    } else {
        Write-Host "      [MISSING] $dir" -ForegroundColor Red
        $allDirsExist = $false
    }
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Diagnostic Summary Complete " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
