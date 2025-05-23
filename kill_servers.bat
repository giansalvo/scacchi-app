@echo off
:: Windows
set port=58000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%port%') do taskkill /PID %%a /F
