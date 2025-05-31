# VividMAS DNS Setup Quick Reference

## 🚀 **Quick Setup for New Domain**

```bash
# 1. Run automated DNS setup
./scripts/setup-domain-dns.sh yourdomain.com YOUR_SERVER_IP admin@yourdomain.com

# 2. Update server configuration
ssh root@YOUR_SERVER_IP "cd /home/vivid/vivid_mas && \
  sed -i 's/N8N_HOSTNAME=.*/N8N_HOSTNAME=n8n.yourdomain.com/' .env && \
  sed -i 's/LETSENCRYPT_EMAIL=.*/LETSENCRYPT_EMAIL=admin@yourdomain.com/' .env && \
  docker-compose restart caddy n8n"
```

## 📋 **Current vividwalls.blog Configuration**

| Service | URL | Port |
|---------|-----|------|
| n8n | https://n8n.vividwalls.blog | 5678 |
| Open WebUI | https://webui.vividwalls.blog | 3000 |
| Flowise | https://flowise.vividwalls.blog | 3001 |
| Supabase | https://supabase.vividwalls.blog | 8000 |
| Langfuse | https://langfuse.vividwalls.blog | 3030 |
| SearXNG | https://search.vividwalls.blog | 8080 |
| Ollama | https://ollama.vividwalls.blog | 11434 |
| WordPress | https://wordpress.vividwalls.blog | 8080 |

## 🔧 **Manual DNS Commands**

```bash
# List domains
doctl compute domain list

# List DNS records
doctl compute domain records list yourdomain.com

# Create single A record
doctl compute domain records create yourdomain.com \
  --record-type A --record-name subdomain \
  --record-data SERVER_IP --record-ttl 300

# Delete DNS record
doctl compute domain records delete yourdomain.com RECORD_ID
```

## 🔍 **Verification Commands**

```bash
# Check DNS propagation
dig +short n8n.yourdomain.com

# Test SSL certificate
curl -I https://n8n.yourdomain.com

# Monitor Caddy logs
ssh root@SERVER_IP "docker logs caddy --follow"
```

## 📁 **Important Files**

- **DNS Rule**: `.cursor/rules/digitalocean-dns-management.mdc`
- **Setup Script**: `scripts/setup-domain-dns.sh`
- **Server Config**: `/home/vivid/vivid_mas/.env`
- **Docker Compose**: `/home/vivid/vivid_mas/docker-compose.yml`
- **Caddyfile**: `/home/vivid/vivid_mas/Caddyfile`

## 🆘 **Emergency Rollback**

```bash
ssh root@SERVER_IP "cd /home/vivid/vivid_mas && \
  cp .env.backup-domain .env && \
  docker-compose restart caddy n8n"
``` 