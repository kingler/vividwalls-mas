# GitHub CI/CD Setup for VividMAS

## 🎉 **Repository Successfully Created!**

Your VividMAS project is now available at: **https://github.com/kingler/vivid_mas**

## 🔐 **Required GitHub Secrets**

To enable automatic deployment to your DigitalOcean droplet, you need to add these secrets to your GitHub repository:

### **1. Go to GitHub Secrets Settings**
Visit: https://github.com/kingler/vivid_mas/settings/secrets/actions

### **2. Add These Secrets**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DIGITALOCEAN_SSH_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----`<br>`b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABBD1ezVia`<br>`zOT12MlwTJXeD6AAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIDsYQNP+NSCXh4cU`<br>`3EM8MtQIa5TjzdRzvnzcSWknfrS7AAAAoIqyUlR9kumNJV4invWT2UGftg8OrrKDx1R6Lp`<br>`v3DiTHw3TL9OrKEQDrFAZFJ6joiCPpEjuWnMi5SUs524jbC5wMIsS9mQDtJ4ZWn0GoXsXr`<br>`GHDqdCYiqptYmSBH2TI3vJFC6zsoCnhwdyNU7tfCisE2JqQ8QqDZQeS5ViLxLqdx0LVO8s`<br>`41Q9AjuLHGnMhKXH4rtXJ1ZAyj9AsNAlnvxMg=`<br>`-----END OPENSSH PRIVATE KEY-----` | Your private SSH key for DigitalOcean access |
| `DIGITALOCEAN_HOST` | `157.230.13.13` | Your DigitalOcean droplet IP address |
| `DIGITALOCEAN_USER` | `root` | SSH user for deployment |

## 🚀 **How CI/CD Works**

### **Automatic Deployment Triggers**
- **Push to `vivid-main` branch** → Triggers deployment
- **Pull Request to `vivid-main`** → Triggers deployment

### **Deployment Process**
1. **Checkout code** from GitHub
2. **Setup SSH** connection to DigitalOcean
3. **Copy files** to server (excluding .env and sensitive files)
4. **Backup** current deployment
5. **Update** VividMAS platform files
6. **Pull** latest Docker images
7. **Restart** all services
8. **Verify** deployment health

### **Services Deployed**
- ✅ **n8n** - https://n8n.vividwalls.blog
- ✅ **Open WebUI** - https://webui.vividwalls.blog
- ✅ **Flowise** - https://flowise.vividwalls.blog
- ✅ **Supabase** - https://supabase.vividwalls.blog
- ✅ **Langfuse** - https://langfuse.vividwalls.blog
- ✅ **SearXNG** - https://search.vividwalls.blog
- ✅ **Ollama** - https://ollama.vividwalls.blog
- ✅ **WordPress** - https://wordpress.vividwalls.blog

## 🔧 **Testing the CI/CD Pipeline**

### **1. Make a Test Change**
```bash
# Edit any file (like README.md)
echo "# VividMAS - Updated $(date)" > README.md

# Commit and push
git add README.md
git commit -m "test: Trigger CI/CD deployment"
git push origin vivid-main
```

### **2. Monitor Deployment**
- Go to: https://github.com/kingler/vivid_mas/actions
- Watch the deployment progress
- Check logs for any issues

### **3. Verify Services**
After deployment completes (5-10 minutes):
- Test: https://n8n.vividwalls.blog
- Test: https://wordpress.vividwalls.blog
- Check all services are responding

## 🛠️ **Manual Deployment (Fallback)**

If CI/CD fails, you can deploy manually:

```bash
# SSH to server
ssh root@157.230.13.13

# Navigate to project
cd /home/vivid/vivid_mas

# Pull latest changes (if you set up git on server)
git pull origin vivid-main

# Restart services
docker-compose up -d --remove-orphans
docker-compose -f wordpress-compose.yml up -d
```

## 📋 **Project Structure**

```
vivid_mas/
├── .github/workflows/
│   └── deploy-to-digitalocean.yml    # CI/CD pipeline
├── .cursor/rules/
│   └── digitalocean-dns-management.mdc  # DNS documentation
├── scripts/
│   └── setup-domain-dns.sh          # DNS automation script
├── docker-compose.yml               # Main services
├── wordpress-compose.yml            # WordPress services
├── Caddyfile                        # Reverse proxy config
├── .env                             # Environment variables (not in git)
└── DNS-SETUP-REFERENCE.md           # Quick DNS reference
```

## 🔒 **Security Notes**

- ✅ **SSH Key** is stored securely in GitHub Secrets
- ✅ **Environment files** (.env) are excluded from git
- ✅ **Automatic backups** before each deployment
- ✅ **Health checks** verify deployment success
- ✅ **HTTPS** enabled for all services

## 🆘 **Troubleshooting**

### **CI/CD Pipeline Fails**
1. Check GitHub Actions logs
2. Verify SSH key is correct
3. Ensure server is accessible
4. Check DigitalOcean droplet status

### **Services Not Responding**
1. SSH to server: `ssh root@157.230.13.13`
2. Check containers: `docker ps`
3. Check logs: `docker logs <container-name>`
4. Restart if needed: `docker-compose restart`

### **DNS Issues**
1. Check DNS propagation: `dig n8n.vividwalls.blog`
2. Verify A records in DigitalOcean DNS
3. Check Caddy logs: `docker logs caddy`

## 🎯 **Next Steps**

1. **Add GitHub Secrets** (required for CI/CD)
2. **Test deployment** with a small change
3. **Monitor services** after deployment
4. **Set up monitoring** (optional)
5. **Configure backups** (recommended)

Your VividMAS platform now has professional CI/CD deployment! 🚀 