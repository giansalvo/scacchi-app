# =============================
# === BACKEND: server.py    ===
# =============================
# backend/server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
import uvicorn
import json
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import datetime
import asyncio

# Ottieni il percorso assoluto della directory del progetto
BASE_DIR = Path(__file__).parent.parent


load_dotenv()
SERVER_PORT = int(os.getenv("SERVER_PORT", 50000))

app = FastAPI()
app.mount("/static", StaticFiles(directory="./frontend"), name="static")
#app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione sostituisci con l'URL del frontend
    allow_methods=["*"],
    allow_headers=["*"]
)

# Lista globale per gestire le connessioni attive
connections_lock = asyncio.Lock()
active_connections = []


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "youruser"),
        password=os.getenv("DB_PASSWORD", "yourpassword"),
        database=os.getenv("DB_NAME", "chess"),
        port=int(os.getenv("DB_PORT", 3306))
    )

@app.get("/hello")
async def index():
    return "HELLO!!"


@app.get("/")
async def index():
    file_path = BASE_DIR / "frontend" / "index.html"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content)
    except UnicodeDecodeError:
        # Fallback per file non UTF-8
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return HTMLResponse(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot read index.html: {str(e)}")

@app.get("/api/state")
async def get_state():
    db = get_db()

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT fen FROM game_state WHERE id = 1")
    result = cursor.fetchone()
    return {"fen": result["fen"]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Aggiunta thread-safe alla lista
    async with connections_lock:
        active_connections.append(websocket)

    client_ip = websocket.client.host if websocket.client else "unknown"
    print(f"[CONNECT] Client connected from {client_ip}. Total: {len(active_connections)}")

    try:
        while True:
            message = await websocket.receive_text()
            print(f"[MESSAGE] From {client_ip}: {message[:100]}...")

            try:
                data = json.loads(message)

                # Broadcast thread-safe
                async with connections_lock:
                    for connection in active_connections.copy():  # Usa una copia
                        try:
                            await connection.send_json({
                                "sender": client_ip,
                                "message": data,
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as e:
                            print(f"Broadcast error: {e}")
                            if connection in active_connections:
                                active_connections.remove(connection)

            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format")

    except WebSocketDisconnect:
        print(f"[DISCONNECT] Client {client_ip} disconnected")
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
    finally:
        # Rimozione thread-safe
        async with connections_lock:
            if websocket in active_connections:
                active_connections.remove(websocket)
        await websocket.close()
        print(f"[STATUS] Remaining clients: {len(active_connections)}")

@app.post("/api/move")
async def receive_move(request: Request):
    db = None
    cursor = None
    try:
        print("[DEBUG] Receiving move from client...")
        raw = await request.body()
        print("[DEBUG] Raw body:", raw.decode())

        data = await request.json()
        move = data.get("move")
        fen = data.get("fen")
        print("[DEBUG] Parsed move:", move, "FEN:", fen)

        # Test della connessione al database
        db = get_db()
        cursor = db.cursor()

        # Esegui una query di test per verificare che il database risponda
        cursor.execute("SELECT 1")
        test_result = cursor.fetchone()
        print("[DEBUG] Database connection test:", test_result)

        # Operazioni principali
        cursor.execute("INSERT INTO moves (move_notation, fen) VALUES (%s, %s)", (move, fen))
        cursor.execute("UPDATE game_state SET fen = %s WHERE id = 1", (fen,))
        db.commit()
        print("[DEBUG] Updated database with new move")

        # Invia la mossa a tutti i client WebSocket
        for client in active_connections:
            await client.send_json({"move": move, "fen": fen})
            print("[DEBUG] Broadcasted move to client")

        return {"status": "ok"}

    except mysql.connector.Error as db_error:
        print("[ERROR] Database error:", str(db_error))
        return {"status": "error", "details": "Database operation failed"}

    except json.JSONDecodeError as json_error:
        print("[ERROR] JSON decode error:", str(json_error))
        return {"status": "error", "details": "Invalid JSON format"}

    except Exception as e:
        print("[ERROR] Unexpected error:", str(e))
        return {"status": "error", "details": "Internal server error"}

    finally:
        # Chiudi sempre cursor e connessione
        if cursor is not None:
            cursor.close()
        if db is not None and db.is_connected():
            db.close()
            print("[DEBUG] Database connection closed")

@app.get("/api/health")
async def health_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        return {"database": "ok"}
    except Exception as e:
        print("[ERROR] Database health check failed:", str(e))
        return {"database": "error", "details": str(e)}

if __name__ == "__main__":
    print(f"[INFO] Starting FastAPI app on port ${SERVER_PORT}")
    uvicorn.run("server:app", host="0.0.0.0", port=SERVER_PORT, reload=True, log_level="debug")

# =============================
# === CLIENT TCP: putty_sim ===
# =============================
# Simulazione con invio TCP o via curl HTTP POST

# Esempio curl:
# curl -X POST http://localhost:8000/api/move -H "Content-Type: application/json" -d '{"move": "e2e4", "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"}'