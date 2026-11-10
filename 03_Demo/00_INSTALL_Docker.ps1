# ============================================================
#  ÉTAPE 0 : installe WSL 2 + Docker Desktop (une seule fois)
#  Clic droit sur PowerShell > "Exécuter en tant qu'administrateur", puis :
#    Set-ExecutionPolicy -Scope Process Bypass -Force
#    & "C:\Users\Fidal\Desktop\CIC\BIG DATA\03_Demo\00_INSTALL_Docker.ps1"
# ============================================================
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Write-Host "Relancez PowerShell EN ADMINISTRATEUR." -ForegroundColor Red; exit 1 }

Write-Host "1/2  Installation de WSL 2..." -ForegroundColor Cyan
wsl --install --no-distribution

Write-Host "2/2  Installation de Docker Desktop..." -ForegroundColor Cyan
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

Write-Host ""
Write-Host "TERMINÉ. Redémarrez le PC maintenant." -ForegroundColor Green
Write-Host "Après le redémarrage : lancez Docker Desktop (acceptez les conditions), attendez 'Engine running',"
Write-Host "puis exécutez 03_Demo\01_RUN_DEMO.ps1 (PowerShell normal, pas besoin d'admin)."
