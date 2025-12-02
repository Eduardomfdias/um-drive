# UM Drive - Sistema de Armazenamento Distribuído

> Projeto final de **Infraestruturas e Tecnologias de Informação (ITI)**  
> Universidade do Minho | Engenharia de Sistemas de Informação  
> **Data de Entrega:** 20 Dezembro 2025 | **Defesa:** 5-6 Janeiro 2026

---

## 📋 Descrição

O **UM Drive** é um sistema de armazenamento de ficheiros distribuído que disponibiliza uma REST API completa para operações CRUD (Create, Read, Update, Delete). O projeto demonstra a evolução de uma arquitetura monolítica para uma arquitetura distribuída, aplicando conceitos modernos de infraestrutura.

### Funcionalidades
- ✅ Upload/Download de ficheiros via REST API
- ✅ Listagem e eliminação de ficheiros
- ✅ Armazenamento partilhado via NFS + ZFS
- ✅ Load balancing dinâmico (Traefik)
- ✅ Escalabilidade horizontal (3 réplicas FastAPI)
- ✅ Monitorização completa (cAdvisor + Prometheus + Grafana)
- ✅ Sistema de alertas (AlertManager)
- ✅ Persistência de dados
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

┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                         │
└─────────────────────────────────────────────────────────────┘
    cAdvisor → Prometheus → Grafana
    (coleta)   (storage)    (dashboards)
                   ↓
              AlertManager
              (alerting)
```

### Componentes

| Componente | Tecnologia | Porta | Descrição |
|------------|------------|-------|-----------|
| **API** | FastAPI (Python) | 8000 | REST API com CRUD operations |
| **Load Balancer** | Traefik v2.10 | 80, 8081 | Distribuição dinâmica de tráfego + dashboard |
| **Storage** | NFS + ZFS | - | Armazenamento partilhado e resiliente |
| **Monitorização** | cAdvisor | 8080 | Coleta de métricas de containers |
| | Prometheus | 9090 | Time-series database + alerting |
| | Grafana | 3000 | Dashboards e visualização |
| **Alerting** | AlertManager | 9093 | Sistema de gestão de alertas |
| **Containerização** | Docker Compose | - | Orquestração de 8 serviços |

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
sudo zfs set mountpoint=/zfs-storage/umdrive tank/storage
sudo zfs set compression=lz4 tank/storage

# Configurar exportação NFS
echo "/zfs-storage/umdrive 192.168.0.0/24(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
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
echo "192.168.0.2:/zfs-storage/umdrive /mnt/nfs_share nfs defaults 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# Clonar projeto
git clone https://github.com/Eduardomfdias/um-drive.git
cd um-drive

# Deploy
docker-compose up -d
```

### 3. Configurar Port Forwarding (VirtualBox)

**VM: UM Drive → Settings → Network → Port Forwarding:**

| Nome | Host Port | Guest Port |
|------|-----------|------------|
| API | 80 | 80 |
| Traefik-Dashboard | 8081 | 8081 |
| Grafana | 3000 | 3000 |
| Prometheus | 9090 | 9090 |
| cAdvisor | 8080 | 8080 |
| AlertManager | 9093 | 9093 |

---

## 🧪 Testes

### Upload de Ficheiro
```bash
curl -X POST -F "file=@test.txt" http://localhost:80/api/files
```

### Listar Ficheiros
```bash
curl http://localhost:80/api/files
```

### Download de Ficheiro
```bash
curl -O http://localhost:80/api/files/<file_id>
```

### Eliminar Ficheiro
```bash
curl -X DELETE http://localhost:80/api/files/<file_id>
```

### Verificar Load Balancing
```bash
for i in {1..30}; do curl -s http://localhost:80 | jq -r '.instance'; done | sort | uniq -c
```

**Resultado esperado:** distribuição equilibrada entre instâncias 1, 2 e 3

---

## 📊 Monitorização

### Acessos
- **Swagger UI:** http://localhost:80/docs
- **Traefik Dashboard:** http://localhost:8081
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Prometheus Alerts:** http://localhost:9090/alerts
- **cAdvisor:** http://localhost:8080
- **AlertManager:** http://localhost:9093

### Configurar Grafana Dashboard

1. Aceder http://localhost:3000
2. Login: `admin` / `admin`
3. **Connections** → **Data sources** → **Add data source**
4. Selecionar **Prometheus**
5. URL: `http://prometheus:9090`
6. **Save & test**
7. **Dashboards** → **New** → **Import**
8. Dashboard ID: `11600` ou `893`
9. Selecionar Prometheus data source
10. **Import**

### Métricas Monitorizadas

- **CPU Usage** por container
- **Memory Usage** por container
- **Network I/O** (RX/TX)
- **Disk I/O** (reads/writes)
- **Container Uptime**
- **Total Containers Running**

### Alertas Configurados

| Alerta | Condição | Severidade |
|--------|----------|-----------|
| HighCPUUsage | CPU > 80% por 2min | Warning |
| HighMemoryUsage | Memória > 500MB por 2min | Warning |
| ContainerDown | Container não responde por 1min | Critical |

---

## 📁 Estrutura do Projeto
```
um-drive/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── services/
│   │   ├── file_service.py
│   │   └── metadata_service.py
│   └── models/
├── docs/
│   ├── 1_Introducao.md
│   ├── 2_Evolucao_Infraestrutura.md
│   ├── 3_Arquitectura_Tecnica.md
│   ├── 4_Deployment.md
│   ├── 5_Monitorizacao.md
│   ├── 6_Testes.md
│   └── 7_Melhorias_Futuras.md
├── docker-compose.yml             # Orquestração completa (8 serviços)
├── Dockerfile                     # Imagem FastAPI
├── prometheus.yml                 # Config Prometheus
├── prometheus-alerts.yml          # Regras de alerta
├── alertmanager.yml               # Config AlertManager
├── requirements.txt               # Dependências Python
├── CHANGELOG.md                   # Histórico de versões
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
sudo mount -t nfs 192.168.0.2:/zfs-storage/umdrive /mnt/nfs_share -v
df -h | grep nfs_share
```

### Prometheus targets "down"
```bash
docker logs prometheus
curl http://localhost:9090/api/v1/targets
```

### Alertas não aparecem
```bash
# Verificar AlertManager conectado
curl http://localhost:9090/api/v1/alertmanagers

# Ver regras carregadas
curl http://localhost:9090/api/v1/rules
```

### Grafana sem dados
```bash
# Testar conexão Prometheus
docker exec grafana wget -qO- http://prometheus:9090/api/v1/query?query=up

# Verificar data source
# Grafana UI → Connections → Data sources → Prometheus → Test
```

---

## 📚 Documentação Completa

Consultar pasta `/docs/` para documentação técnica detalhada:

1. **1_Introducao.md** - Contexto, objetivos e arquitetura
2. **2_Evolucao_Infraestrutura.md** - Fases de desenvolvimento (0-5)
3. **3_Arquitectura_Tecnica.md** - Diagramas, fluxos, configurações
4. **4_Deployment.md** - Guia passo-a-passo completo
5. **5_Monitorizacao.md** - Stack de observabilidade
6. **6_Testes.md** - Testes funcionais, carga, resiliência
7. **7_Melhorias_Futuras.md** - Roadmap técnico

---

## 🎯 Objetivos Alcançados

### Fases de Desenvolvimento
- ✅ **Fase 0:** Aplicação monolítica funcional
- ✅ **Fase 1:** Containerização com Docker
- ✅ **Fase 2:** Storage partilhado via NFS + ZFS
- ✅ **Fase 3:** Load balancing com Traefik (service discovery)
- ✅ **Fase 5:** Monitorização completa + AlertManager

### Requisitos Funcionais
- ✅ REST API com CRUD completo
- ✅ Upload/download de ficheiros
- ✅ Persistência de dados
- ✅ Metadados em JSON

### Requisitos Não-Funcionais
- ✅ Escalabilidade horizontal (3 réplicas)
- ✅ Alta disponibilidade (restart automático)
- ✅ Observabilidade (métricas + dashboards)
- ✅ Resiliência (recuperação de falhas)
- ✅ Load balancing dinâmico

---

## 🚧 Melhorias Futuras

Consultar `/docs/7_Melhorias_Futuras.md` para detalhes completos.

### Curto Prazo
- [ ] Base de dados para metadados (PostgreSQL)
- [ ] Autenticação JWT
- [ ] TLS/HTTPS com Let's Encrypt

### Médio Prazo
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Testes de carga automatizados
- [ ] Backups automatizados (ZFS snapshots)

### Longo Prazo
- [ ] Migração para Kubernetes
- [ ] Auto-scaling (HPA)
- [ ] Object Storage (MinIO)
- [ ] Logging centralizado (ELK/Loki)

---

## 👥 Equipa

**Grupo de 4 elementos**
- **Curso:** Engenharia de Sistemas de Informação
- **UC:** Infraestruturas e Tecnologias de Informação (ITI)
- **Universidade do Minho**
- **Ano Letivo:** 2025/2026

---

## 🔗 Links Úteis

- **Repositório:** https://github.com/Eduardomfdias/um-drive
- **Documentação Docker:** https://docs.docker.com/
- **Prometheus:** https://prometheus.io/
- **Grafana:** https://grafana.com/
- **Traefik:** https://doc.traefik.io/traefik/

---

## 📄 Infraestruturas de Tecnologias da Informação

Projeto académico - ITI | Grupo 7 | 2025
