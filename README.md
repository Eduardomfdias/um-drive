# UM Drive - Sistema de Armazenamento Distribuído

> Projeto final de **Infraestruturas e Tecnologias de Informação (ITI)**  
> Universidade do Minho | Engenharia de Sistemas de Informação  
> **Data de Entrega:** 20 Dezembro 2025 | **Defesa:** 5-6 Janeiro 2026

---

## 📋 Descrição

O **UM Drive** é um sistema de armazenamento de ficheiros distribuído que disponibiliza uma REST API completa para operações CRUD (Create, Read, Update, Delete). O projeto demonstra a evolução de uma arquitetura monolítica para uma arquitetura distribuída, aplicando conceitos modernos de infraestrutura.

### Funcionalidades
- ✅ Upload/Download de ficheiros
- ✅ Listagem e eliminação de ficheiros
- ✅ Armazenamento partilhado via NFS
- ✅ Load balancing dinâmico (Traefik)
- ✅ Escalabilidade horizontal (3 réplicas)
- ✅ Monitorização completa (cAdvisor + Prometheus + Grafana)
- ✅ Persistência de dados (ZFS + NFS)
- ✅ Alta disponibilidade

---

## 🏗️ Arquitetura
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
│  └──────────────────┘         │  - Monitoring    │       │
│                                └──────────────────┘       │
└────────────────────────────────────────────────────────────┘
```

### Componentes

| Componente | Tecnologia | Porta | Descrição |
|------------|------------|-------|-----------|
| **API** | FastAPI (Python) | 8000 | REST API com CRUD operations |
| **Load Balancer** | Traefik v2.10 | 80, 8081 | Distribuição dinâmica de tráfego |
| **Storage** | NFS + ZFS | - | Armazenamento partilhado e resiliente |
| **Monitorização** | cAdvisor | 8080 | Coleta de métricas de containers |
| | Prometheus | 9090 | Time-series database |
| | Grafana | 3000 | Dashboards e visualização |
| **Containerização** | Docker Compose | - | Orquestração de serviços |

---

## 🚀 Quick Start

### Pré-requisitos
- VirtualBox 7.0+
- 2 VMs Ubuntu Server 24.04 LTS
- 8GB RAM total (4GB por VM)
- 40GB disco por VM

### 1. Setup NFS Server (VM 192.168.0.2)
```bash
# Configurar IP estático
sudo nano /etc/netplan/01-netcfg.yaml
# Adicionar: enp0s8 → 192.168.0.2/24
sudo netplan apply

# Instalar NFS e ZFS
sudo apt update
sudo apt install -y nfs-kernel-server zfsutils-linux

# Criar ZFS pool
sudo zpool create tank /dev/sdb
sudo zfs create tank/storage
sudo zfs set mountpoint=/mnt/nfs_share tank/storage
sudo zfs set compression=lz4 tank/storage

# Configurar exportação NFS
echo "/mnt/nfs_share 192.168.0.3(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
```

### 2. Setup UM Drive (VM 192.168.0.3)
```bash
# Configurar IP estático
sudo nano /etc/netplan/01-netcfg.yaml
# Adicionar: enp0s8 → 192.168.0.3/24
sudo netplan apply

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar NFS client
sudo apt install -y nfs-common docker-compose

# Montar NFS
sudo mkdir -p /mnt/nfs_share
echo "192.168.0.2:/mnt/nfs_share /mnt/nfs_share nfs defaults 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# Clonar projeto
git clone <repo-url>
cd um-drive

# Deploy
docker-compose up -d
```

### 3. Configurar Port Forwarding (VirtualBox)

**VM: UM Drive → Settings → Network → Port Forwarding:**

| Nome | Host Port | Guest Port |
|------|-----------|------------|
| API | 80 | 80 |
| Traefik | 8081 | 8081 |
| Grafana | 3000 | 3000 |
| Prometheus | 9090 | 9090 |
| cAdvisor | 8080 | 8080 |

---

## 🧪 Testes

### Upload de Ficheiro
```bash
curl -X POST -F "file=@test.txt" http://localhost:80/upload
```

### Listar Ficheiros
```bash
curl http://localhost:80/files
```

### Download de Ficheiro
```bash
curl -O http://localhost:80/download/<file_id>
```

### Verificar Load Balancing
```bash
for i in {1..30}; do curl -s http://localhost:80 | jq -r '.instance'; done | sort | uniq -c
```

---

## 📊 Monitorização

### Acessos
- **Swagger UI:** http://localhost:80/docs
- **Traefik Dashboard:** http://localhost:8081
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **cAdvisor:** http://localhost:8080

### Configurar Grafana
1. Aceder http://localhost:3000
2. Login: `admin` / `admin`
3. Add Data Source → Prometheus → URL: `http://prometheus:9090`
4. Import Dashboard → ID: `193` (Docker monitoring)

---

## 📁 Estrutura do Projeto
```
um-drive/
├── app/
│   └── main.py              # FastAPI application
├── docs/
│   ├── 1_Introducao.md
│   ├── 2_Evolucao_Infraestrutura.md
│   ├── 3_Arquitectura_Tecnica.md
│   ├── 4_Deployment.md
│   ├── 5_Monitorizacao.md
│   └── 6_Testes.md
├── docker-compose.yml       # Orquestração de serviços
├── Dockerfile               # Imagem FastAPI
├── prometheus.yml           # Config Prometheus
├── requirements.txt         # Dependências Python
└── README.md
```

---

## 🔧 Troubleshooting

### Containers não iniciam
```bash
docker-compose logs
docker ps -a
```

### NFS não monta
```bash
showmount -e 192.168.0.2
sudo mount -t nfs 192.168.0.2:/mnt/nfs_share /mnt/nfs_share -v
```

### Prometheus targets "down"
```bash
docker logs prometheus
curl http://localhost:9090/api/v1/targets
```

---

## 📚 Documentação Completa

Consultar pasta `/docs/` para documentação técnica detalhada:
- Evolução da infraestrutura
- Decisões de arquitetura
- Guia de deployment
- Configuração de monitorização
- Testes realizados

---

## 🎯 Objetivos Alcançados

- ✅ **Fase 0:** Aplicação monolítica funcional
- ✅ **Fase 1:** Containerização com Docker
- ✅ **Fase 2:** Storage partilhado via NFS + ZFS
- ✅ **Fase 3:** Load balancing com Traefik
- ✅ **Fase 5:** Monitorização completa (cAdvisor + Prometheus + Grafana)
- ✅ Persistência de dados e configurações
- ✅ Alta disponibilidade (recuperação automática)
- ✅ Escalabilidade horizontal (3 réplicas)

---

## 🚧 Melhorias Futuras

- [ ] Base de dados para metadados (PostgreSQL)
- [ ] Autenticação/Autorização (JWT/OAuth2)
- [ ] TLS/HTTPS
- [ ] Auto-scaling com Kubernetes
- [ ] Testes de carga automatizados
- [ ] CI/CD pipeline

---

## 👥 Equipa

- Dias (e equipa de 4 elementos)
- **Curso:** Engenharia de Sistemas de Informação
- **UC:** Infraestruturas e Tecnologias de Informação
- **Universidade do Minho**

---

## 📄 Licença

Projeto académico - Universidade do Minho © 2025
