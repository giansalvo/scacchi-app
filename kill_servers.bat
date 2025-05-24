@echo off
:: Windows
set port=3306
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%port%') do taskkill /PID %%a /F
