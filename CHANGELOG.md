# Changelog

## [1.0.0-docker] - 2025-10-28

### Added
- Docker containerization completa
- Docker Compose com 3 instâncias da API
- NGINX Load Balancer (algoritmo least_conn)
- Health checks automáticos em todos os containers
- Scripts de deploy automatizado
- Documentação Docker completa
- .dockerignore para builds otimizados
- README.md com instruções de uso

### Features
- 3 réplicas da API em containers isolados
- Load balancing automático via NGINX
- Persistência de dados via NFS/ZFS
- Health monitoring integrado
- Auto-restart em caso de falha

### Infrastructure
- REST API (FastAPI) containerizada
- NFS client nos containers
- Volume partilhado para storage
- Network isolation entre serviços
- Portas: 80 (nginx), 8001-8003 (APIs)

### Changed
- Arquitetura monolítica → distribuída
- Deployment manual → automatizado
- Storage local → NFS remoto

### Technical Details
- Base image: python:3.12-slim
- Container runtime: Docker 28.5.1
- Orchestration: Docker Compose v2.40.2
- Load balancer: NGINX Alpine
- Health check interval: 30s

## [0.1.0] - 2025-10-22

### Added
- REST API inicial (FastAPI)
- Integração NFS básica
- ZFS filesystem configurado
- CRUD operations completas
- Swagger UI documentation
- Metadata JSON storage
