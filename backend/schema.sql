# =============================
# === DATABASE: schema.sql ===
# =============================
# database/schema.sql

CREATE TABLE IF NOT EXISTS game_state (
    id INT PRIMARY KEY,
    fen TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    move_notation VARCHAR(10) NOT NULL,
    fen TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO game_state (id, fen) VALUES (1, 'startpos')
    ON DUPLICATE KEY UPDATE fen = 'startpos';

-- Crea l'utente
CREATE USER 'utente_scacchi'@'%' IDENTIFIED BY 'password';

-- Concedi tutti i permessi sul database scacchi
GRANT ALL PRIVILEGES ON scacchi.* TO 'utente_scacchi'@'%';

-- Applica i cambiamenti
FLUSH PRIVILEGES;