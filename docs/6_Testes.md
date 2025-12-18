# 6. Testes

## Testes Unitários

### Executar
```bash
# Instalar dependências
pip install --break-system-packages -r requirements.txt

# Executar todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app --cov-report=html
```

### Cobertura
- **21 testes** (12 API + 9 File Service)
- Endpoints CRUD completos
- Health check
- Casos de erro (404)
- Concorrência

### Resultados
```
tests/test_api.py::TestAPI::test_root_endpoint PASSED
tests/test_api.py::TestAPI::test_health_endpoint PASSED
tests/test_api.py::TestAPI::test_upload_file PASSED
tests/test_api.py::TestAPI::test_download_file PASSED
tests/test_api.py::TestAPI::test_update_file PASSED
tests/test_api.py::TestAPI::test_delete_file PASSED
tests/test_file_service.py::TestFileService::test_save_file PASSED
tests/test_file_service.py::TestFileService::test_update_file PASSED
tests/test_file_service.py::TestFileService::test_delete_file PASSED
tests/test_file_service.py::TestFileService::test_concurrent_saves PASSED

=================== 21 passed in 2.27s ===================
```

---

## Testes CRUD

### Upload
```bash
echo "teste" > test.txt
curl -X POST -F "file=@test.txt" http://localhost/api/files
```

### List
```bash
curl http://localhost/api/files
```

### Download
```bash
curl http://localhost/api/files/{file_id} -o downloaded.txt
```

### Update
```bash
curl -X PUT -F "file=@test2.txt" http://localhost/api/files/{file_id}
```

### Delete
```bash
curl -X DELETE http://localhost/api/files/{file_id}
```

---

## Testes Load Balancing

### Distribuição de Tráfego
```bash
for i in {1..30}; do curl -s http://localhost/ | jq -r '.instance'; done | sort | uniq -c
```

**Esperado:** Distribuição aproximadamente igual entre instâncias 1, 2, 3.

### Health Check
```bash
curl http://localhost/api/health
```

---

## Testes de Resiliência

### Falha de Container
```bash
docker stop um-drive-api-2
curl http://localhost/  # Deve funcionar
docker start um-drive-api-2
```

### Reboot Sistema
```bash
sudo reboot
# Após reboot
docker ps
df -h | grep nfs
curl http://localhost/
```

### Concorrência
```bash
for i in {1..10}; do
  echo "file$i" > file$i.txt
  curl -X POST -F "file=@file$i.txt" http://localhost/api/files &
done
wait
```

---

## Testes de Monitorização

### Verificar Targets Prometheus
```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health}'
```

### Métricas API
```bash
curl http://localhost/metrics | grep http_requests_total
```

### Stress Test (Opcional)
```bash
sudo apt install -y apache2-utils
ab -n 1000 -c 10 http://localhost/api/health
```

---

## Checklist

**Funcionalidade:**
- [ ] CRUD completo funcional
- [ ] Swagger UI acessível (http://localhost/docs)

**Distribuição:**
- [ ] 3 réplicas ativas
- [ ] Load balancing equilibrado
- [ ] Sticky sessions funcionam

**Resiliência:**
- [ ] Sobrevive reboot
- [ ] Recupera de falha container
- [ ] NFS persistente

**Monitorização:**
- [ ] Todos targets Prometheus UP
- [ ] Dashboards Grafana funcionais
- [ ] Métricas aplicação expostas

---

## Validação NFS

```bash
# VM2: Criar ficheiro via API
curl -X POST -F "file=@test.txt" http://localhost/api/files

# VM1: Verificar ficheiro existe no NFS
ls -la /mnt/nfs_share/
cat /mnt/nfs_share/metadata.json
```