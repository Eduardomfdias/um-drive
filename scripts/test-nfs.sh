#!/bin/bash
# Script para testar se o NFS está a funcionar corretamente

echo "=============================="
echo "  TESTE DE FUNCIONAMENTO NFS  "
echo "=============================="

MOUNT_POINT="/mnt/umdrive_storage"

echo "[1/4] Verificando se NFS está montado..."
if mountpoint -q $MOUNT_POINT; then
    echo "✅ NFS montado em $MOUNT_POINT"
else
    echo "❌ NFS NÃO está montado!"
    exit 1
fi

echo "[2/4] Testando permissões de escrita..."
TEST_FILE="$MOUNT_POINT/test_$(date +%s).txt"
if echo "Teste de escrita NFS - $(hostname) - $(date)" > $TEST_FILE 2>/dev/null; then
    echo "✅ Escrita funcional"
    cat $TEST_FILE
    rm $TEST_FILE
else
    echo "❌ Sem permissões de escrita!"
    exit 1
fi

echo "[3/4] Verificando espaço disponível..."
df -h $MOUNT_POINT

echo "[4/4] Listando ficheiros no NFS..."
ls -lah $MOUNT_POINT

echo ""
echo "✅ Todos os testes passaram com sucesso!"
