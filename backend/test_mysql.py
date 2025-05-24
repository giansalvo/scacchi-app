import mysql.connector
from mysql.connector import Error


def test_connection(host, user, password, database, port=3306):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        if conn.is_connected():
            print(f"✅ Connesso con successo come '{user}'")

            # Test aggiuntivo: verifica le tabelle disponibili
            # cursor = conn.cursor()
            # cursor.execute("SHOW TABLES")
            # tables = cursor.fetchall()
            # print(f"📊 Tabelle nel database '{database}': {len(tables)}")
            # for table in tables:
            #    print(f"- {table[0]}")

    except Error as e:
        print(f"❌ Errore durante la connessione come '{user}':")
        print(f"Codice errore: {e.errno}")
        print(f"Messaggio: {e.msg}")

        # Gestione specifica per errori comuni
        if e.errno == 1045:
            print(">> Accesso negato: verifica username/password")
        elif e.errno == 2003:
            print(">> Impossibile connettersi al server MySQL")
        elif e.errno == 1049:
            print(f">> Database '{database}' non esistente")

    finally:
        if conn and conn.is_connected():
            conn.close()
            # print(f"🔌 Connessione chiusa per '{user}'\n")


# Test con root
test_connection(
    host='127.0.0.1',
    user='root',
    password='',
    database='scacchi'
)

# Test con utente personalizzato
test_connection(
    host='127.0.0.1',
    user='utente_scacchi',
    password='password',
    database='scacchi'
)

# Extra: verifica con parametri errati (esempio didattico)
test_connection(
    host='127.0.0.1',
    user='utente_inesistente',
    password='wrong',
    database='scacchi'
)
