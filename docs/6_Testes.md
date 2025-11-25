# 6. Testes

## Testes Funcionais (CRUD)

### **1. Upload de Ficheiro**
```bash
# Criar ficheiro teste
echo "Hello UM Drive" > test.txt

# Upload
curl -X POST -F "file=@test.txt" http://localhost:80/upload

# Resposta esperada:
# {"file_id":"uuid-aqui","filename":"test.txt"}
```

**Validação:**
- ✅ Status 200
- ✅ Ficheiro guardado em NFS
- ✅ Metadata atualizado
```bash
# Verificar no NFS
ls -la /mnt/nfs_share
cat /mnt/nfs_share/metadata.json
```

---

### **2. Listar Ficheiros**
```bash
curl http://localhost:80/files

# Resposta esperada:
# {"uuid": {"filename":"test.txt","size":15}}
```

---

### **3. Download de Ficheiro**
```bash
# Usar file_id do upload
curl -O http://localhost:80/download/uuid-aqui

# Verificar conteúdo
cat test.txt
```

**Validação:**
- ✅ Ficheiro descarregado
- ✅ Conteúdo idêntico ao original

---

### **4. Eliminar Ficheiro**
```bash
curl -X DELETE http://localhost:80/delete/uuid-aqui

# Resposta: {"message":"File deleted"}

# Verificar remoção
curl http://localhost:80/files
ls /mnt/nfs_share  # Ficheiro não deve existir
```

---

## Testes de Load Balancing

### **Verificar Distribuição de Tráfego**
```bash
# Fazer múltiplos requests
for i in {1..30}; do
  curl -s http://localhost:80 | jq -r '.instance'
done | sort | uniq -c

# Resultado esperado (distribuição equilibrada):
#   10 1
#   10 2
#   10 3
```

**Validação:**
- ✅ Tráfego distribuído entre 3 instâncias
- ✅ Round-robin funcional

---

### **Traefik Dashboard**
Aceder: http://localhost:8081

**Verificar:**
- ✅ 3 backends ativos
- ✅ Health checks a funcionar
- ✅ Métricas de requests

---

## Testes de Falha e Recuperação

### **Teste 1: Falha de Container**
```bash
# Parar 1 instância
docker stop um-drive-api-2

# Testar API (deve continuar a funcionar)
curl http://localhost:80

# Verificar Traefik
# Dashboard deve mostrar apenas 2 backends ativos

# Restaurar
docker start um-drive-api-2

# Traefik deve detetar automaticamente (30s)
```

**Validação:**
- ✅ Sistema continua disponível
- ✅ Traefik redireciona para instâncias saudáveis
- ✅ Recovery automático

---

### **Teste 2: Reboot do Sistema**
```bash
# VM UM Drive
sudo reboot

# Após reboot (aguardar 2-3 min)
docker ps  # Todos containers devem estar UP
df -h | grep nfs  # NFS montado
curl http://localhost:80  # API responde

# Verificar dados persistiram
curl http://localhost:80/files
```

**Validação:**
- ✅ Containers reiniciam automaticamente
- ✅ NFS mount persistente
- ✅ Dados intactos

---

### **Teste 3: Falha do NFS Server**
```bash
# Simular falha
# VM NFS: sudo systemctl stop nfs-kernel-server

# VM UM Drive: tentar upload
curl -X POST -F "file=@test.txt" http://localhost:80/upload
# Deve falhar (connection error ou timeout)

# Restaurar NFS
# VM NFS: sudo systemctl start nfs-kernel-server

# Retry upload (deve funcionar)
```

**Validação:**
- ✅ Sistema deteta falha
- ✅ Recuperação após NFS voltar

---

## Testes de Monitorização

### **Verificar Coleta de Métricas**
```bash
# cAdvisor
curl http://localhost:8080/metrics | grep container_cpu_usage

# Prometheus Targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Resultado esperado:
# {"job":"cadvisor","health":"up"}
# {"job":"um-drive-api","health":"up"}
```

---

### **Stress Test (Opcional)**
Gerar carga para ver métricas:
```bash
# Instalar Apache Bench
sudo apt install -y apache2-utils

# Teste de carga (1000 requests, 10 concorrentes)
ab -n 1000 -c 10 http://localhost:80/

# Observar no Grafana:
# - CPU spike
# - Memória
# - Network traffic
```

**Métricas Esperadas:**
- CPU: aumento temporário
- Memória: estável
- Network: aumento proporcional

---

## Testes de Concorrência

### **Upload Simultâneo**
```bash
# 10 uploads em paralelo
for i in {1..10}; do
  echo "file$i" > file$i.txt
  curl -X POST -F "file=@file$i.txt" http://localhost:80/upload &
done
wait

# Verificar todos foram guardados
curl http://localhost:80/files | jq 'keys | length'
# Deve retornar 10
```

**Validação:**
- ✅ Sem race conditions
- ✅ Todos ficheiros guardados
- ✅ Metadata consistente

---

## Checklist de Testes

### **Funcionalidade**
- [ ] Upload ficheiro
- [ ] Download ficheiro
- [ ] Listar ficheiros
- [ ] Eliminar ficheiro
- [ ] Swagger UI acessível

### **Distribuição**
- [ ] Load balancing funcional
- [ ] 3 instâncias ativas
- [ ] Traefik dashboard correto

### **Resiliência**
- [ ] Sobrevive a reboot
- [ ] Recupera de falha de container
- [ ] NFS mount persistente

### **Monitorização**
- [ ] cAdvisor coleta métricas
- [ ] Prometheus targets UP
- [ ] Grafana dashboards funcionais

### **Performance**
- [ ] Latência < 500ms (uploads pequenos)
- [ ] Concorrência sem erros
- [ ] [Opcional] Stress test suportado

---

## Resultados Esperados

### **Métricas de Sucesso**
- ✅ 100% uptime após setup
- ✅ 0% perda de dados
- ✅ Load balancing equilibrado (±10%)
- ✅ Recuperação automática < 1min

### **Logs de Teste**
Guardar logs dos testes:
```bash
# Logs containers
docker-compose logs > test-logs.txt

# Métricas Prometheus
curl http://localhost:9090/api/v1/query?query=up > test-metrics.json
```
