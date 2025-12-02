# Diagrama de Casos de Uso - UM Drive

## Use Case Diagram (UML)
```mermaid
%%{init: {'theme':'base'}}%%
graph LR
    subgraph System["<b>UM Drive System</b>"]
        direction TB
        
        subgraph FileOps["<b>File Operations</b>"]
            UC1((Upload<br/>File))
            UC2((Download<br/>File))
            UC3((List<br/>Files))
            UC4((Delete<br/>File))
            UC5((View<br/>Metadata))
        end
        
        subgraph Monitoring["<b>Monitoring & Admin</b>"]
            UC6((Monitor<br/>System))
            UC7((View<br/>Metrics))
            UC8((Configure<br/>Alerts))
            UC9((View<br/>Logs))
            UC10((Manage<br/>Containers))
        end
    end
    
    User([👤 User/<br/>Client])
    Admin([👨‍💼 System<br/>Admin])
    
    User -.-> UC1
    User -.-> UC2
    User -.-> UC3
    User -.-> UC4
    User -.-> UC5
    
    Admin -.-> UC6
    Admin -.-> UC7
    Admin -.-> UC8
    Admin -.-> UC9
    Admin -.-> UC10
    
    style System fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style FileOps fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Monitoring fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    style User fill:#4caf50,stroke:#2e7d32,stroke-width:2px,color:#fff
    style Admin fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    
    style UC1 fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    style UC2 fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    style UC3 fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    style UC4 fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    style UC5 fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    
    style UC6 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    style UC7 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    style UC8 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    style UC9 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
    style UC10 fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px
```

---

## Diagrama de Arquitetura com Atores
```mermaid
flowchart TB
    subgraph Actors["<b>ATORES</b>"]
        User[("👤<br/><b>User/Client</b><br/>Utilizador Final")]
        Admin[("👨‍💼<br/><b>System Admin</b><br/>Administrador")]
    end
    
    subgraph API["<b>UM DRIVE API</b>"]
        direction LR
        Traefik[<b>Traefik</b><br/>Load Balancer]
        API1[FastAPI<br/>Instance 1]
        API2[FastAPI<br/>Instance 2]
        API3[FastAPI<br/>Instance 3]
    end
    
    subgraph Storage["<b>STORAGE</b>"]
        NFS[("<b>NFS + ZFS</b><br/>Shared Storage<br/>192.168.0.2")]
    end
    
    subgraph Monitoring["<b>MONITORING STACK</b>"]
        direction TB
        cAdvisor[<b>cAdvisor</b><br/>Metrics Collector]
        Prometheus[<b>Prometheus</b><br/>Time-series DB]
        Grafana[<b>Grafana</b><br/>Dashboards]
        AlertMgr[<b>AlertManager</b><br/>Alerting]
    end
    
    User -->|"UC1: Upload File<br/>UC2: Download File<br/>UC3: List Files<br/>UC4: Delete File<br/>UC5: View Metadata"| Traefik
    
    Traefik -->|Round-robin| API1
    Traefik -->|Round-robin| API2
    Traefik -->|Round-robin| API3
    
    API1 <-->|Read/Write| NFS
    API2 <-->|Read/Write| NFS
    API3 <-->|Read/Write| NFS
    
    Admin -->|"UC6: Monitor System<br/>UC7: View Metrics<br/>UC8: Configure Alerts<br/>UC9: View Logs<br/>UC10: Manage Containers"| Monitoring
    
    cAdvisor -->|Scrape| API1
    cAdvisor -->|Scrape| API2
    cAdvisor -->|Scrape| API3
    cAdvisor -->|Metrics| Prometheus
    
    Prometheus -->|Query| Grafana
    Prometheus -->|Alerts| AlertMgr
    
    style Actors fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style API fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style Storage fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    style Monitoring fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    
    style User fill:#66bb6a,stroke:#2e7d32,stroke-width:2px,color:#fff
    style Admin fill:#42a5f5,stroke:#0d47a1,stroke-width:2px,color:#fff
    
    style Traefik fill:#ff9800,stroke:#e65100,stroke-width:2px
    style NFS fill:#03a9f4,stroke:#01579b,stroke-width:2px
```

---

## Casos de Uso Detalhados

### 👤 **User/Client Use Cases**

| ID | Nome | Descrição | Prioridade |
|----|------|-----------|------------|
| UC1 | Upload File | Fazer upload de ficheiros para o sistema | Alta |
| UC2 | Download File | Descarregar ficheiros armazenados | Alta |
| UC3 | List Files | Listar todos os ficheiros disponíveis | Média |
| UC4 | Delete File | Eliminar ficheiros do sistema | Média |
| UC5 | View Metadata | Consultar informações dos ficheiros | Baixa |

### 👨‍💼 **System Admin Use Cases**

| ID | Nome | Descrição | Prioridade |
|----|------|-----------|------------|
| UC6 | Monitor System | Monitorizar saúde do sistema em tempo real | Alta |
| UC7 | View Metrics | Visualizar métricas históricas e dashboards | Alta |
| UC8 | Configure Alerts | Gerir regras de alertas e notificações | Média |
| UC9 | View Logs | Consultar logs dos containers | Média |
| UC10 | Manage Containers | Iniciar/parar/reiniciar containers | Alta |

---

## Fluxo de Interação
```mermaid
sequenceDiagram
    actor User as 👤 User
    participant LB as Traefik<br/>Load Balancer
    participant API as FastAPI<br/>Instance
    participant NFS as NFS Storage
    actor Admin as 👨‍💼 Admin
    participant Mon as Monitoring<br/>Stack
    
    Note over User,NFS: Use Case: Upload File
    User->>LB: POST /api/files
    LB->>API: Forward request
    API->>NFS: Save file
    NFS-->>API: Success
    API->>NFS: Update metadata
    API-->>User: 200 OK + file_id
    
    Note over Admin,Mon: Use Case: Monitor System
    Mon->>API: Scrape metrics (15s)
    API-->>Mon: CPU, Memory, Network
    Admin->>Mon: View Grafana
    Mon-->>Admin: Dashboard with metrics
    
    Note over Mon: Alert triggered
    Mon->>Admin: 🚨 HighCPUUsage Alert
```

---

## Matriz de Requisitos vs Use Cases

| Requisito | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| **Escalabilidade** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - | ✅ |
| **Disponibilidade** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Persistência** | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ | - |
| **Observabilidade** | - | - | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Load Balancing** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - | - | - |
| **Monitorização** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Tecnologias por Use Case
```mermaid
mindmap
  root((UM Drive<br/>Use Cases))
    User Operations
      Upload/Download
        FastAPI
        Traefik
        NFS
      List/Delete
        FastAPI
        JSON Metadata
        NFS
    Admin Operations
      Monitor
        cAdvisor
        Prometheus
        Grafana
      Alerts
        AlertManager
        Prometheus Rules
      Logs
        Docker Logs
        JSON Driver
```

