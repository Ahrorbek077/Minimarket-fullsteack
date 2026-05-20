#!/bin/bash
# SSL sertifikat olish
# Ishlatish: bash ssl-setup.sh yourdomain.com email@mail.com
DOMAIN=$1; EMAIL=$2
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Ishlatish: bash ssl-setup.sh yourdomain.com email@example.com"
    exit 1
fi
cd /opt/minimarket
docker compose -f docker-compose.prod.yml run --rm certbot \
    certonly --webroot --webroot-path=/var/www/certbot \
    --email $EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN -d www.$DOMAIN
echo "✅ SSL olindi! Nginx conf dagi YOUR_DOMAIN.COM ni $DOMAIN ga almashtiring"
