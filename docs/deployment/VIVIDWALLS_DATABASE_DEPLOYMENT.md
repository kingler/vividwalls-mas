# VividWalls Database Deployment Guide

## 🚀 **Manual Deployment Instructions**

Since GitHub push protection is blocking automated deployment due to API keys in git history, here's how to manually deploy the VividWalls database to your Digital Ocean droplet.

## 📋 **What We've Built**

### **Database Schema (`scripts/supabase-vividwalls-schema.sql`)**
- Complete PostgreSQL schema with pgvector extension
- Product catalog with variants, images, and collections
- AI analysis and classification tables
- Comprehensive tagging system with categories
- Vector embeddings for semantic search
- Room suitability analysis
- Search and recommendation functions
- Row Level Security policies

### **Data Import (`scripts/fix-csv-import.py`)**
- Python script that properly handles CSV with HTML content
- Imports 58 products, 506 variants, 513 images
- Processes collections, tags, and product relationships
- Handles multiline HTML descriptions correctly
- Creates proper JSON dimensions data

### **Deployment Script (`scripts/deploy-droplet-database.sh`)**
- Automated database setup for Digital Ocean droplet
- Checks for existing schema and offers to recreate
- Installs Python dependencies
- Runs CSV import with proper database connection
- Verifies deployment success

### **n8n Workflows**
- `VividWalls-Database-Integration-Workflow.json` - Multi-criteria search and AI enhancement
- `VividWalls-Prompt-Chain-Image-Retrieval.json` - Bifurcated prompt chain for image retrieval

## 🔧 **Manual Deployment Steps**

### **Step 1: Upload Files to Droplet**

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Navigate to project directory
cd /home/vivid/vivid_mas

# Create the scripts directory if it doesn't exist
mkdir -p scripts
```

### **Step 2: Copy Database Files**

Copy these files to your droplet in the `/home/vivid/vivid_mas/scripts/` directory:

1. **`supabase-vividwalls-schema.sql`** - Complete database schema
2. **`migrate-vividwalls-data.sql`** - Data migration script  
3. **`fix-csv-import.py`** - CSV import script
4. **`deploy-droplet-database.sh`** - Deployment automation script

### **Step 3: Copy n8n Workflows**

Copy these files to `/home/vivid/vivid_mas/n8n/workflows/`:

1. **`VividWalls-Database-Integration-Workflow.json`**
2. **`VividWalls-Prompt-Chain-Image-Retrieval.json`**

### **Step 4: Upload CSV Data**

Ensure these CSV files are in `/home/vivid/vivid_mas/n8n/data/shared/`:

1. **`vividwalls-products-list-2-23-2025.csv`** - Product catalog
2. **`vividwalls-q&a.csv`** - Q&A dataset  
3. **`vividwalls-room-analysis-qa.csv`** - Room analysis dataset (50 entries)

### **Step 5: Run Database Deployment**

```bash
# Make the deployment script executable
chmod +x scripts/deploy-droplet-database.sh

# Run the deployment script
./scripts/deploy-droplet-database.sh
```

The script will:
- ✅ Check PostgreSQL is running
- ✅ Deploy the database schema
- ✅ Install Python dependencies
- ✅ Import CSV data
- ✅ Verify deployment success

### **Step 6: Import n8n Workflows**

1. Go to https://n8n.vividwalls.blog
2. Navigate to **Workflows** → **Import from File**
3. Import both workflow JSON files
4. Activate the workflows

## 📊 **Expected Results**

After successful deployment:

```
📊 Database Status:
   Collections: 10
   Products: 58
   Variants: 506
   Images: 513
```

## 🔍 **Verification Commands**

Test the database deployment:

```bash
# Connect to database
docker exec -it vivid_mas-supabase-db-1 psql -h localhost -p 5432 -U postgres -d postgres

# Check product count
SELECT COUNT(*) FROM products;

# Check collections
SELECT name, mood_profile FROM collections LIMIT 5;

# Test search functionality
SELECT title, collection FROM products WHERE title ILIKE '%echo%' LIMIT 3;
```

## 🌐 **Integration Points**

### **n8n RAG System**
- Database integration workflows ready for RAG queries
- Vector search capabilities with pgvector
- Multi-criteria search (tags, colors, categories, room suitability)

### **Open WebUI Connection**
- Configure Open WebUI to use n8n workflows for product queries
- Vector embeddings ready for semantic search
- Room analysis Q&A dataset for contextual responses

### **MCP Server Integration**
- n8n MCP server configured for workflow automation
- Database queries accessible via MCP tools
- Ready for AI agent integration

## 🚨 **Important Notes**

1. **Environment Variables**: Ensure your droplet's `.env` file has the correct database credentials
2. **CSV Data**: The product CSV must be uploaded to the shared directory for import
3. **Permissions**: Ensure proper file permissions for scripts and data files
4. **Backup**: The deployment script creates backups before making changes

## 🎯 **Next Steps After Deployment**

1. **Test RAG Functionality**: Query the database through n8n workflows
2. **Configure Open WebUI**: Connect to n8n for product recommendations
3. **Import Additional Data**: Add more product images and descriptions
4. **Optimize Search**: Fine-tune vector embeddings and search parameters

## 📞 **Support**

If you encounter issues:
1. Check PostgreSQL container logs: `docker logs vivid_mas-supabase-db-1`
2. Verify CSV file format and location
3. Ensure all dependencies are installed
4. Check database connection settings

---

**Status**: Ready for manual deployment to Digital Ocean droplet
**Database**: PostgreSQL with pgvector, comprehensive VividWalls schema
**Data**: 58 products, 506 variants, 513 images ready for import
**Workflows**: n8n integration ready for RAG system 