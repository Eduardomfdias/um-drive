# Scripts de Configuração NFS - UM Drive

## 🚀 Uso Rápido

### 1. No Servidor NFS (VM3)
```bash
./setup-nfs-server.sh
```

### 2. Nos Clientes (VM1 e VM2)
```bash
./setup-nfs-client.sh 192.168.56.12
```

### 3. Testar
```bash
./test-nfs.sh
```

## 📋 Pré-requisitos
- Ubuntu Server 22.04
- 3 VMs em rede: 192.168.56.10, .11, .12
- Acesso sudo
