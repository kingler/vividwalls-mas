# VividWalls n8n Workflow Import Guide

## 🚀 Quick Start

All workflow files have been transferred to your droplet at:
```
/home/vivid/vivid_mas/n8n/workflows/import/
```

**n8n Dashboard**: https://n8n.vividwalls.blog

## 📥 Import Process

### Step 1: Access n8n
1. Open https://n8n.vividwalls.blog in your browser
2. You should see the n8n interface (version 1.93.0)

### Step 2: Import Each Workflow
For each workflow file:
1. Click **"+ Add workflow"** or go to an existing workflow
2. Click the **"⋯"** menu (three dots) in the top right
3. Select **"Import from file"**
4. Either:
   - Upload the JSON file from your local machine, OR
   - Copy the content from the files on your droplet and paste it

## 🔧 Workflows to Import

### 1. ✨ Enhanced VividWalls CopilotKit Workflow
- **File**: `Enhanced-VividWalls-CopilotKit-Workflow.json`
- **Purpose**: WordPress CopilotKit integration with AI image analysis
- **Webhook URL**: `/vividwalls-copilot`
- **Features**:
  - Image analysis for room recommendations
  - Art recommendation engine
  - Q&A assistant
  - Knowledge base integration

### 2. 🔗 VividWalls Prompt Chain Image Retrieval
- **File**: `VividWalls-Prompt-Chain-Image-Retrieval.json`
- **Purpose**: Advanced prompt chain with workflow bifurcation
- **Webhook URL**: `/prompt-chain-retrieval`
- **Features**:
  - Multi-step AI processing
  - Database query preparation
  - Workflow bifurcation for complex analysis
  - Response aggregation

### 3. 🗄️ VividWalls Database Integration
- **File**: `VividWalls-Database-Integration-Workflow.json`
- **Purpose**: Database search with multiple query methods
- **Webhook URL**: `/vividwalls-database-search`
- **Features**:
  - Vector similarity search
  - Tag-based search
  - Category & collection search
  - Color-based search
  - Multi-criteria search
  - **⚠️ Requires PostgreSQL credentials**

### 4. 💬 Simple Chatbot Workflow
- **File**: `chatbot-workflow.json`
- **Purpose**: Basic WordPress chatbot with OpenAI
- **Webhook URL**: `/chatbot`
- **Features**:
  - Simple Q&A functionality
  - **⚠️ Requires OpenAI API credentials**

## 🔑 Required Credentials Setup

### OpenAI API Credentials
1. In n8n, go to **Settings** → **Credentials**
2. Click **"+ Add Credential"**
3. Select **"OpenAI"**
4. Enter your OpenAI API key
5. Name it: `openai-credentials`

### PostgreSQL Database Credentials
1. In n8n, go to **Settings** → **Credentials**
2. Click **"+ Add Credential"**
3. Select **"Postgres"**
4. Configure connection:
   ```
   Host: localhost (or 157.230.13.13)
   Port: 5432
   Database: postgres
   Username: postgres
   Password: [your secure postgres password]
   ```
5. Name it: `vividwalls-postgres`

## 🧪 Testing Workflows

### Test CopilotKit Workflow
```bash
curl -X POST https://n8n.vividwalls.blog/webhook/vividwalls-copilot \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "I need artwork for my modern living room with blue accents",
    "sessionId": "test_session_123",
    "source": "wordpress",
    "page_url": "https://vividwalls.blog/test"
  }'
```

### Test Database Integration
```bash
curl -X POST https://n8n.vividwalls.blog/webhook/vividwalls-database-search \
  -H "Content-Type: application/json" \
  -d '{
    "originalInquiry": "modern abstract art for office",
    "queryType": "hybrid",
    "searchParameters": {
      "primaryTags": ["modern", "abstract"],
      "roomTypes": ["office"],
      "moodClassifications": ["professional"]
    },
    "sessionId": "test_db_search",
    "userId": "test_user"
  }'
```

### Test Simple Chatbot
```bash
curl -X POST https://n8n.vividwalls.blog/webhook/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What types of artwork do you offer for bedrooms?"
  }'
```

## 🔧 Workflow Configuration Notes

### Database Integration Workflow
- **PostgreSQL Connection**: Must point to your VividWalls database
- **Tables Required**: 
  - `products`
  - `product_analysis`
  - `product_images`
  - `product_variants`
  - `product_tags`
  - `tags`
  - `product_embeddings`
- **Functions Required**: `search_products_multi_criteria()`

### CopilotKit Workflow
- **Knowledge Base**: Uses `/data/shared/knowledge/vividwalls-q&a.csv`
- **Image Analysis**: Requires OpenAI GPT-4 Vision
- **CORS**: Configured for `vividwalls.blog` domains

### Prompt Chain Workflow
- **Bifurcation**: Calls other workflows via HTTP requests
- **AI Models**: Uses GPT-4 Turbo for analysis
- **Response Aggregation**: Combines multiple workflow results

## 🌐 Integration with WordPress

### CopilotKit Integration
Add to your WordPress theme or plugin:
```javascript
const response = await fetch('https://n8n.vividwalls.blog/webhook/vividwalls-copilot', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    chatInput: userMessage,
    sessionId: sessionId,
    source: 'wordpress',
    page_url: window.location.href
  })
});
```

### Database Search Integration
```javascript
const searchResults = await fetch('https://n8n.vividwalls.blog/webhook/vividwalls-database-search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    originalInquiry: searchQuery,
    queryType: 'hybrid',
    userId: userId,
    sessionId: sessionId
  })
});
```

## 📊 Monitoring & Analytics

### Workflow Execution Logs
- Check n8n execution history for each workflow
- Monitor webhook response times
- Track error rates and success metrics

### Database Query Logging
- The database integration workflow logs all searches
- Check `search_queries` table for analytics
- Monitor search patterns and user behavior

## 🚨 Troubleshooting

### Common Issues
1. **Credentials Not Found**: Ensure credential names match exactly
2. **Database Connection Failed**: Check PostgreSQL credentials and network access
3. **OpenAI API Errors**: Verify API key and rate limits
4. **Webhook 404 Errors**: Ensure workflows are active and saved

### Debug Steps
1. Check workflow execution logs in n8n
2. Test individual nodes in workflows
3. Verify credential configurations
4. Check network connectivity between services

## 🎯 Next Steps

1. **Import all workflows** using the n8n web interface
2. **Configure credentials** for OpenAI and PostgreSQL
3. **Test each workflow** with the provided sample requests
4. **Integrate with WordPress** using the webhook URLs
5. **Monitor performance** and optimize as needed

## 📚 Additional Resources

- **n8n Documentation**: https://docs.n8n.io/
- **OpenAI API Docs**: https://platform.openai.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **VividWalls Database Schema**: See `supabase-vividwalls-schema.sql`

---

**🔗 Quick Links**:
- n8n Dashboard: https://n8n.vividwalls.blog
- WordPress Site: https://vividwalls.blog
- Database: PostgreSQL on droplet (port 5432) 