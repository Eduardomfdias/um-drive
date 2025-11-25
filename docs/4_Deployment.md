# 4. Deployment Guide

## Pré-requisitos

### Software Necessário
- VirtualBox 7.0+
- Ubuntu Server 24.04 LTS (2 VMs)
- 8GB RAM mínimo (4GB por VM)
- 40GB disco por VM

### Conhecimentos
- Bash/Linux básico
- Docker e Docker Compose
- Redes (IP estático, port forwarding)

---

## Setup VM 1: NFS Server (192.168.0.2)

### **1. Configurar IP Estático**
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```
```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      addresses:
        - 192.168.0.2/24
```

Aplicar:
```bash
sudo netplan apply
ip a | grep 192.168.0.2  # Verificar
```

---

### **2. Instalar NFS Server e ZFS**
```bash
# NFS
sudo apt update
sudo apt install -y nfs-kernel-server

# ZFS
sudo apt install -y zfsutils-linux
```

---

### **3. Criar ZFS Pool e Dataset**
```bash
# Listar discos
lsblk

# Criar pool (ajustar /dev/sdX conforme o teu disco)
sudo zpool create tank /dev/sdb

# Criar dataset
sudo zfs create tank/storage

# Configurar ponto de montagem
sudo zfs set mountpoint=/mnt/nfs_share tank/storage

# Otimizações
sudo zfs set compression=lz4 tank/storage
sudo zfs set atime=off tank/storage

# Verificar
zfs list
```

---

### **4. Configurar Exportação NFS**
```bash
sudo nano /etc/exports
```

Adicionar:
```
/mnt/nfs_share 192.168.0.3(rw,sync,no_subtree_check,no_root_squash)
```

Aplicar:
```bash
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server

# Verificar
showmount -e localhost
```

---

## Setup VM 2: UM Drive Server (192.168.0.3)

### **1. Configurar IP Estático**
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```
```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      addresses:
        - 192.168.0.3/24
```

Aplicar:
```bash
sudo netplan apply
ip a | grep 192.168.0.3  # Verificar
```

---

### **2. Instalar Docker e Docker Compose**
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose
sudo apt install -y docker-compose

# Verificar
docker --version
docker-compose --version
```

---

### **3. Instalar NFS Client**
```bash
sudo apt install -y nfs-common
```

---

### **4. Criar Ponto de Montagem e Montar NFS**
```bash
sudo mkdir -p /mnt/nfs_share

# Testar mount manual
sudo mount -t nfs 192.168.0.2:/mnt/nfs_share /mnt/nfs_share

# Verificar
df -h | grep nfs_share
ls -la /mnt/nfs_share

# Tornar persistente
sudo nano /etc/fstab
```

Adicionar ao final:
```
192.168.0.2:/mnt/nfs_share /mnt/nfs_share nfs defaults 0 0
```

Testar:
```bash
sudo umount /mnt/nfs_share
sudo mount -a
df -h | grep nfs_share
```

---

### **5. Clonar Projeto (ou criar estrutura)**
```bash
cd ~
mkdir -p um-drive
cd um-drive
```

---

### **6. Criar Ficheiros do Projeto**

**Dockerfile:**
```bash
cat > Dockerfile << 'DOCKER_EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKER_EOF
```

**requirements.txt:**
```bash
cat > requirements.txt << 'REQ_EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
REQ_EOF
```

**prometheus.yml:**
```bash
cat > prometheus.yml << 'PROM_EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'um-drive-api'
    static_configs:
      - targets: ['um-drive-api-1:8000', 'um-drive-api-2:8000', 'um-drive-api-3:8000']
PROM_EOF
```

**docker-compose.yml:**
```bash
cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  um-drive-api-1:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: um-drive-api-1
    volumes:
      - /mnt/nfs_share:/mnt/nfs_share
    environment:
      - STORAGE_PATH=/mnt/nfs_share
      - API_INSTANCE=1
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.um-drive.rule=Host(`localhost`)"
      - "traefik.http.services.um-drive.loadbalancer.server.port=8000"
    networks:
      - um-drive-network
    restart: unless-stopped

  um-drive-api-2:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: um-drive-api-2
    volumes:
      - /mnt/nfs_share:/mnt/nfs_share
    environment:
      - STORAGE_PATH=/mnt/nfs_share
      - API_INSTANCE=2
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.um-drive.rule=Host(`localhost`)"
      - "traefik.http.services.um-drive.loadbalancer.server.port=8000"
    networks:
      - um-drive-network
    restart: unless-stopped

  um-drive-api-3:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: um-drive-api-3
    volumes:
      - /mnt/nfs_share:/mnt/nfs_share
    environment:
      - STORAGE_PATH=/mnt/nfs_share
      - API_INSTANCE=3
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.um-drive.rule=Host(`localhost`)"
      - "traefik.http.services.um-drive.loadbalancer.server.port=8000"
    networks:
      - um-drive-network
    restart: unless-stopped

  traefik:
    image: traefik:v2.10
    container_name: traefik
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8081:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - um-drive-network
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - um-drive-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - um-drive-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - um-drive-network
    restart: unless-stopped

networks:
  um-drive-network:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
COMPOSE_EOF
```

---

### **7. Criar Código FastAPI**
```bash
mkdir -p app
cat > app/main.py << 'APP_EOF'
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import json
import uuid

app = FastAPI(title="UM Drive API")

STORAGE_PATH = os.getenv("STORAGE_PATH", "/mnt/nfs_share")
METADATA_FILE = os.path.join(STORAGE_PATH, "metadata.json")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

@app.get("/")
def root():
    return {"message": "UM Drive API", "instance": os.getenv("API_INSTANCE", "unknown")}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(STORAGE_PATH, file_id)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    metadata = load_metadata()
    metadata[file_id] = {"filename": file.filename, "size": len(content)}
    save_metadata(metadata)
    
    return {"file_id": file_id, "filename": file.filename}

@app.get("/files")
def list_files():
    return load_metadata()

@app.get("/download/{file_id}")
def download_file(file_id: str):
    metadata = load_metadata()
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = os.path.join(STORAGE_PATH, file_id)
    return FileResponse(file_path, filename=metadata[file_id]["filename"])

@app.delete("/delete/{file_id}")
def delete_file(file_id: str):
    metadata = load_metadata()
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = os.path.join(STORAGE_PATH, file_id)
    os.remove(file_path)
    del metadata[file_id]
    save_metadata(metadata)
    
    return {"message": "File deleted"}
APP_EOF
```

---

### **8. Deploy**
```bash
# Build e start
docker-compose up -d

# Verificar
docker ps
docker logs um-drive-api-1
```

---

## Port Forwarding (VirtualBox)

**VM: UM Drive**  
Settings → Network → Adapter 1 (NAT) → Port Forwarding:

| Nome | Host Port | Guest Port |
|------|-----------|------------|
| API | 80 | 80 |
| Grafana | 3000 | 3000 |
| cAdvisor | 8080 | 8080 |
| Traefik-Dashboard | 8081 | 8081 |
| Prometheus | 9090 | 9090 |

---

## Validação
```bash
# API
curl http://localhost:80

# Traefik Dashboard
# Browser: http://localhost:8081

# Grafana
# Browser: http://localhost:3000 (admin/admin)

# Upload teste
curl -X POST -F "file=@test.txt" http://localhost:80/upload

# Listar ficheiros
curl http://localhost:80/files
```
