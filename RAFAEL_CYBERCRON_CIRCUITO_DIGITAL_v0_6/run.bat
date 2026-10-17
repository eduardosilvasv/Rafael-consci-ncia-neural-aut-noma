@echo off
cd /d "%~dp0"
title RAFAEL 0.6 - Teste local com PIN
setlocal
set /p RAFAEL_ACCESS_CODE=Crie um PIN numerico local com pelo menos 8 digitos: 
if "%RAFAEL_ACCESS_CODE%"=="" (echo PIN vazio. & pause & exit /b 1)
if "%RAFAEL_ACCESS_CODE:~7,1%"=="" (echo O PIN precisa ter pelo menos 8 caracteres. & pause & exit /b 1)
set RAFAEL_SESSION_SECRET=%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%
set RAFAEL_COOKIE_SECURE=0
set HOST=127.0.0.1
set PORT=8000
where py >nul 2>nul
if %errorlevel%==0 (set PYTHON=py) else (set PYTHON=python)
%PYTHON% --version
if errorlevel 1 (echo Python nao foi encontrado. Instale Python 3.11 ou superior. & pause & exit /b 1)
start "RAFAEL - Painel" http://127.0.0.1:8000/login
%PYTHON% server.py
pause
