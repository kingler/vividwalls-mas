# 🚀 VividMAS Digital Ocean Deployment Guide

This guide will help you deploy the complete VividMAS AI automation platform on Digital Ocean with automatic SSL certificates, domain configuration, and production-ready security.

## 📋 Prerequisites

### 1. Digital Ocean Account
- Active Digital Ocean account
- Access to create droplets

### 2. Domain Requirements
- A domain name you own (e.g., `yourdomain.com`)
- Access to manage DNS records for the domain

### 3. Recommended Droplet Specifications

**For Production Use:**
- **Size**: CPU-Optimized droplet
  - **vCPUs**: 8 cores minimum (16 cores recommended)
  - **RAM**: 16 GB minimum (32 GB recommended)
  - **Storage**: 100 GB SSD minimum (200 GB recommended)
- **OS**: Ubuntu 22.04 LTS
- **Network**: Standard networking

**For Testing/Development:**
- **Size**: General Purpose droplet
  - **vCPUs**: 4 cores minimum
  - **RAM**: 8 GB minimum  
  - **Storage**: 50 GB SSD minimum
- **OS**: Ubuntu 22.04 LTS

## 🏗️ Architecture Overview

The VividMAS platform includes these services:

| Service | Purpose | Port | Domain |
|---------|---------|------|---------|
| **n8n** | Workflow automation platform | 5678 | n8n.yourdomain.com |
| **Open WebUI** | ChatGPT-like AI interface | 3000 | ui.yourdomain.com |
| **Flowise** | No-code AI agent builder | 3001 | flowise.yourdomain.com |
| **Supabase** | Database + Authentication | 8000 | supabase.yourdomain.com |
| **Langfuse** | LLM observability platform | 3002 | langfuse.yourdomain.com |
| **SearXNG** | Privacy-focused search engine | 8080 | search.yourdomain.com |
| **Ollama** | Local LLM server | 11434 | ollama.yourdomain.com |
| **Caddy** | Reverse proxy + SSL | 80/443 | - |

**Supporting Services:**
- PostgreSQL (database)
- Redis/Valkey (caching)
- Qdrant (vector database)
- ClickHouse (analytics)
- MinIO (S3-compatible storage)

## 🚀 Deployment Steps

### Step 1: Create Digital Ocean Droplet

1. **Log into Digital Ocean** and click "Create Droplet"

2. **Choose Image**: Ubuntu 22.04 LTS

3. **Choose Size**: 
   - For production: CPU-Optimized 8 vCPU, 16 GB RAM
   - For testing: General Purpose 4 vCPU, 8 GB RAM

4. **Choose Region**: Select closest to your users

5. **Authentication**: 
   - Add your SSH key for secure access
   - Or use password (less secure)

6. **Finalize**: 
   - Add a hostname (e.g., `vividmas-prod`)
   - Add tags if desired
   - Click "Create Droplet"

### Step 2: Configure DNS Records

**Before deployment, set up these DNS A records:**

Point these subdomains to your droplet's IP address:

```
n8n.yourdomain.com      → [DROPLET_IP]
ui.yourdomain.com       → [DROPLET_IP]
flowise.yourdomain.com  → [DROPLET_IP]
supabase.yourdomain.com → [DROPLET_IP]
langfuse.yourdomain.com → [DROPLET_IP]
search.yourdomain.com   → [DROPLET_IP]
ollama.yourdomain.com   → [DROPLET_IP]
```

**Example DNS Configuration:**
```
Type: A Record
Name: n8n
Value: 167.172.123.456  (your droplet IP)
TTL: 300 (5 minutes)
```

### Step 3: Connect to Your Droplet

```bash
# Connect via SSH (replace with your droplet IP)
ssh root@YOUR_DROPLET_IP

# Create a non-root user for security
adduser vivid
usermod -aG sudo vivid
su - vivid
```

### Step 4: Run the Deployment Script

1. **Download and execute the deployment script:**

```bash
# Download the deployment script
curl -fsSL https://raw.githubusercontent.com/vividwalls-studio/vivid_mas/vivid-main/deploy-to-digitalocean.sh -o deploy.sh

# Make it executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

2. **Follow the prompts:**
   - Enter your domain name (e.g., `yourdomain.com`)
   - Enter your email for SSL certificates
   - Wait for the automated installation (10-15 minutes)

### Step 5: Verify Deployment

After deployment completes, verify each service:

1. **Check systemd service status:**
```bash
sudo systemctl status vividmas
```

2. **Check Docker containers:**
```bash
docker ps
```

3. **Test web access:**
   - Visit `https://n8n.yourdomain.com` (should show n8n setup)
   - Visit `https://ui.yourdomain.com` (should show Open WebUI)
   - All other services should be accessible

## 🔐 Security Configuration

### Generated Credentials

The deployment script creates a `credentials.txt` file with all generated passwords. **Save this file securely** and transfer it off the server.

### Firewall Configuration

The script automatically configures UFW (Uncomplicated Firewall):

```bash
# View firewall status
sudo ufw status

# The following ports are opened:
# 22 (SSH), 80 (HTTP), 443 (HTTPS)
# 3000, 3001, 3002, 5678, 8000, 8080, 11434
```

### SSL Certificates

Caddy automatically generates and renews Let's Encrypt SSL certificates for all configured domains.

## 🛠️ Post-Deployment Configuration

### 1. Set Up n8n (Workflow Automation)

1. Visit `https://n8n.yourdomain.com`
2. Complete the initial setup:
   - Create an admin account
   - Configure your preferences
3. Import the included workflows from the `/backup` directory

### 2. Set Up Open WebUI (AI Chat Interface)

1. Visit `https://ui.yourdomain.com`
2. Create an admin account
3. Configure connection to Ollama:
   - Go to Settings → Connections
   - Set Ollama URL to: `http://ollama:11434`

### 3. Set Up Flowise (AI Agent Builder)

1. Visit `https://flowise.yourdomain.com`
2. Login with credentials from `credentials.txt`:
   - Username: `admin`
   - Password: `[generated password]`

### 4. Set Up Supabase (Database)

1. Visit `https://supabase.yourdomain.com`
2. Login with credentials from `credentials.txt`
3. Access the database dashboard

### 5. Configure Service Connections

**Connect n8n to Ollama:**
- In n8n credentials, set Ollama URL to: `http://ollama:11434`

**Connect services to PostgreSQL:**
- Host: `db` (internal Docker network)
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: `[from credentials.txt]`

## 📊 Monitoring and Management

### System Management Commands

```bash
# Check service status
sudo systemctl status vividmas

# Start services
sudo systemctl start vividmas

# Stop services
sudo systemctl stop vividmas

# Restart services
sudo systemctl restart vividmas

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f n8n
docker-compose logs -f ollama
```

### Resource Monitoring

```bash
# Check resource usage
htop

# Check disk usage
df -h

# Check Docker resource usage
docker stats
```

### Database Management

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U postgres -d postgres

# Backup database
docker exec postgres pg_dump -U postgres postgres > backup.sql

# Restore database
docker exec -i postgres psql -U postgres postgres < backup.sql
```

## 🔧 Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker containers
cd vivid_mas
docker-compose pull
sudo systemctl restart vividmas
```

### Backup Strategy

**Important files to backup:**
- `credentials.txt` (passwords and keys)
- `.env` (environment configuration)
- Docker volumes (persistent data)

```bash
# Backup Docker volumes
docker run --rm -v vivid_mas_n8n_storage:/data -v $(pwd):/backup ubuntu tar czf /backup/n8n_backup.tar.gz /data

# Backup PostgreSQL
docker exec postgres pg_dump -U postgres postgres > postgres_backup.sql
```

## 🚨 Troubleshooting

### Common Issues

**1. Services not starting:**
```bash
# Check Docker status
sudo systemctl status docker

# Check logs
docker-compose logs

# Restart Docker
sudo systemctl restart docker
```

**2. SSL certificate issues:**
```bash
# Check Caddy logs
docker-compose logs caddy

# Verify DNS resolution
nslookup n8n.yourdomain.com
```

**3. Memory issues:**
```bash
# Check memory usage
free -h

# If out of memory, consider upgrading droplet
# or reducing services
```

**4. Port conflicts:**
```bash
# Check what's using ports
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Log Locations

```bash
# Application logs
docker-compose logs [service_name]

# System logs
journalctl -u vividmas

# Caddy logs (SSL/proxy)
docker-compose logs caddy
```

## 💰 Cost Estimation

**Monthly costs for different droplet sizes:**

| Droplet Size | vCPUs | RAM | Storage | Monthly Cost* |
|-------------|-------|-----|---------|---------------|
| 4 vCPU, 8GB | 4 | 8 GB | 160 GB | ~$48/month |
| 8 vCPU, 16GB | 8 | 16 GB | 320 GB | ~$96/month |
| 16 vCPU, 32GB | 16 | 32 GB | 640 GB | ~$192/month |

*Prices are estimates and may vary

**Additional costs:**
- Domain name: ~$10-15/year
- SSL certificates: Free (Let's Encrypt)
- Backups: ~$2-5/month (optional)

## 🔗 Additional Resources

- [VividMAS GitHub Repository](https://github.com/vividwalls-studio/vivid_mas)
- [n8n Documentation](https://docs.n8n.io/)
- [Supabase Self-Hosting Guide](https://supabase.com/docs/guides/self-hosting)
- [Digital Ocean Droplet Documentation](https://docs.digitalocean.com/products/droplets/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs using the commands provided
3. Check the GitHub repository for known issues
4. Create an issue on the GitHub repository with:
   - Error messages
   - Log outputs
   - Droplet specifications
   - Steps to reproduce

---

**⚠️ Security Notice**: Always keep your droplet updated, use strong passwords, and regularly backup your data. The generated credentials should be stored securely and never shared publicly. 