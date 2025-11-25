# 3. Arquitetura Técnica

## Diagrama de Rede
```
┌────────────────────────────────────────────────────────────┐
│                    HOST (VirtualBox)                       │
│                                                            │
│  ┌──────────────────┐         ┌──────────────────┐       │
│  │  VM 1: NFS       │         │  VM 2: UM Drive  │       │
│  │  192.168.0.2     │◄────────┤  192.168.0.3     │       │
│  │                  │  NFS    │                  │       │
│  │  - ZFS Storage   │         │  - 3x FastAPI    │       │
│  │  - NFS Server    │         │  - Traefik       │       │
│  │  /mnt/nfs_share  │         │  - Monitoring    │       │
│  └──────────────────┘         └──────────────────┘       │
│                                                            │
│  Port Forwarding:                                         │
│  - 80 → 192.168.0.3:80 (UM Drive API)                    │
│  - 3000 → 192.168.0.3:3000 (Grafana)                     │
│  - 8080 → 192.168.0.3:8080 (cAdvisor)                    │
│  - 8081 → 192.168.0.3:8081 (Traefik Dashboard)           │
│  - 9090 → 192.168.0.3:9090 (Prometheus)                  │
└────────────────────────────────────────────────────────────┘
```

---

## NFS Server (VM 192.168.0.2)

### **Configuração ZFS**
```bash
# Pool criado
sudo zpool create tank /dev/sdb

# Dataset para storage
sudo zfs create tank/storage

# Ponto de montagem
sudo zfs set mountpoint=/mnt/nfs_share tank/storage

# Propriedades
sudo zfs set compression=lz4 tank/storage
sudo zfs set atime=off tank/storage
```

### **Exportação NFS**
Ficheiro: `/etc/exports`
```
/mnt/nfs_share 192.168.0.3(rw,sync,no_subtree_check,no_root_squash)
```

### **Serviços**
```bash
sudo systemctl enable nfs-kernel-server
sudo systemctl start nfs-kernel-server
sudo exportfs -ra
```

---

## UM Drive Server (VM 192.168.0.3)

### **Mount NFS Client**
Ficheiro: `/etc/fstab`
```
192.168.0.2:/mnt/nfs_share /mnt/nfs_share nfs defaults 0 0
```

Verificação:
```bash
sudo mount -a
df -h | grep nfs_share
```

### **Docker Compose Services**

#### **FastAPI (3 réplicas)**
```yaml
um-drive-api-1/2/3:
  build: .
  volumes:
    - /mnt/nfs_share:/mnt/nfs_share
  environment:
    - STORAGE_PATH=/mnt/nfs_share
    - API_INSTANCE=1/2/3
  labels:
    - "traefik.enable=true"
    - "traefik.http.services.um-drive.loadbalancer.server.port=8000"
```

#### **Traefik**
```yaml
traefik:
  image: traefik:v2.10
  command:
    - "--providers.docker=true"
    - "--entrypoints.web.address=:80"
  ports:
    - "80:80"
    - "8081:8080"  # Dashboard
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
```

#### **Monitorização**
```yaml
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  ports: ["8080:8080"]
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
  privileged: true

prometheus:
  image: prom/prometheus:latest
  ports: ["9090:9090"]
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro

grafana:
  image: grafana/grafana:latest
  ports: ["3000:3000"]
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Fluxo de Dados

### **Upload de Ficheiro**
```
1. Cliente → HTTP POST /upload → Traefik (port 80)
2. Traefik → Round-robin → FastAPI container (1, 2 ou 3)
3. FastAPI → Guarda ficheiro → /mnt/nfs_share (NFS mount)
4. NFS Client → Rede → NFS Server (192.168.0.2)
5. NFS Server → Escreve em ZFS → /mnt/nfs_share
6. FastAPI → Guarda metadados → metadata.json (NFS)
7. FastAPI → Resposta → Cliente (200 OK)
```

### **Download de Ficheiro**
```
1. Cliente → HTTP GET /download/{file_id} → Traefik
2. Traefik → Load balance → FastAPI container
3. FastAPI → Lê metadata.json (NFS)
4. FastAPI → Lê ficheiro (NFS)
5. FastAPI → Stream → Cliente
```

### **Monitorização**
```
1. cAdvisor → Coleta métricas → Todos os containers Docker
2. Prometheus → Scrape (15s) → cAdvisor endpoint
3. Prometheus → Armazena → Time-series DB
4. Grafana → Query → Prometheus API
5. Grafana → Renderiza → Dashboards web
```

---

## Persistência e Recuperação

### **Dados**
- ✅ Ficheiros: NFS share (persistente entre reboots)
- ✅ Metadados: `metadata.json` no NFS
- ✅ Métricas: Prometheus volumes Docker

### **Configuração**
- ✅ NFS mount: `/etc/fstab` (automático no boot)
- ✅ Containers: `restart: unless-stopped`
- ✅ Network: `/etc/netplan/01-netcfg.yaml`

### **Teste de Recuperação**
```bash
# Testar reboot
sudo reboot

# Após reboot, verificar
docker ps               # Containers devem estar UP
df -h | grep nfs       # NFS deve estar montado
curl http://localhost  # API deve responder
```

---

## Rede Interna

### **Docker Network**
```yaml
networks:
  um-drive-network:
    driver: bridge
```

**Containers na mesma rede podem comunicar por nome:**
- `prometheus` → `http://cadvisor:8080/metrics`
- `traefik` → `http://um-drive-api-1:8000`

### **VMs Network**
- **Adapter 1:** NAT (acesso internet)
- **Adapter 2:** Host-only (192.168.0.x)
- NFS comunicação: 192.168.0.2 ↔ 192.168.0.3
