# Changelog

## [2.1.0-production-ready] - 2025-12-22

### Added
- **SQLite** para metadados (substitui JSON)
  - Transações ACID para integridade de dados
  - Write-Ahead Logging (WAL) para concorrência
  - Queries indexadas e performance otimizada
- **4 novos alertas** no Prometheus:
  - APIHighLatency (latência > 1s)
  - APIHighErrorRate (> 5% erros 5xx)
  - NoHealthyReplicas (< 2 APIs healthy)
  - DiskSpaceNFS (storage > 80%)
- Total de **7 alertas** configurados
- Fixture `clean_db` para isolamento entre testes

### Changed
- Metadados: JSON → SQLite (`/mnt/nfs_share/metadata.db`)
- Melhoria na integridade e consistência dos dados
- File locking nativo da BD (substitui fcntl manual)

### Technical Improvements
- Base de dados relacional com suporte ACID
- Timeout de 30s para operações concorrentes
- Prepared statements contra SQL injection
- Alerting abrangente (containers + API + storage)
- 21/21 testes unitários a passar

---

## [2.0.0-monitoring] - 2025-12-02

### Added
- Stack de monitorização completa (cAdvisor + Prometheus + Grafana)
- AlertManager com sistema de alertas
- 3 regras de alerta: HighCPUUsage, HighMemoryUsage, ContainerDown
- Dashboard Grafana funcional com métricas em tempo real
- Documentação técnica completa em /docs/
  - 1_Introducao.md
  - 2_Evolucao_Infraestrutura.md
  - 3_Arquitectura_Tecnica.md
  - 4_Deployment.md
  - 5_Monitorizacao.md
  - 6_Testes.md

### Changed
- NGINX → Traefik v2.10 (load balancer dinâmico com service discovery)
- Arquitetura de monitorização: métricas centralizadas e observabilidade completa

### Infrastructure
- cAdvisor (8080): Coleta métricas de containers
- Prometheus (9090): Time-series database com alerting
- Grafana (3000): Dashboards e visualização
- AlertManager (9093): Gestão de alertas
- Traefik (80, 8081): Load balancing + dashboard

### Technical Stack
- Container runtime: Docker + Docker Compose
- Load balancer: Traefik v2.10 (dynamic service discovery)
- Monitoring: cAdvisor + Prometheus + Grafana + AlertManager
- Storage: NFS + ZFS (192.168.0.2)
- API: FastAPI (3 réplicas em 192.168.0.3)

---

## [1.0.0-docker] - 2025-10-28

### Added
- Docker containerization completa
- Docker Compose com 3 instâncias da API
- NGINX Load Balancer (algoritmo least_conn)
- Health checks automáticos
- Persistência via NFS/ZFS

### Features
- 3 réplicas da API em containers isolados
- Load balancing automático
- Auto-restart em caso de falha

### Changed
- Arquitetura monolítica → distribuída
- Storage local → NFS remoto

---

## [0.1.0] - 2025-10-22

### Added
- REST API inicial (FastAPI)
- Integração NFS básica
- ZFS filesystem configurado
- CRUD operations completas
- Swagger UI documentation