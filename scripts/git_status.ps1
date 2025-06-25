# Git Status Check Script
cd "C:\Users\AU3009\Claudeworks\projects\wildlife-detector"

Write-Host "=== Git Status ===" -ForegroundColor Cyan
git status

Write-Host "`n=== Current Branch ===" -ForegroundColor Cyan
git branch --show-current

Write-Host "`n=== Remote Info ===" -ForegroundColor Cyan
git remote -v

Write-Host "`n=== Recent Commits ===" -ForegroundColor Cyan
git log --oneline -5
