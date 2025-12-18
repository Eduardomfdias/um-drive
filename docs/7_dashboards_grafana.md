# Dashboards e Métricas - Grafana

## Dashboards Configurados

### Dashboard 893 - Docker & System Monitoring
Monitorização de containers e recursos do sistema.

**Métricas disponíveis:**
- CPU Usage por container
- Memory Usage por container
- Network I/O (tráfego entrada/saída)
- Container Status (running/stopped)
- Filesystem Usage

**O que mostra:**
- 3 réplicas UM Drive API em execução
- Traefik load balancer
- Prometheus, Grafana, AlertManager, cAdvisor
- Consumo de recursos em tempo real

---

### Dashboard 14282 - cAdvisor Exporter
Métricas detalhadas de containers via cAdvisor.

**Métricas disponíveis:**
- Container CPU Usage (%)
- Container Memory Usage vs limite
- Filesystem I/O
- Network Traffic (bytes sent/received)
- Container uptime

**O que mostra:**
- Comparação de recursos entre as 3 réplicas API
- Performance individual de cada container
- Utilização de disco e rede

---

## Métricas Prometheus da API

A aplicação expõe métricas em `/metrics`:

```promql
# Total requests por endpoint e método
http_requests_total{handler="/api/files", method="GET"}

# Latência dos requests (histograma)
http_request_duration_seconds_bucket

# Tamanho dos requests/responses
http_request_size_bytes
http_response_size_bytes

# CPU e memória do processo Python
process_cpu_seconds_total
process_resident_memory_bytes
```

---

## Acesso aos Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Grafana | http://192.168.0.3:3000 | admin/admin |
| Prometheus | http://192.168.0.3:9090 | - |
| AlertManager | http://192.168.0.3:9093 | - |
| Traefik Dashboard | http://192.168.0.3:8081 | - |
| cAdvisor | http://192.168.0.3:8080 | - |
| UM Drive API | http://192.168.0.3/docs | - |

---

## Estrutura de Monitorização

```
┌─────────────┐
│   Grafana   │ ← Visualização
└─────┬───────┘
      │
┌─────▼───────┐
│ Prometheus  │ ← Recolha métricas
└─────┬───────┘
      │
      ├─────► cAdvisor (métricas containers)
      ├─────► UM Drive APIs (métricas aplicação)
      └─────► AlertManager (alertas)
```