import socket
from threading import Thread, Lock
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import time
import json

# Configurazione
TCP_PORT = 5555
HTTP_PORT = 8080
HOST = "localhost"


class SSERequestHandler(BaseHTTPRequestHandler):
    clients = set()
    lock = Lock()

    def log_message(self, format, *args):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [HTTP] {self.address_string()} - {format % args}")

    def send_sse_headers(self):
        """Invia gli header per la connessione SSE"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def handle_sse(self):
        """Gestione connessione SSE"""
        client_ip = self.client_address[0]
        print(f"[SSE] Nuova connessione da {client_ip}")

        self.send_sse_headers()
        with self.lock:
            self.clients.add(self)

        try:
            # Invia un messaggio di benvenuto immediato
            welcome_msg = json.dumps({
                'timestamp': datetime.now().isoformat(),
                'message': 'Connessione SSE stabilita',
                'source': 'SERVER'
            })
            self.wfile.write(f"data: {welcome_msg}\n\n".encode())
            self.wfile.flush()

            # Mantiene la connessione attiva
            while True:
                time.sleep(1)
        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            with self.lock:
                if self in self.clients:
                    self.clients.remove(self)
            print(f"[SSE] Connessione chiusa con {client_ip}")

    def do_GET(self):
        if self.path == "/stream":
            self.handle_sse()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())


def tcp_server():
    """Server TCP con gestione robusta"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, TCP_PORT))
        s.listen(5)
        print(f"[TCP] Server avviato su {HOST}:{TCP_PORT}")

        while True:
            conn, addr = None, None
            try:
                conn, addr = s.accept()
                conn.settimeout(30.0)
                print(f"[TCP] Connessione da {addr[0]}:{addr[1]}")

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    msg = data.decode('utf-8').strip()
                    print(f"[TCP] Ricevuto: '{msg}'")

                    # Invia ACK al client TCP
                    conn.sendall(f"ACK:{msg}\n".encode('utf-8'))

                    # Prepara il messaggio per SSE
                    event_data = json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'message': msg,
                        'source': 'TCP'
                    })

                    # Invia a tutti i client SSE
                    with SSERequestHandler.lock:
                        for client in list(SSERequestHandler.clients):
                            try:
                                client.wfile.write(f"data: {event_data}\n\n".encode())
                                client.wfile.flush()
                            except:
                                SSERequestHandler.clients.remove(client)

            except socket.timeout:
                print(f"[TCP] Timeout con {addr[0]}:{addr[1]}")
            except Exception as e:
                print(f"[TCP] Errore: {str(e)}")
            finally:
                if conn:
                    conn.close()
                if addr:
                    print(f"[TCP] Chiusa connessione con {addr[0]}:{addr[1]}")


if __name__ == "__main__":
    Thread(target=tcp_server, daemon=True).start()

    server = HTTPServer((HOST, HTTP_PORT), SSERequestHandler)
    print(f"[HTTP] Server avviato su http://{HOST}:{HTTP_PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer arrestato")
        server.server_close()