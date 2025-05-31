# VividWalls Content Migration to Digital Ocean Droplet

## 📋 **Quick Migration Steps**

You have **3 options** to migrate your VividWalls knowledge base to your Digital Ocean Droplet:

---

## 🚀 **Option 1: Automated Script (Recommended)**

### Step 1: Configure the Migration Script

Edit the script with your droplet details:

```bash
nano vivid_mas/scripts/migrate-to-droplet.sh
```

Update these variables:
```bash
DROPLET_IP="YOUR_ACTUAL_DROPLET_IP"        # e.g., "143.198.123.45"
DROPLET_USER="root"                        # or your username
DROPLET_PATH="/root/vivid_mas"             # path to your project on droplet
SSH_KEY_PATH="~/.ssh/id_rsa"               # path to your SSH key
```

### Step 2: Run the Migration

```bash
cd vivid_mas
./scripts/migrate-to-droplet.sh
```

The script will:
- ✅ Test SSH connection
- ✅ Create remote directories
- ✅ Transfer all files
- ✅ Set proper permissions
- ✅ Restart n8n container

---

## 🔧 **Option 2: Manual SCP Transfer**

### Step 1: Transfer Files

```bash
# Replace YOUR_DROPLET_IP with your actual IP
DROPLET_IP="YOUR_DROPLET_IP"

# Create remote directory
ssh root@$DROPLET_IP "mkdir -p /root/vivid_mas/n8n/shared/knowledge"

# Transfer knowledge base files
scp vivid_mas/n8n/shared/knowledge/* root@$DROPLET_IP:/root/vivid_mas/n8n/shared/knowledge/

# Set permissions
ssh root@$DROPLET_IP "chmod -R 755 /root/vivid_mas/n8n/shared/"
```

### Step 2: Restart n8n

```bash
ssh root@$DROPLET_IP "cd /root/vivid_mas && docker-compose restart n8n"
```

---

## 📁 **Option 3: Manual Upload via SFTP**

### Step 1: Connect via SFTP

```bash
sftp root@YOUR_DROPLET_IP
```

### Step 2: Navigate and Upload

```bash
# Navigate to the correct directory
cd /root/vivid_mas/n8n/shared/knowledge

# Upload files
put vivid_mas/n8n/shared/knowledge/vividwalls-q&a.csv
put "vivid_mas/n8n/shared/knowledge/V3 Local Agentic RAG AI Agent.json"
put "vivid_mas/n8n/shared/knowledge/Enhanced-VividWalls-CopilotKit-Workflow.json"

# Exit SFTP
quit
```

### Step 3: Set Permissions and Restart

```bash
ssh root@YOUR_DROPLET_IP "chmod -R 755 /root/vivid_mas/n8n/shared/ && cd /root/vivid_mas && docker-compose restart n8n"
```

---

## 🔍 **Verification Steps**

After migration, verify the files are in place:

```bash
# Check files exist on droplet
ssh root@YOUR_DROPLET_IP "ls -la /root/vivid_mas/n8n/shared/knowledge/"

# Should show:
# - vividwalls-q&a.csv
# - V3 Local Agentic RAG AI Agent.json  
# - Enhanced-VividWalls-CopilotKit-Workflow.json
```

## 📊 **Files Being Transferred**

| File | Purpose | Size |
|------|---------|------|
| `vividwalls-q&a.csv` | Knowledge base with Q&A data | ~6.5KB |
| `V3 Local Agentic RAG AI Agent.json` | Original n8n workflow | ~40KB |
| `Enhanced-VividWalls-CopilotKit-Workflow.json` | Enhanced workflow with CopilotKit integration | ~15KB |

## 🎯 **Next Steps After Migration**

1. **Import Workflow into n8n**:
   - Access n8n at `https://YOUR_DROPLET_IP:5678`
   - Import `Enhanced-VividWalls-CopilotKit-Workflow.json`
   - Activate the workflow

2. **Configure OpenAI Credentials**:
   - Add OpenAI API key in n8n credentials
   - Update workflow nodes to use the credentials

3. **Test the Webhook**:
   ```bash
   curl -X POST https://n8n.vividwalls.blog/webhook/vividwalls-copilot \
     -H "Content-Type: application/json" \
     -d '{"chatInput": "test", "sessionId": "test"}'
   ```

4. **Install WordPress Plugin**:
   - Upload the plugin files to your WordPress site
   - Configure the webhook URL in plugin settings

## 🚨 **Troubleshooting**

### SSH Connection Issues
```bash
# Test SSH connection
ssh -v root@YOUR_DROPLET_IP

# If using a different SSH key
ssh -i /path/to/your/key root@YOUR_DROPLET_IP
```

### Permission Issues
```bash
# Fix permissions on droplet
ssh root@YOUR_DROPLET_IP "chown -R 1000:1000 /root/vivid_mas/n8n/shared/"
```

### n8n Not Reading Files
```bash
# Check Docker volume mount
ssh root@YOUR_DROPLET_IP "docker exec -it n8n ls -la /data/shared/knowledge/"

# Restart n8n if needed
ssh root@YOUR_DROPLET_IP "cd /root/vivid_mas && docker-compose restart n8n"
```

---

## 📞 **Need Help?**

If you encounter issues:
1. Check the migration script output for specific errors
2. Verify your SSH key has access to the droplet
3. Ensure the droplet path exists and is writable
4. Check Docker container logs: `docker logs n8n`

**Ready to migrate?** Choose your preferred option above and get your VividWalls AI assistant running on your Digital Ocean Droplet! 🚀 