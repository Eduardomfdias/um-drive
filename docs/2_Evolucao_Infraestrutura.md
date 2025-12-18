# 2. Evolução da Infraestrutura

## Fases de Desenvolvimento

### **Fase 0: Monolítico (Prova de Conceito)**
- Aplicação FastAPI única
- Armazenamento local (filesystem)
- Operações CRUD básicas
- Validação funcional

**Status:** Completado

---

### **Fase 1: Containerização**
- Migração para Docker
- Criação de Dockerfile para FastAPI
- Isolamento de aplicação
- Docker Compose para orquestração local

**Status:** Completado

**Ficheiros:**
- `Dockerfile`
- `docker-compose.yml`

---

### **Fase 2: Armazenamento Partilhado (NFS)**
- Setup de NFS Server dedicado (VM separada)
- Configuração ZFS para storage resiliente
- Mount NFS em todas as instâncias
- Persistência de dados entre containers

**Componentes:**
- **NFS Server (192.168.0.2):**
  - ZFS pool: `tank`
  - Export: `/mnt/nfs_share`
  - Permissões: `rw,sync,no_subtree_check,no_root_squash`

- **NFS Client (192.168.0.3):**
  - Mount point: `/mnt/nfs_share`
  - Persistente via `/etc/fstab`

**Status:** Completado

---

### **Fase 3: Distribuição e Load Balancing**
- Escalabilidade horizontal: 3 réplicas FastAPI
- Load balancer dinâmico: **Traefik v2.10**
- Service discovery automático
- Health checks integrados

**Justificação Traefik vs NGINX:**
- Auto-discovery de containers (sem configuração manual)
- Dashboard web integrado
- Configuração via labels Docker
- Melhor para ambientes cloud-native

**Status:** Completado

---

### **Fase 4: Observabilidade e Monitorização**
Stack de monitorização completa implementada:

**Componentes:**
1. **cAdvisor (porta 8080)**
   - Coleta métricas de containers (CPU, memória, rede, I/O)
   - Expõe endpoint para Prometheus

2. **Prometheus (porta 9090)**
   - Armazena time-series de métricas
   - Scraping de cAdvisor a cada 15s
   - Queries para análise de dados

3. **Grafana (porta 3000)**
   - Visualização de métricas
   - Dashboards personalizáveis
   - Alerting (configurável)

4. **AlertManager (porta 9093)**
   - Gestão de alertas
   - Notificações configuráveis

5. **Prometheus Instrumentator**
   - Métricas da aplicação FastAPI
   - Request rate, latência, erros
   - Expõe endpoint `/metrics`

**Métricas Monitorizadas:**
- CPU por container
- Memória (usage, limits)
- Network I/O
- Disk I/O
- Uptime dos serviços
- Request rate e latência da API
- HTTP status codes

**Status:** Completado

---

## Resumo da Evolução

| Fase | Descrição | Status |
|------|-----------|--------|
| 0 | Monolítico (PoC) | Completado |
| 1 | Containerização | Completado |
| 2 | NFS Storage | Completado |
| 3 | Load Balancing (Traefik) | Completado |
| 4 | Monitorização | Completado |

---

## Decisões Técnicas Justificadas

### **1. Docker Compose vs Kubernetes**
- **Escolha:** Docker Compose
- **Razão:** Simplicidade, cumprimento de requisitos académicos, prazo limitado

### **2. Traefik vs NGINX**
- **Escolha:** Traefik
- **Razão:** Dynamic service discovery, melhor fit para containers

### **3. NFS vs Object Storage (MinIO/S3)**
- **Escolha:** NFS
- **Razão:** Requisito explícito do projeto, simplicidade de setup

### **4. ZFS vs ext4**
- **Escolha:** ZFS
- **Razão:** Snapshots, compressão, integridade de dados