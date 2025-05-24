@echo off
set DB_HOST=localhost
set DB_USER=utente_scacchi
set DB_PASSWORD=password
set DB_NAME=scacchi
set DB_PORT=3306
set SERVER_PORT=10000
uvicorn backend.server:app --reload --port 10000