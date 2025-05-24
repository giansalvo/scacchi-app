#!/bin/bash
# set_env.sh - Imposta le variabili d'ambiente con valori di default

# Colori per il output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per esportare le variabili
maybe_export() {
    local var_name=$1
    local default_value=$2
    
    if [ -z "${!var_name}" ]; then
        export $var_name="$default_value"
        echo -e "${GREEN}✔${NC} $var_name=${default_value}"
    else
        echo -e "${YELLOW}⚠${NC} $var_name=${!var_name} (già impostata)"
    fi
}

# Verifica che lo script sia eseguito con bash
if [ -z "$BASH_VERSION" ]; then
    echo -e "${RED}✘ Errore: Lo script deve essere eseguito con bash${NC}"
    exit 1
fi

echo -e "\n${YELLOW}=== Impostazione Variabili d'Ambiente ===${NC}"

# Database
maybe_export "MYSQL_ROOT_PASSWORD" "$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=')"
maybe_export "MYSQL_USER" "app_user"
maybe_export "MYSQL_PASSWORD" "$(openssl rand -base64 16)"
maybe_export "MYSQL_DATABASE" "scacchi_db"
maybe_export "MYSQL_PORT" "3306"

# Applicazione
maybe_export "SERVER_PORT" "58000"
maybe_export "DB_HOST" "db"

# SSL (Render.com)
maybe_export "MYSQL_SSL_CA" "/etc/ssl/certs/ca-certificates.crt"
maybe_export "MYSQL_SSL_MODE" "REQUIRED"

echo -e "\n${YELLOW}=== Configurazione Attuale ===${NC}"
env | grep -E 'MYSQL_|SERVER_PORT|DB_HOST'

echo -e "\n${GREEN}✅ Configurazione completata!${NC}"
echo -e "Per rendere permanenti le variabili:"
echo -e "1. Salva in .env: ${YELLOW}./set_env.sh > .env${NC}"
echo -e "2. Per ambiente shell: ${YELLOW}source .env${NC}"