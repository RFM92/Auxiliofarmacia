@echo off
REM ============================================================
REM  Auxilio Farmacia - publicacao no GitHub (Windows)
REM  Rode dentro da pasta do repositorio
REM ============================================================
setlocal
set GITHUB_USER=raphaelmenossi-maker
set GITHUB_REPO=Auxiliofarmacia

echo.
echo 1) Verificando segredos...
if exist .env (
  echo    REMOVENDO .env do rastreamento
  git rm --cached .env 2>nul
)

echo.
echo 2) Commit...
if not exist .git git init -b main
git add -A
git commit -m "feat: Auxilio Farmacia v2026.08.1 - 61 medicamentos, paywall por plano, PIX/cartao" 2>nul

echo.
echo 3) Enviando para o GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/%GITHUB_REPO%.git
git push -u origin main

if errorlevel 1 (
  echo.
  echo  FALHOU. Crie o repositorio vazio em https://github.com/new
  echo  nome: %GITHUB_REPO%  - sem README e sem .gitignore
  echo  e rode este .bat de novo.
  pause
  exit /b 1
)

echo.
echo  OK! Repo: https://github.com/%GITHUB_USER%/%GITHUB_REPO%
echo.
echo  Proximo passo - Cloudflare Pages (frontend):
echo    1) dash.cloudflare.com - Workers ^& Pages - Create
echo    2) Connect to Git - escolha o repositorio
echo    3) Build command: (vazio)
echo    4) Build output directory: site
echo    5) Deploy
echo.
pause
