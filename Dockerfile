# Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="AI Agent with Claude Tool Use"

# Variabili ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directory di lavoro
WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice applicazione
COPY *.py .

# Crea directory per dati
RUN mkdir -p /app/data/notes

# Utente non-root per sicurezza
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

# Porta esposta
EXPOSE 8000

# Comando di avvio (CLI interattivo)
CMD ["python", "main.py"]
