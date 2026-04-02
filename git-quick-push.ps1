# Git Quick Push Tool
# Usage: .\git-quick-push.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Git Quick Push Tool" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in git repo
$gitDir = git rev-parse --git-dir 2>$null
if (-not $gitDir) {
    Write-Host "[Error] Not a git repository!" -ForegroundColor Red
    exit 1
}

# Show status
Write-Host "[1/5] Checking status..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host $status
} else {
    Write-Host "Working tree clean" -ForegroundColor Green
}
Write-Host ""

# Get commit message
$commitMsg = Read-Host "Enter commit message (press Enter for default 'update')"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "update"
}

# Add files
Write-Host ""
Write-Host "[2/5] Adding files..." -ForegroundColor Yellow
git add -A
Write-Host "Done" -ForegroundColor Green

# Commit
Write-Host ""
Write-Host "[3/5] Committing..." -ForegroundColor Yellow
git commit -m "$commitMsg" | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Committed" -ForegroundColor Green
} else {
    Write-Host "[Info] Nothing to commit" -ForegroundColor Yellow
    exit 0
}

# Push
Write-Host ""
Write-Host "[4/5] Pushing..." -ForegroundColor Yellow
git push origin HEAD 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Pushed" -ForegroundColor Green
} else {
    Write-Host "Setting upstream..." -ForegroundColor Yellow
    git push -u origin HEAD
}

# Done
Write-Host ""
Write-Host "[5/5] Done!" -ForegroundColor Green
$lastCommit = git log -1 --oneline
Write-Host $lastCommit -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
