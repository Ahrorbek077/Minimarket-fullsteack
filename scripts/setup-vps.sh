#!/bin/bash
# VPS dastlabki sozlash — faqat BIR MARTA ishlatiladi
set -e
echo "🚀 VPS sozlash boshlanmoqda..."

apt-get update && apt-get upgrade -y
apt-get install -y curl wget git unzip ufw fail2ban htop

echo "📦 Docker o'rnatilmoqda..."
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin
systemctl enable docker && systemctl start docker
echo "✅ Docker $(docker --version)"

echo "🔒 Firewall sozlanmoqda..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

systemctl enable fail2ban && systemctl start fail2ban

mkdir -p /opt/minimarket
echo ""
echo "✅ VPS tayyor! Keyingi qadam: deploy.sh ni ishga tushiring"
