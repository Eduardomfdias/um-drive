# 🚀 UM Drive - File Storage System

Sistema de armazenamento de ficheiros com REST API, NFS, ZFS e Docker.

## 📋 Projeto

- **Disciplina:** Infraestruturas de Tecnologias de Informação (ITI)
- **Universidade do Minho**
- **Ano Letivo:** 2025/2026

## 🎯 Objetivos

Sistema de armazenamento distribuído que evolui de monolítico para distribuído:

- ✅ REST API (FastAPI + Python 3.12)
- ✅ Network File System (NFS)
- ✅ ZFS File System com integridade de dados
- ✅ Docker + Docker Compose
- ✅ Load Balancer (NGINX)
- ✅ Health Checks automáticos

## 🏗️ Arquitetura

```
Cliente → NGINX (:80) → API 1 (:8001) ↘
                      → API 2 (:8002) → NFS → ZFS (192.168.0.2)
                      → API 3 (:8003) ↗
```

## 🚀 Quick Start

### Pré-requisitos

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo apt-get install docker-compose-plugin

# Python 3.12+
python3 --version
```

### Instalação

```bash
# 1. Clonar repositório
git clone <repository-url>
cd um-drive-1

# 2. Configurar NFS (ver documentação)

# 3. Deploy com Docker
docker compose up -d

# 4. Verificar status
docker compose ps
```

## 🌐 Acessos

- **Load Balancer:** http://localhost/
- **Swagger UI:** http://localhost/docs
- **API 1:** http://localhost:8001/docs
- **API 2:** http://localhost:8002/docs
- **API 3:** http://localhost:8003/docs

## 🧪 Testar

```bash
# Upload
echo "test" > test.txt
curl -X POST http://localhost/api/files -F "file=@test.txt"

# Listar
curl http://localhost/api/files

# Download
curl http://localhost/api/files/{file_id} -o downloaded.txt
```

## 📁 Estrutura

```
um-drive-1/
├── Dockerfile              # Imagem Docker da API
├── docker-compose.yml      # Orquestração (3 APIs + nginx)
├── nginx.conf             # Load balancer config
├── requirements.txt       # Dependências Python
├── app/                   # Código fonte
│   ├── main.py           # FastAPI application
│   ├── api/              # Endpoints REST
│   ├── models/           # Data models
│   └── services/         # Business logic
├── docs/                  # Documentação
└── scripts/              # Scripts auxiliares
```

## 📊 Funcionalidades

### REST API (CRUD)
- ✅ POST /api/files - Upload de ficheiros
- ✅ GET /api/files - Listar ficheiros
- ✅ GET /api/files/{id} - Download ficheiro
- ✅ PUT /api/files/{id} - Atualizar metadata
- ✅ DELETE /api/files/{id} - Eliminar ficheiro

### Infraestrutura
- ✅ 3 instâncias da API em containers
- ✅ Load balancing (least connections)
- ✅ Health checks automáticos
- ✅ Persistência via NFS/ZFS
- ✅ Restart automático

## 🔧 Comandos Úteis

```bash
# Ver logs
docker compose logs -f

# Reiniciar serviços
docker compose restart

# Parar tudo
docker compose down

# Rebuild
docker compose up -d --build

# Ver recursos
docker stats
```

## 📅 Timeline

- **Início:** 22/10/2025
- **Docker Implementation:** 28/10/2025
- **Entrega:** 20/12/2025
- **Defesa:** 05-06/01/2026

## 📝 Licença

Projeto académico - Universidade do Minho © 2025
