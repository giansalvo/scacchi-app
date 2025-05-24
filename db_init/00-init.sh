#!/bin/bash
# Processa gli SQL sostituendo le variabili
envsubst < /docker-entrypoint-initdb.d/01-permissions.sql > /tmp/01-permissions-processed.sql
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < /tmp/01-permissions-processed.sql