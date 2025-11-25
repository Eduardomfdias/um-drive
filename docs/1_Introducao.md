# UM Drive - Sistema de Armazenamento Distribuído

## 1. Contexto e Objetivos

O **UM Drive** é um sistema de armazenamento de ficheiros distribuído desenvolvido como projeto final da UC de Infraestruturas e Tecnologias de Informação (ITI) da Universidade do Minho.

### Objetivos principais:
- Implementar um serviço de file storage com REST API
- Evolução de arquitetura monolítica para distribuída
- Aplicar práticas modernas: containerização, NFS, load balancing, monitorização
- Garantir escalabilidade, disponibilidade e observabilidade

---

## 2. Arquitetura Final
```
┌─────────────────────────────────────────────────────────────────┐
│                         UM DRIVE SYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   USER (Browser)     │
                    │   localhost:80       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Traefik (port 80)  │
                    │   Dynamic LB         │
                    └──────────┬───────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  FastAPI #1     │  │  FastAPI #2     │  │  FastAPI #3     │
│  (Container)    │  │  (Container)    │  │  (Container)    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │   NFS SHARED STORAGE │
                    │   ZFS (192.168.0.2)  │
                    │   /mnt/nfs_share     │
                    └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                             │
└─────────────────────────────────────────────────────────────────┘
    cAdvisor → Prometheus → Grafana
    (métricas)  (storage)   (dashboards)
```

---

## 3. Tecnologias Utilizadas

| Componente | Tecnologia | Justificação |
|------------|------------|--------------|
| **API** | FastAPI (Python) | Performance, documentação automática (Swagger) |
| **Containerização** | Docker + Docker Compose | Isolamento, portabilidade, reprodutibilidade |
| **Load Balancer** | Traefik v2.10 | Service discovery automático, dashboard integrado |
| **Storage** | NFS + ZFS | Partilha de ficheiros, snapshots, compressão |
| **Monitorização** | cAdvisor + Prometheus + Grafana | Métricas em tempo real, alerting, visualização |
| **Virtualização** | VirtualBox (Ubuntu 24.04) | Ambiente isolado para desenvolvimento |

---

## 4. Infraestrutura

### **VM 1 - NFS Server (192.168.0.2)**
- ZFS pool para storage
- Exportação NFS de `/mnt/nfs_share`
- Backup e snapshots

### **VM 2 - UM Drive Application (192.168.0.3)**
- 3 réplicas FastAPI (containers)
- Traefik (load balancer)
- Stack de monitorização (cAdvisor, Prometheus, Grafana)
- Cliente NFS (mount em `/mnt/nfs_share`)

---

## 5. Portas e Acessos

| Serviço | Porta | URL |
|---------|-------|-----|
| UM Drive API | 80 | http://localhost:80 |
| Traefik Dashboard | 8081 | http://localhost:8081 |
| Grafana | 3000 | http://localhost:3000 (admin/admin) |
| Prometheus | 9090 | http://localhost:9090 |
| cAdvisor | 8080 | http://localhost:8080 |

---

**Data:** Novembro 2025  
**Curso:** Engenharia de Sistemas de Informação  
**UC:** Infraestruturas e Tecnologias de Informação (ITI)
