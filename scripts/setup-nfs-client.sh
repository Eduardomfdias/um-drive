#!/bin/bash
# Script para configurar NFS Client (executar na VM1 e VM2)

set -e

echo "===================================="
echo "  CONFIGURAÇÃO NFS CLIENT (VM1/2)  "
echo "===================================="

if [ -z "$1" ]; then
    echo "❌ Erro: IP do servidor NFS não fornecido"
    echo ""
    echo "Uso: $0 <IP_DO_SERVIDOR_NFS>"
    echo "Exemplo: $0 192.168.56.12"
    exit 1
fi

NFS_SERVER_IP=$1

echo "[1/6] Atualizando sistema..."
sudo apt update

echo "[2/6] Instalando NFS Client..."
sudo apt install -y nfs-common

echo "[3/6] Criando ponto de montagem..."
sudo mkdir -p /mnt/umdrive_storage

echo "[4/6] Testando conexão ao servidor NFS..."
if showmount -e $NFS_SERVER_IP &>/dev/null; then
    echo "✅ Servidor NFS acessível!"
    showmount -e $NFS_SERVER_IP
else
    echo "❌ Erro: Não foi possível conectar ao servidor NFS em $NFS_SERVER_IP"
    exit 1
fi

echo "[5/6] Montando NFS..."
sudo mount -t nfs $NFS_SERVER_IP:/srv/nfs/umdrive /mnt/umdrive_storage

if mountpoint -q /mnt/umdrive_storage; then
    echo "✅ NFS montado com sucesso!"
else
    echo "❌ Erro ao montar NFS"
    exit 1
fi

echo "[6/6] Configurando montagem automática..."
FSTAB_LINE="$NFS_SERVER_IP:/srv/nfs/umdrive /mnt/umdrive_storage nfs defaults 0 0"

if grep -q "$NFS_SERVER_IP:/srv/nfs/umdrive" /etc/fstab; then
    echo "Entrada já existe em /etc/fstab"
else
    echo "$FSTAB_LINE" | sudo tee -a /etc/fstab
fi

echo ""
echo "✅ NFS Client configurado com sucesso!"
echo ""
echo "📊 Montagens ativas:"
df -h | grep umdrive_storage
echo ""
echo "📁 Ponto de montagem: /mnt/umdrive_storage"
echo "🔗 Servidor NFS: $NFS_SERVER_IP:/srv/nfs/umdrive"
