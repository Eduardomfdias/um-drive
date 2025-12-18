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

```mermaid
flowchart TD
    User[User Browser<br/>localhost:80] --> Traefik[Traefik Load Balancer<br/>Port 80]
    
    Traefik --> API1[FastAPI Replica 1<br/>Container]
    Traefik --> API2[FastAPI Replica 2<br/>Container]
    Traefik --> API3[FastAPI Replica 3<br/>Container]
    
    API1 --> NFS[NFS Shared Storage<br/>ZFS - 192.168.0.2<br/>/mnt/nfs_share]
    API2 --> NFS
    API3 --> NFS
    
    API1 -.->|metrics| Prometheus
    API2 -.->|metrics| Prometheus
    API3 -.->|metrics| Prometheus
    
    cAdvisor[cAdvisor] -.->|container metrics| Prometheus[Prometheus<br/>Port 9090]
    Prometheus --> Grafana[Grafana<br/>Port 3000]
    Prometheus --> AlertManager[AlertManager<br/>Port 9093]
    
    style User fill:#e1f5ff
    style Traefik fill:#ffe1e1
    style API1 fill:#e1ffe1
    style API2 fill:#e1ffe1
    style API3 fill:#e1ffe1
    style NFS fill:#fff4e1
    style Grafana fill:#f0e1ff
    style Prometheus fill:#f0e1ff
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

```mermaid
graph LR
    subgraph VM1[VM 1 - NFS Server<br/>192.168.0.2]
        ZFS[ZFS Pool] --> NFS_Export[NFS Export<br/>/mnt/nfs_share]
    end
    
    subgraph VM2[VM 2 - Application Server<br/>192.168.0.3]
        NFS_Client[NFS Client Mount] --> Docker[Docker Compose]
        Docker --> API_Group[FastAPI Replicas x3]
        Docker --> Traefik_LB[Traefik LB]
        Docker --> Monitor[Monitoring Stack]
    end
    
    NFS_Export -.->|NFS Protocol| NFS_Client
    
    style VM1 fill:#fff4e1
    style VM2 fill:#e1f5ff
```

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

**Curso:** Mestrado em Engenharia e Gestão de Sistemas de Informação  
**UC:** Infraestruturas e Tecnologias de Informação (ITI)