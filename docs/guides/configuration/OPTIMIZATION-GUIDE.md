# VividMAS Optimized Setup Guide

## 🎯 Overview

This guide helps you optimize your VividMAS stack to run efficiently on a **4 vCPU, 8GB RAM** Digital Ocean droplet by reducing services to only the essentials:

- **n8n** - Workflow automation
- **WordPress** - Main website/CMS  
- **Supabase** - Database and authentication
- **OpenWebUI** - AI chat interface
- **Caddy** - Reverse proxy with SSL

## 💰 Cost Optimization

**Before**: Full stack (~15+ services) requiring 16GB+ RAM = **$96+/month**
**After**: Essential stack (5 services) on 8GB RAM = **$48/month**
**Savings**: **~$48/month** (50% reduction)

## 🖥️ Recommended Digital Ocean Droplet

### Configuration
- **CPU**: 4 vCPUs (Regular Intel or AMD)
- **Memory**: 8GB RAM
- **Storage**: 160GB SSD
- **Cost**: ~$48/month
- **Bandwidth**: 5TB transfer

### Memory Allocation
```
Service          Memory Usage
n8n              ~512MB-1GB
WordPress Stack  ~1.5-2GB (WordPress + MySQL + Redis)
Supabase Stack   ~3-4GB (PostgreSQL + Auth + API)
OpenWebUI        ~1-1.5GB
Caddy            ~50-100MB
System Overhead  ~1GB
Buffer           ~1GB
Total            ~7-8GB (fits in 8GB)
```

## 🚀 Quick Deployment

### Step 1: Backup Current Setup
```bash
# SSH into your server
ssh root@157.230.13.13

# Navigate to project directory
cd /home/vivid/vivid_mas

# Run the optimized deployment script
./scripts/deploy-optimized.sh
```

### Step 2: DNS Configuration
Add these A records to your `vividwalls.blog` domain:

```
n8n.vividwalls.blog      → 157.230.13.13
webui.vividwalls.blog    → 157.230.13.13  
supabase.vividwalls.blog → 157.230.13.13
vividwalls.blog          → 157.230.13.13
```

### Step 3: Verify Deployment
```bash
# Check service status
docker-compose ps

# Monitor resource usage
./monitor-resources.sh

# View logs if needed
docker-compose logs -f n8n
```

## 📁 File Structure

```
vivid_mas/
├── docker-compose.optimized.yml    # Optimized main services
├── env.optimized                   # Streamlined environment config
├── Caddyfile.optimized            # Reverse proxy config
└── scripts/
    └── deploy-optimized.sh         # Automated deployment

wordpress-compose.optimized.yml     # Optimized WordPress stack
monitor-resources.sh                # Resource monitoring script
```

## 🔧 Configuration Changes

### Services Removed
- **Ollama** (Local LLM) - Use external APIs instead
- **Qdrant** (Vector DB) - Use Supabase vector extensions
- **Flowise** (AI Builder) - Use n8n for AI workflows
- **Langfuse** (LLM Observability) - Simplify monitoring
- **SearXNG** (Search) - Use external search APIs
- **ClickHouse** (Analytics DB) - Use Supabase analytics
- **MinIO** (Object Storage) - Use Supabase storage
- **Redis** (Caching) - Only keep WordPress Redis

### Memory Limits Added
```yaml
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 512M
```

### Database Optimizations
```yaml
# MySQL for WordPress
command: --innodb-buffer-pool-size=256M

# Redis for WordPress  
command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
```

## 🌐 Access URLs

After deployment, your services will be available at:

- **Main Website**: https://vividwalls.blog
- **n8n Workflows**: https://n8n.vividwalls.blog
- **AI Chat**: https://webui.vividwalls.blog  
- **Supabase**: https://supabase.vividwalls.blog

## 📊 Monitoring & Maintenance

### Resource Monitoring
```bash
# Check overall system resources
./monitor-resources.sh

# Check specific service logs
docker-compose logs -f [service-name]

# View container resource usage
docker stats
```

### Common Commands
```bash
# Restart a service
docker-compose restart n8n

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Update a service
docker-compose pull [service-name]
docker-compose up -d [service-name]
```

## 🔒 Security Features

### SSL/TLS
- Automatic Let's Encrypt certificates via Caddy
- HTTPS enforced for all services
- Security headers configured

### Network Security
- Services isolated in Docker networks
- Only necessary ports exposed
- Reverse proxy handles external access

## 🚨 Troubleshooting

### High Memory Usage
```bash
# Check memory usage
free -h

# Find memory-hungry processes
ps aux --sort=-%mem | head -10

# Restart services if needed
docker-compose restart
```

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Check available resources
df -h
free -h

# Restart Docker if needed
sudo systemctl restart docker
```

### SSL Certificate Issues
```bash
# Check Caddy logs
docker-compose logs caddy

# Verify DNS propagation
nslookup n8n.vividwalls.blog

# Restart Caddy
docker-compose restart caddy
```

## 📈 Performance Tips

### 1. Database Optimization
- Regular database cleanup
- Optimize WordPress database monthly
- Monitor Supabase query performance

### 2. Resource Management
- Monitor memory usage weekly
- Clean Docker images monthly: `docker system prune -f`
- Rotate logs to prevent disk filling

### 3. Backup Strategy
```bash
# Backup databases
docker exec wordpress-mysql mysqldump -u root -p wordpress > backup.sql
docker exec supabase-db pg_dump -U postgres postgres > supabase-backup.sql

# Backup volumes
docker run --rm -v wordpress_data:/data -v $(pwd):/backup alpine tar czf /backup/wordpress-backup.tar.gz /data
```

## 🔄 Rollback Plan

If you need to revert to the full stack:

```bash
# Restore original configurations
cp vivid_mas/docker-compose.yml.backup vivid_mas/docker-compose.yml
cp vivid_mas/.env.backup vivid_mas/.env
cp vivid_mas/Caddyfile.backup vivid_mas/Caddyfile

# Restart with original config
cd vivid_mas
docker-compose down
docker-compose up -d
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs [service]`
3. Monitor resources: `./monitor-resources.sh`
4. Consider upgrading droplet if consistently hitting memory limits

## 🎉 Benefits of Optimized Setup

✅ **50% cost reduction** ($48/month vs $96/month)
✅ **Faster startup times** (fewer services to initialize)
✅ **Better resource utilization** (memory limits prevent runaway processes)
✅ **Simplified maintenance** (fewer moving parts)
✅ **Professional domain setup** (SSL-secured subdomains)
✅ **Maintained core functionality** (all essential features preserved)

This optimized setup provides the core VividMAS functionality while significantly reducing resource requirements and costs. 