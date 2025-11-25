# 5. Monitorização

## Stack de Monitorização

### **Arquitetura**
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  cAdvisor    │─────▶│  Prometheus  │─────▶│   Grafana    │
│  (Coleta)    │      │  (Storage)   │      │  (Visualiza) │
└──────────────┘      └──────────────┘      └──────────────┘
       │
       ▼
  Docker Engine
  (containers)
```

---

## cAdvisor (Container Advisor)

### **Função**
- Monitoriza containers Docker em tempo real
- Coleta métricas de: CPU, memória, rede, disco
- Expõe endpoint HTTP para Prometheus

### **Configuração**
```yaml
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  ports:
    - "8080:8080"
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
  privileged: true
```

### **Acesso**
- URL: http://localhost:8080
- Interface web com métricas em tempo real
- Endpoint Prometheus: http://cadvisor:8080/metrics

### **Métricas Principais**
- `container_cpu_usage_seconds_total`
- `container_memory_usage_bytes`
- `container_network_receive_bytes_total`
- `container_network_transmit_bytes_total`
- `container_fs_reads_bytes_total`
- `container_fs_writes_bytes_total`

---

## Prometheus

### **Função**
- Time-series database para métricas
- Scraping de targets (cAdvisor, FastAPI)
- Query language (PromQL)
- Base para alerting

### **Configuração**
Ficheiro: `prometheus.yml`
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'um-drive-api'
    static_configs:
      - targets: 
          - 'um-drive-api-1:8000'
          - 'um-drive-api-2:8000'
          - 'um-drive-api-3:8000'
```

### **Acesso**
- URL: http://localhost:9090
- Interface web para queries
- Targets: Status → Targets (verificar health)

### **Queries Úteis (PromQL)**
```promql
# CPU usage por container
rate(container_cpu_usage_seconds_total[5m])

# Memória usage
container_memory_usage_bytes

# Network RX
rate(container_network_receive_bytes_total[5m])

# Network TX
rate(container_network_transmit_bytes_total[5m])

# Uptime
(time() - container_start_time_seconds) / 60
```

### **Verificação de Targets**
```bash
curl http://localhost:9090/api/v1/targets | jq
```

Todos os targets devem estar `"health": "up"`.

---

## Grafana

### **Função**
- Visualização de métricas em dashboards
- Gráficos interativos e customizáveis
- Alerting (email, Slack, etc)

### **Acesso**
- URL: http://localhost:3000
- Login: `admin` / `admin`
- (Prompt para mudar password no primeiro login)

---

## Configuração Inicial Grafana

### **1. Adicionar Data Source (Prometheus)**
1. Menu → Connections → Data Sources
2. Add data source → Prometheus
3. URL: `http://prometheus:9090`
4. Save & Test → deve aparecer "Successfully queried"

---

### **2. Importar Dashboard (Recomendado)**

**Dashboard ID: 193** (Docker Container & Host Metrics)

Passos:
1. Menu → Dashboards → Import
2. Dashboard ID: `193`
3. Load
4. Selecionar Prometheus data source
5. Import

**Ou Dashboard ID: 11600** (Docker monitoring with Prometheus)

---

### **3. Dashboard Manual (Alternativa)**

Se preferires criar dashboard personalizado:

#### **Panel 1: CPU Usage**
- Visualization: Time series
- Query:
```promql
rate(container_cpu_usage_seconds_total{name=~"um-drive-api.*"}[5m]) * 100
```
- Legend: `{{name}}`

#### **Panel 2: Memory Usage**
- Visualization: Time series
- Query:
```promql
container_memory_usage_bytes{name=~"um-drive-api.*"} / 1024 / 1024
```
- Unit: `MiB`
- Legend: `{{name}}`

#### **Panel 3: Network I/O**
- Visualization: Time series
- Queries:
```promql
# RX
rate(container_network_receive_bytes_total{name=~"um-drive-api.*"}[5m])

# TX
rate(container_network_transmit_bytes_total{name=~"um-drive-api.*"}[5m])
```
- Unit: `bytes/sec`

#### **Panel 4: Disk I/O**
- Visualization: Time series
- Queries:
```promql
# Reads
rate(container_fs_reads_bytes_total{name=~"um-drive-api.*"}[5m])

# Writes
rate(container_fs_writes_bytes_total{name=~"um-drive-api.*"}[5m])
```

#### **Panel 5: Container Uptime**
- Visualization: Stat
- Query:
```promql
(time() - container_start_time_seconds{name=~"um-drive-api.*"}) / 60
```
- Unit: `minutes`

---

## Métricas Monitorizadas

### **Nível de Container**
| Métrica | Descrição | Importância |
|---------|-----------|-------------|
| CPU Usage | % utilização CPU | Identificar bottlenecks |
| Memory Usage | RAM consumida | Detectar memory leaks |
| Network RX/TX | Tráfego entrada/saída | Análise de carga |
| Disk I/O | Operações read/write | Performance storage |
| Uptime | Tempo desde start | Disponibilidade |

### **Nível de Sistema**
- Total containers running
- NFS mount status (via cAdvisor filesystem metrics)
- Traefik request rate (se configurado)

---

## Alerting (Opcional)

### **Exemplo: Alerta de CPU Alta**
```yaml
# prometheus-alerts.yml
groups:
  - name: container_alerts
    rules:
      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.name }} high CPU"
          description: "CPU usage > 80% for 5 minutes"
```

Adicionar ao Prometheus:
```yaml
rule_files:
  - "prometheus-alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

---

## Troubleshooting

### **cAdvisor não coleta métricas**
```bash
# Verificar logs
docker logs cadvisor

# Verificar permissões
ls -la /var/run/docker.sock

# Reiniciar
docker-compose restart cadvisor
```

### **Prometheus targets "down"**
```bash
# Verificar conectividade
docker exec prometheus wget -qO- http://cadvisor:8080/metrics

# Verificar config
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Reload config
docker exec prometheus kill -HUP 1
```

### **Grafana não conecta ao Prometheus**
```bash
# Testar dentro do container Grafana
docker exec grafana wget -qO- http://prometheus:9090/api/v1/query?query=up

# Verificar network
docker network inspect um-drive_um-drive-network
```

---

## Screenshots para Documentação

**Capturar:**
1. Traefik Dashboard (http://localhost:8081) mostrando os 3 backends
2. cAdvisor (http://localhost:8080) com métricas de containers
3. Prometheus Targets (http://localhost:9090/targets) todos "UP"
4. Grafana Dashboard com gráficos de CPU, memória, rede

**Guardar em:** `/docs/screenshots/`

---

## Exportar Dashboard Grafana

Para incluir no Git:
```bash
# No Grafana UI:
# Dashboard → Share → Export → Save to file

# Guardar como: grafana-dashboard.json
```
