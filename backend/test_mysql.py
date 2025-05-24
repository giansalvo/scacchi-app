import mysql.connector

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='scacchi',
    port=3306
)
print("✅ Connesso!")