FROM python:3.12-slim

LABEL maintainer="ITI2025"
LABEL description="UM Drive - File Storage REST API"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar NFS client
RUN apt-get update && apt-get install -y --no-install-recommends \
    nfs-common \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar utilizador não-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ ./app/

# Criar diretório storage
RUN mkdir -p /mnt/nfs-storage && \
    chown -R appuser:appuser /app /mnt/nfs-storage

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]