# 🌐 VividMAS Infrastructure - Complete URL Directory

**Last Updated**: May 26, 2025  
**Server**: 157.230.13.13 (DigitalOcean)  
**Domain**: vividwalls.blog  
**Status**: All services operational with HTTPS ✅

## 🚀 **LIVE HTTPS SERVICES - All Working!**

### **Core Platform Services**

1. **WordPress Main Site**
   - 🔗 **[https://vividwalls.blog](https://vividwalls.blog)**
   - 📝 Description: Main WordPress multisite (vividwalls-studio)
   - 🔧 Admin: [https://vividwalls.blog/wp-admin](https://vividwalls.blog/wp-admin)
   - 👤 Login: kingler-admin / VQC$RkIJxzZDL)xh(Y

2. **n8n Workflow Automation**
   - 🔗 **[https://n8n.vividwalls.blog](https://n8n.vividwalls.blog)**
   - 📝 Description: Visual workflow automation platform
   - 🐳 Container: `n8n` (port 5678)

3. **Open WebUI (LLM Chat Interface)**
   - 🔗 **[https://webui.vividwalls.blog](https://webui.vividwalls.blog)**
   - 📝 Description: Modern AI chat interface for LLMs
   - 🐳 Container: `open-webui` (port 8080)

4. **Langfuse (LLM Analytics & Observability)**
   - 🔗 **[https://langfuse.vividwalls.blog](https://langfuse.vividwalls.blog)**
   - 📝 Description: LLM observability, analytics, and prompt management
   - 🐳 Container: `vivid_mas-langfuse-web-1` (port 3000)

5. **Flowise (No-Code AI Builder)**
   - 🔗 **[https://flowise.vividwalls.blog](https://flowise.vividwalls.blog)**
   - 📝 Description: Visual AI workflow builder with drag-and-drop interface
   - 🐳 Container: `flowise` (port 3001)

6. **SearXNG (Privacy Search Engine)**
   - 🔗 **[https://searxng.vividwalls.blog](https://searxng.vividwalls.blog)**
   - 📝 Description: Privacy-focused metasearch engine
   - 🐳 Container: `searxng` (port 8080)

7. **Supabase API Gateway**
   - 🔗 **[https://supabase.vividwalls.blog](https://supabase.vividwalls.blog)**
   - 📝 Description: Database API and authentication gateway
   - 🐳 Container: `supabase-kong` (port 8000)

8. **Ollama (Local LLM Server)**
   - 🔗 **[https://ollama.vividwalls.blog](https://ollama.vividwalls.blog)**
   - 📝 Description: Local large language model server
   - 🐳 Container: `ollama` (port 11434)

## 🔧 **INFRASTRUCTURE SERVICES**

### **Database & Storage**

9. **PostgreSQL (Main Database)**
   - 🐳 Container: `postgres` (port 5432)
   - 📝 Description: Primary database for WordPress and applications
   - 🔒 Internal access only

10. **Supabase Database**
    - 🐳 Container: `supabase-db` (port 5432)
    - 📝 Description: Supabase PostgreSQL instance
    - 🔒 Internal access only

11. **Redis Cache**
    - 🐳 Container: `vivid_mas-langfuse-redis-1` (port 6379)
    - 📝 Description: Redis cache for Langfuse
    - 🔒 Internal access only

12. **ClickHouse Analytics**
    - 🐳 Container: `vivid_mas-langfuse-clickhouse-1` (port 8123)
    - 📝 Description: Analytics database for Langfuse
    - 🔒 Internal access only

13. **MinIO Object Storage**
    - 🐳 Container: `vivid_mas-langfuse-minio-1` (port 9000)
    - 📝 Description: S3-compatible object storage
    - 🔒 Internal access only

### **Supporting Services**

14. **Caddy Reverse Proxy**
    - 🐳 Container: `caddy` (ports 80, 443)
    - 📝 Description: Automatic HTTPS reverse proxy and load balancer
    - 🔧 Manages SSL certificates for all domains

15. **Langfuse Worker**
    - 🐳 Container: `vivid_mas-langfuse-worker-1`
    - 📝 Description: Background job processor for Langfuse
    - 🔒 Internal service only

## 📊 **CONTAINER SUMMARY**

| Service Type | Count | Status |
|--------------|-------|--------|
| **Web Applications** | 8 | ✅ All HTTPS-enabled |
| **Databases** | 4 | ✅ Running |
| **Infrastructure** | 3 | ✅ Running |
| **Total Containers** | 15 | ✅ All operational |

## 🔐 **SECURITY & ACCESS**

### **SSL Certificates**
- ✅ All domains have valid Let's Encrypt certificates
- ✅ Automatic renewal via Caddy
- ✅ HTTPS-only access enforced

### **DNS Configuration**
- ✅ All subdomains configured in DigitalOcean DNS
- ✅ TTL: 300 seconds (5 minutes)
- ✅ All pointing to 157.230.13.13

### **Network Configuration**
- 🌐 Network: `vivid_mas` (unified Docker network)
- 🔒 Internal container communication
- 🚪 External access via Caddy reverse proxy only

## 🛠 **ADMINISTRATION**

### **Server Access**
```bash
ssh -i ~/.ssh/digitalocean root@157.230.13.13
cd /home/vivid/vivid_mas
```

### **Container Management**

```bash
# View all containers
docker ps

# Restart specific service
docker-compose restart [service-name]

# View logs
docker logs [container-name]

# Restart Caddy (for SSL/config changes)
docker-compose restart caddy
```

### **DNS Management**

```bash
# List DNS records
doctl compute domain records list vividwalls.blog

# Add new subdomain
doctl compute domain records create vividwalls.blog \
  --record-type A \
  --record-name [subdomain] \
  --record-data 157.230.13.13 \
  --record-ttl 300
```

## 🎯 **QUICK ACCESS LINKS**

**Most Used Services:**

- 🏠 [Main Site](https://vividwalls.blog)
- 🔧 [WordPress Admin](https://vividwalls.blog/wp-admin)
- 🤖 [AI Chat](https://webui.vividwalls.blog)
- ⚡ [Workflows](https://n8n.vividwalls.blog)
- 📊 [Analytics](https://langfuse.vividwalls.blog)
- 🔍 [Search](https://searxng.vividwalls.blog)

**Development Tools:**

- 🧠 [AI Builder](https://flowise.vividwalls.blog)
- 🗄️ [Database API](https://supabase.vividwalls.blog)
- 🤖 [Local LLMs](https://ollama.vividwalls.blog)

---

**🎉 VividMAS Platform Status: FULLY OPERATIONAL**  
*Complete AI automation infrastructure with 15 containers running on unified network*
