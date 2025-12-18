# 4. Deployment Guide

## Pré-requisitos
- VirtualBox 7.0+
- Ubuntu Server 24.04 LTS (2 VMs)
- 8GB RAM total (4GB por VM)
- 40GB disco por VM

---

## VM 1: NFS Server (192.168.0.2)

### 1. IP Estático
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```
```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      addresses: [192.168.0.2/24]
```
```bash
sudo netplan apply
```

### 2. Instalar Dependências
```bash
sudo apt update
sudo apt install -y nfs-kernel-server zfsutils-linux
```

### 3. Configurar ZFS
```bash
sudo zpool create tank /dev/sdb
sudo zfs create tank/storage
sudo zfs set mountpoint=/mnt/nfs_share tank/storage
sudo zfs set compression=lz4 tank/storage
sudo zfs set atime=off tank/storage
```

### 4. Exportar NFS
```bash
echo '/mnt/nfs_share 192.168.0.3(rw,sync,no_subtree_check,no_root_squash)' | sudo tee -a /etc/exports
sudo exportfs -ra
sudo systemctl enable --now nfs-kernel-server
```

---

## VM 2: UM Drive Server (192.168.0.3)

### 1. IP Estático
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```
```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      addresses: [192.168.0.3/24]
```
```bash
sudo netplan apply
```

### 2. Instalar Docker
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt install -y docker-compose nfs-common
```

### 3. Montar NFS
```bash
sudo mkdir -p /mnt/nfs_share
echo '192.168.0.2:/mnt/nfs_share /mnt/nfs_share nfs defaults 0 0' | sudo tee -a /etc/fstab
sudo mount -a
```

### 4. Deploy Aplicação
```bash
git clone <repo-url> ~/um-drive
cd ~/um-drive
docker-compose up -d
```

**Verificar:**
```bash
docker ps
curl http://localhost/
```

---

## Port Forwarding (VirtualBox)

VM2 → Settings → Network → Adapter 1 (NAT) → Port Forwarding:

| Serviço | Host | Guest |
|---------|------|-------|
| API | 80 | 80 |
| Grafana | 3000 | 3000 |
| Prometheus | 9090 | 9090 |
| Traefik | 8081 | 8081 |
| cAdvisor | 8080 | 8080 |

---

## Validação

```bash
# API funcional
curl http://localhost/

# Upload teste
curl -X POST -F "file=@test.txt" http://localhost/api/files

# Listar ficheiros
curl http://localhost/api/files

# Grafana
# Browser: http://localhost:3000 (admin/admin)
```

---

## Scripts Auxiliares

Ver pasta `/scripts`:
- `setup-nfs-server.sh` - Automatiza setup VM1
- `setup-nfs-client.sh` - Automatiza setup VM2
- `test-nfs.sh` - Valida conectividade NFS