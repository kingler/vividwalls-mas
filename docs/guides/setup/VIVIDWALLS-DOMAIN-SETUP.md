# VividMAS Professional Domain Setup Guide

## 🎯 Overview

This guide will configure your VividMAS platform to use your professional domain **vividwalls.blog** with proper HTTPS and SSL certificates. This will resolve the secure cookie issue and give you a professional setup.

## 🚀 Quick Setup (Automated)

### Prerequisites

1. **DigitalOcean CLI (doctl)** installed and authenticated:
   ```bash
   # Install doctl (if not already installed)
   brew install doctl
   
   # Authenticate with your DigitalOcean account
   doctl auth init
   # Enter your DigitalOcean API token when prompted
   ```

2. **SSH access** to your server (157.230.13.13)

### Run the Setup Script

```bash
# Execute the automated domain setup
./scripts/setup-vividwalls-domain.sh
```

This script will:
- ✅ Create DNS A records for all VividMAS services
- ✅ Update server configuration files
- ✅ Enable HTTPS and SSL certificates
- ✅ Fix the secure cookie issue
- ✅ Restart all services

## 🌐 Your New Service URLs

After setup completion (5-30 minutes for DNS propagation):

| Service | URL | Description |
|---------|-----|-------------|
| **n8n** | https://n8n.vividwalls.blog | Workflow Automation |
| **Open WebUI** | https://webui.vividwalls.blog | AI Chat Interface |
| **Flowise** | https://flowise.vividwalls.blog | No-code AI Builder |
| **Supabase** | https://supabase.vividwalls.blog | Database + Auth |
| **Langfuse** | https://langfuse.vividwalls.blog | LLM Observability |
| **SearXNG** | https://search.vividwalls.blog | Privacy Search |
| **Ollama** | https://ollama.vividwalls.blog | Local LLMs |
| **WordPress** | https://wordpress.vividwalls.blog | CMS Admin |

## 🔍 Verification

Check the setup status:

```bash
# Run the verification script
./scripts/verify-domain-setup.sh
```

This will check:
- ✅ DNS propagation status
- ✅ SSL certificate generation
- ✅ Service health
- ✅ Server connectivity

## 📊 Manual Verification Commands

```bash
# Check DNS propagation
dig +short n8n.vividwalls.blog

# Test SSL certificate
curl -I https://n8n.vividwalls.blog

# Monitor Caddy logs (SSL certificate generation)
ssh root@157.230.13.13 "docker logs caddy --follow"

# Check all services status
ssh root@157.230.13.13 "cd /home/vivid/vivid_mas && docker-compose ps"
```

## 🔧 WordPress Admin Access

- **URL**: https://wordpress.vividwalls.blog/wp-admin/
- **Username**: `kingler-admin`
- **Password**: `VQC$RkIJxzZDL)xh(Y`
- **Email**: `kingler@vividwalls.co`

## ⏱️ Timeline

1. **Immediate (0-2 minutes)**: DNS records created
2. **5-30 minutes**: DNS propagation completes
3. **5-15 minutes after DNS**: SSL certificates generated
4. **Total time**: Usually 10-45 minutes for full setup

## 🛠️ What the Setup Changes

### DNS Records Created
```
n8n.vividwalls.blog      → 157.230.13.13
webui.vividwalls.blog    → 157.230.13.13
flowise.vividwalls.blog  → 157.230.13.13
supabase.vividwalls.blog → 157.230.13.13
langfuse.vividwalls.blog → 157.230.13.13
search.vividwalls.blog   → 157.230.13.13
ollama.vividwalls.blog   → 157.230.13.13
wordpress.vividwalls.blog → 157.230.13.13
```

### Server Configuration Updates
- ✅ Environment variables updated with domain hostnames
- ✅ n8n webhook URL changed to `https://n8n.vividwalls.blog`
- ✅ Secure cookies enabled (`N8N_SECURE_COOKIE=true`)
- ✅ Let's Encrypt email configured
- ✅ Caddy reverse proxy configured for all services
- ✅ WordPress domain configuration updated

## 🔒 Security Improvements

- **HTTPS Everywhere**: All services now use SSL/TLS encryption
- **Automatic SSL Renewal**: Caddy handles Let's Encrypt certificate renewal
- **Secure Cookies**: n8n secure cookie issue resolved
- **Professional URLs**: No more IP addresses in URLs

## 🆘 Troubleshooting

### DNS Not Propagating
```bash
# Check current DNS status
dig +short n8n.vividwalls.blog

# If empty, wait 10-15 minutes and check again
# DNS propagation can take up to 30 minutes
```

### SSL Certificate Issues
```bash
# Check Caddy logs for certificate generation
ssh root@157.230.13.13 "docker logs caddy --follow"

# Common issues:
# - DNS not propagated yet (wait for DNS first)
# - Let's Encrypt rate limits (wait 1 hour)
# - Firewall blocking port 80/443
```

### Service Not Responding
```bash
# Check if services are running
ssh root@157.230.13.13 "cd /home/vivid/vivid_mas && docker-compose ps"

# Restart specific service
ssh root@157.230.13.13 "cd /home/vivid/vivid_mas && docker-compose restart n8n"

# Check service logs
ssh root@157.230.13.13 "docker logs n8n --follow"
```

### Rollback (Emergency)
```bash
# If something goes wrong, rollback to IP-based setup
ssh root@157.230.13.13 "cd /home/vivid/vivid_mas && \
  cp .env.backup-* .env && \
  docker-compose restart caddy n8n"
```

## 🎉 Benefits of This Setup

1. **Professional URLs**: Clean, branded domain names
2. **HTTPS Security**: All traffic encrypted
3. **No More Cookie Issues**: Secure cookies work properly
4. **Automatic SSL**: Certificates auto-renew
5. **Better SEO**: Professional domain for WordPress
6. **Easier Sharing**: Clean URLs for team collaboration

## 📞 Support

If you encounter any issues:

1. Run the verification script: `./scripts/verify-domain-setup.sh`
2. Check the troubleshooting section above
3. Monitor logs: `ssh root@157.230.13.13 "docker logs caddy --follow"`

Your VividMAS platform will be professionally configured and ready for production use! 🚀 