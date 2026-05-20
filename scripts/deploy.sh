#!/bin/bash
# Minimarket Deploy Skripti
set -e
APP_DIR="/opt/minimarket"
COMPOSE="docker compose -f docker-compose.prod.yml"

if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "❌ .env.production topilmadi! /opt/minimarket/ ga ko'chiring"
    exit 1
fi

cd $APP_DIR
echo "🔨 Docker image'lar qurilmoqda..."
$COMPOSE build --no-cache

echo "⏹  Eski containerlar to'xtatilmoqda..."
$COMPOSE down --remove-orphans

echo "▶️  Ishga tushirilmoqda..."
$COMPOSE up -d

echo ""
$COMPOSE ps
echo "✅ Deploy muvaffaqiyatli!"
