# Dashboards e Métricas - Grafana

## Dashboards Configurados

### Dashboard 893 - Docker & System Monitoring (Editada)
Monitorização de containers e recursos do sistema.

**Painéis configurados:**
- Network Traffic (total)
- Containers (contagem: 8)
- CPU Usage (%)
- Sent/Received Network Traffic per Container
- Memory Swap per Container
- CPU Usage per Container
- Memory Usage per Container
- Usage memory / Remaining memory / Limit memory (tabelas)

**O que mostra:**
- 3 réplicas UM Drive API em execução
- Traefik load balancer
- Prometheus, Grafana, AlertManager, cAdvisor
- Consumo de recursos em tempo real por container

---

### Dashboard 14282 - cAdvisor Exporter
Métricas detalhadas de containers via cAdvisor.

**Métricas disponíveis:**
- Container CPU Usage (%)
- Container Memory Usage vs limite
- Filesystem I/O
- Network Traffic (bytes sent/received)
- Container uptime
- Process count por container

**O que mostra:**
- Comparação de recursos entre as 3 réplicas API
- Performance individual de cada container
- Utilização de disco e rede
- Picos de carga e tendências

---

### UM Drive API - Complete Metrics (Custom Dashboard)
Dashboard personalizada focada nas métricas da aplicação e operações CRUD.

#### **Painéis incluídos (12 no total):**

**1. CRUD Operations Rate (req/s)**
- Gráfico temporal com requests/segundo separados por método HTTP
- Linhas individuais: GET, POST, PUT, DELETE
- Mostra atividade CRUD em tempo real

**2. Request Latency (Percentiles)**
- Latência da API em percentis
- p50 (mediana), p95, p99
- Identifica degradação de performance

**3-7. CRUD Counters**
- **Total Requests**: Contador total de todas as operações
- **GET (Read)**: Total de operações de leitura
- **POST (Create)**: Total de operações de criação
- **PUT (Update)**: Total de operações de atualização
- **DELETE (Delete)**: Total de operações de remoção
- Cada um com cor diferente para identificação visual

**8. Success (2xx)**
- Contador de requests bem-sucedidos
- Status codes 2xx

**9. HTTP Status Codes**
- Gráfico temporal de status codes
- 2xx (Success), 4xx (Client Error), 5xx (Server Error)
- Identifica padrões de erro

**10. Requests by Endpoint**
- Requests por endpoint específico
- Mostra quais endpoints são mais utilizados
- Útil para identificar hotspots

**11. Request/Response Size**
- Tamanho médio de requests e responses
- Em bytes
- Monitoriza transfer de dados

**12. API Memory Usage**
- Consumo de memória das instâncias da API
- Resident memory vs Virtual memory
- Identifica memory leaks

#### **Queries utilizadas:**

```promql
# CRUD Operations Rate
sum(rate(http_requests_total{method="GET"}[1m]))
sum(rate(http_requests_total{method="POST"}[1m]))
sum(rate(http_requests_total{method="PUT"}[1m]))
sum(rate(http_requests_total{method="DELETE"}[1m]))

# Latency Percentiles
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))

# Status Codes
sum(rate(http_requests_total{status="2xx"}[1m]))
sum(rate(http_requests_total{status="4xx"}[1m]))
sum(rate(http_requests_total{status="5xx"}[1m]))

# Request/Response Size
rate(http_request_size_bytes_sum[1m]) / rate(http_request_size_bytes_count[1m])
rate(http_response_size_bytes_sum[1m]) / rate(http_response_size_bytes_count[1m])

# Memory Usage
process_resident_memory_bytes
process_virtual_memory_bytes
```

---

## Importar Dashboards

### Dashboard 893 e 14282 (Pré-configuradas)
1. Grafana → Dashboards → New → Import
2. Inserir ID: `893` ou `14282`
3. Selecionar data source: **Prometheus**
4. Import

### UM Drive API - Complete Metrics (Custom)
1. Grafana → Dashboards → New → Import
2. Upload JSON file: `um-drive-dashboard-complete.json`
3. Confirmar data source: **Prometheus**
4. UID sugerido: `um-drive-api-complete`
5. Import

Localização do ficheiro: `/home/iti2025/um-drive/` ou disponibilizado separadamente.

---

## Métricas Prometheus da API

A aplicação expõe métricas em `/metrics`:

### **HTTP Metrics**
```promql
# Total requests por endpoint e método
http_requests_total{handler="/api/files", method="GET"}
http_requests_total{handler="/api/files/{file_id}", method="GET"}
http_requests_total{handler="/api/files/{file_id}", method="PUT"}
http_requests_total{handler="/api/files/{file_id}", method="DELETE"}

# Latência dos requests (histograma)
http_request_duration_seconds_bucket{handler="/api/files", method="POST"}
http_request_duration_seconds_sum
http_request_duration_seconds_count

# Tamanho dos requests/responses
http_request_size_bytes_sum
http_request_size_bytes_count
http_response_size_bytes_sum
http_response_size_bytes_count
```

### **Process Metrics**
```promql
# CPU e memória do processo Python
process_cpu_seconds_total
process_resident_memory_bytes
process_virtual_memory_bytes

# File descriptors
process_open_fds
process_max_fds

# Python garbage collection
python_gc_objects_collected_total
python_gc_collections_total
```

---

## Casos de Uso

### **Monitorizar Performance CRUD**
- Dashboard: **UM Drive API - Complete Metrics**
- Painéis: CRUD Operations Rate + Request Latency
- Uso: Verificar se operações estão balanceadas entre réplicas

### **Diagnosticar Problemas**
- Dashboard: **Dashboard 893**
- Painéis: Container CPU/Memory
- Uso: Identificar container com problemas de recursos

### **Análise de Erros**
- Dashboard: **UM Drive API - Complete Metrics**
- Painel: HTTP Status Codes
- Uso: Ver picos de 4xx (erros cliente) ou 5xx (erros servidor)

### **Capacity Planning**
- Dashboard: **cAdvisor Exporter (14282)**
- Painéis: Resource usage trends
- Uso: Determinar quando escalar réplicas

---

## Acesso aos Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |
| Traefik Dashboard | http://localhost:8081 | - |
| cAdvisor | http://localhost:8080 | - |
| UM Drive API | http://localhost/docs | - |

**Nota:** Se aceder remotamente, substituir `localhost` pelo IP da VM: `192.168.0.3`

---

## Estrutura de Monitorização

```
┌─────────────────────┐
│      Grafana        │ ← Visualização (3 dashboards)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│     Prometheus      │ ← Recolha métricas (15s interval)
└──────────┬──────────┘
           │
           ├─────► cAdvisor (métricas containers)
           ├─────► UM Drive API-1 (métricas aplicação)
           ├─────► UM Drive API-2 (métricas aplicação)
           ├─────► UM Drive API-3 (métricas aplicação)
           └─────► AlertManager (gestão alertas)
```

---

## Configuração de Data Source

### Primeira vez (se não configurado):
1. Grafana → Configuration (⚙️) → Data Sources
2. Add data source → Prometheus
3. URL: `http://prometheus:9090`
4. Access: Server (default)
5. Save & Test

**Nota:** O nome do serviço `prometheus` funciona porque todos os containers estão na mesma rede Docker (`um-drive-network`).

---

## Troubleshooting

### Dashboard não mostra dados
```bash
# Verificar se Prometheus está a fazer scrape
curl http://localhost:9090/api/v1/targets

# Verificar se API expõe métricas
curl http://localhost/metrics

# Verificar logs
docker logs grafana
docker logs prometheus
```

### Queries retornam vazio
- Verificar se há tráfego na API (fazer requests)
- Ajustar time range no Grafana (últimos 15 min)
- Verificar se data source está correto

