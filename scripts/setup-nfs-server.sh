#!/bin/bash
# Script para configurar NFS Server (executar na VM3)

set -e  # Parar se houver erro

echo "==================================="
echo "  CONFIGURAÇÃO NFS SERVER (VM3)   "
echo "==================================="

# Atualizar sistema
echo "[1/6] Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar NFS Server
echo "[2/6] Instalando NFS Server..."
sudo apt install -y nfs-kernel-server

# Criar diretório partilhado
echo "[3/6] Criando diretório partilhado..."
sudo mkdir -p /srv/nfs/umdrive
sudo chown -R nobody:nogroup /srv/nfs/umdrive
sudo chmod 777 /srv/nfs/umdrive

# Configurar exports
echo "[4/6] Configurando /etc/exports..."
EXPORT_LINE="/srv/nfs/umdrive 192.168.56.0/24(rw,sync,no_subtree_check,no_root_squash)"

if grep -q "/srv/nfs/umdrive" /etc/exports; then
    echo "Configuração já existe em /etc/exports"
else
    echo "$EXPORT_LINE" | sudo tee -a /etc/exports
fi

# Aplicar configuração
echo "[5/6] Aplicando configuração..."
sudo exportfs -a
sudo exportfs -v

# Reiniciar serviço NFS
echo "[6/6] Reiniciando NFS Server..."
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server

# Mostrar status
echo ""
echo "✅ NFS Server configurado com sucesso!"
echo ""
echo "📊 Status do serviço:"
sudo systemctl status nfs-kernel-server --no-pager
echo ""
echo "📁 Diretório partilhado: /srv/nfs/umdrive"
echo "🌐 Rede permitida: 192.168.56.0/24"
echo ""
echo "Para testar de outro servidor:"
echo "  showmount -e $(hostname -I | awk '{print $1}')"
