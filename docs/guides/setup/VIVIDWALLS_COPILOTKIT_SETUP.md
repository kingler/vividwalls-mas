# VividWalls CopilotKit WordPress Integration Setup Guide

## 🎉 Migration Status: COMPLETED ✅

All files have been successfully transferred to the Digital Ocean droplet and the infrastructure is ready for the final setup steps.

## Current Status

### ✅ Completed Steps
- [x] DNS configuration (all subdomains working with SSL)
- [x] Knowledge base files transferred to `/home/vivid/vivid_mas/n8n/shared/knowledge/`
- [x] WordPress plugin file uploaded to server
- [x] Assets (CSS/JS) uploaded to server
- [x] n8n container restarted and accessible
- [x] Infrastructure verified and working

### 🔄 Next Steps Required
- [ ] Import Enhanced-VividWalls-CopilotKit-Workflow.json into n8n
- [ ] Configure OpenAI API credentials in n8n
- [ ] Install WordPress plugin
- [ ] Test complete integration

## Step-by-Step Completion Guide

### Step 1: Import the CopilotKit Workflow into n8n

1. **Access n8n Interface:**
   - Open: https://n8n.vividwalls.blog
   - Login with your n8n credentials

2. **Import the Enhanced Workflow:**
   - Click the "+" button to create a new workflow
   - Click the "..." menu in the top right
   - Select "Import from file"
   - The workflow file is located on the server at:
     `/home/vivid/vivid_mas/n8n/shared/knowledge/Enhanced-VividWalls-CopilotKit-Workflow.json`
   
   **Alternative method - Copy from server:**
   ```bash
   # Download the workflow file from server to import
   scp -i ~/.ssh/digitalocean root@157.230.13.13:/home/vivid/vivid_mas/n8n/shared/knowledge/Enhanced-VividWalls-CopilotKit-Workflow.json ./
   ```

3. **Activate the Workflow:**
   - After importing, click the "Active" toggle in the top right
   - The webhook endpoint will become available at: `https://n8n.vividwalls.blog/webhook/vividwalls-copilot`

### Step 2: Configure OpenAI Credentials

1. **In the n8n workflow:**
   - Find the OpenAI nodes (there should be several)
   - Click on each OpenAI node
   - Configure the credentials:
     - **API Key**: Your OpenAI API key
     - **Organization ID**: (optional) Your OpenAI organization ID

2. **Test the OpenAI Connection:**
   - Save the workflow
   - Test one of the OpenAI nodes to ensure connectivity

### Step 3: Install WordPress Plugin

1. **Copy Plugin to WordPress Directory:**
   ```bash
   # SSH into the server
   ssh -i ~/.ssh/digitalocean root@157.230.13.13
   
   # Copy plugin to WordPress plugins directory
   docker cp /home/vivid/vivid_mas/wordpress-copilotkit-plugin.php wordpress:/var/www/html/wp-content/plugins/
   
   # Copy assets to WordPress directory
   docker cp /home/vivid/vivid_mas/assets/. wordpress:/var/www/html/wp-content/plugins/vividwalls-copilot/assets/
   ```

2. **Activate Plugin in WordPress:**
   - Go to: https://vividwalls.blog/wp-admin/
   - Navigate to Plugins → Installed Plugins
   - Find "VividWalls CopilotKit Integration"
   - Click "Activate"

3. **Configure Plugin Settings:**
   - Go to Settings → VividWalls CopilotKit
   - Set the webhook URL: `https://n8n.vividwalls.blog/webhook/vividwalls-copilot`
   - Save settings

### Step 4: Add CopilotKit to Your Pages

1. **Using Shortcode:**
   ```
   [vividwalls_copilot mode="chat"]
   [vividwalls_copilot mode="sidebar"]
   [vividwalls_copilot mode="popup"]
   ```

2. **Automatic Floating Widget:**
   - The plugin automatically adds a floating chat widget to all pages
   - Can be disabled in plugin settings if needed

### Step 5: Test the Integration

1. **Test Webhook Endpoint:**
   ```bash
   curl -X POST https://n8n.vividwalls.blog/webhook/vividwalls-copilot \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, test message", "type": "text"}'
   ```

2. **Test WordPress Integration:**
   - Visit any page on https://vividwalls.blog
   - Look for the floating chat widget
   - Try sending a message
   - Test image upload functionality

## File Locations on Server

### Knowledge Base Files
```
/home/vivid/vivid_mas/n8n/shared/knowledge/
├── Enhanced-VividWalls-CopilotKit-Workflow.json  # Main CopilotKit workflow
├── vividwalls-q&a.csv                           # Knowledge base data
├── V3 Local Agentic RAG AI Agent.json           # Original workflow
├── VividWalls-Advanced-Art-Analysis-System.json  # Advanced analysis
└── VividWalls-Batch-Art-Analysis.json           # Batch processing
```

### WordPress Plugin Files
```
/home/vivid/vivid_mas/
├── wordpress-copilotkit-plugin.php              # Main plugin file
└── assets/
    ├── vividwalls-copilot.js                    # JavaScript functionality
    ├── vividwalls-copilot-enhanced.js           # Enhanced version
    └── vividwalls-copilot.css                   # Styling
```

## Integration Features

### AI Assistant Capabilities
- **Text Chat**: Natural language Q&A about VividWalls products
- **Image Analysis**: Upload room photos for AI-powered art recommendations
- **Product Recommendations**: Contextual art suggestions based on room analysis
- **Knowledge Base**: Access to curated VividWalls product information

### WordPress Integration
- **Floating Widget**: Always-accessible chat interface
- **Shortcode Support**: Embed chat in specific pages/posts
- **Multiple Modes**: Chat, sidebar, and popup display options
- **Mobile Responsive**: Optimized for all device sizes

### Technical Features
- **Real-time Chat**: WebSocket-like experience using AJAX
- **Image Upload**: Drag-and-drop and click-to-upload functionality
- **Session Management**: Maintains conversation context
- **Error Handling**: Graceful fallbacks and user feedback
- **Security**: WordPress nonces and input sanitization

## Troubleshooting

### Common Issues

1. **Webhook Returns 404:**
   - Ensure the workflow is imported and activated in n8n
   - Check that the webhook URL is correct

2. **OpenAI Errors:**
   - Verify API key is correctly configured
   - Check OpenAI account has sufficient credits
   - Ensure API key has proper permissions

3. **WordPress Plugin Not Working:**
   - Check plugin is activated
   - Verify webhook URL in plugin settings
   - Check browser console for JavaScript errors

4. **Image Upload Issues:**
   - Ensure proper file permissions on server
   - Check file size limits in WordPress/PHP
   - Verify OpenAI Vision API is working

### Debug Commands

```bash
# Check n8n container logs
ssh -i ~/.ssh/digitalocean root@157.230.13.13 "cd /home/vivid/vivid_mas && docker logs n8n --tail 50"

# Check WordPress container logs
ssh -i ~/.ssh/digitalocean root@157.230.13.13 "docker logs wordpress --tail 50"

# Test webhook endpoint
curl -I https://n8n.vividwalls.blog/webhook/vividwalls-copilot

# Check file permissions
ssh -i ~/.ssh/digitalocean root@157.230.13.13 "ls -la /home/vivid/vivid_mas/n8n/shared/knowledge/"
```

## Support Information

- **Server IP**: 157.230.13.13
- **Domain**: vividwalls.blog
- **n8n Interface**: https://n8n.vividwalls.blog
- **WordPress Admin**: https://vividwalls.blog/wp-admin/
- **SSH Access**: `ssh -i ~/.ssh/digitalocean root@157.230.13.13`

## Next Steps After Setup

1. **Content Creation**: Add more Q&A entries to the knowledge base
2. **Workflow Optimization**: Fine-tune AI responses based on user feedback
3. **Analytics**: Monitor usage and conversation patterns
4. **Expansion**: Consider adding more AI capabilities or integrations

---

**Status**: Ready for final configuration steps
**Last Updated**: May 27, 2025
**Migration**: ✅ Complete 