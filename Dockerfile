# Base image Python
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file necessari
COPY .env .
COPY requirements.txt .
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Esponi la porta
EXPOSE 58000

# Comando di avvio
CMD ["python", "backend/server.py"]