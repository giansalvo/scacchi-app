# =============================
# === CLIENT HTTP SIMULATOR ===
# =============================
# client_http.py

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
PORT = os.getenv("SERVER_PORT", 50000)
URL = f"http://localhost:{PORT}/api/move"

moves = [
    ("e2e4", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"),
    ("c7c5", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"),
    ("g1f3", "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2")
]

for move, fen in moves:
    payload = {"move": move, "fen": fen}
    try:
        print(f"[DEBUG] Sending move: {move}")
        response = requests.post(URL, json=payload, headers={"Content-Type": "application/json"})
        print("[DEBUG] Server response:", response.status_code, response.text)
        time.sleep(2)
    except Exception as e:
        print("[ERROR] Failed to send move:", e)