#!/bin/bash

# Import VividWalls Workflows to n8n
# This script transfers workflow files to the droplet and provides import instructions

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"

echo "🚀 Importing VividWalls Workflows to n8n"
echo "====================================="

# Step 1: Transfer workflow files to droplet
echo "📤 Transferring workflow files to droplet..."

# Create workflows directory if it doesn't exist
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} 'mkdir -p /home/vivid/vivid_mas/n8n/workflows/import'

# Transfer the workflow files
echo "📁 Transferring Enhanced-VividWalls-CopilotKit-Workflow.json..."
scp -i ~/.ssh/digitalocean n8n/backup/workflows/Enhanced-VividWalls-CopilotKit-Workflow.json ${DROPLET_USER}@${DROPLET_IP}:/home/vivid/vivid_mas/n8n/workflows/import/

echo "📁 Transferring VividWalls-Prompt-Chain-Image-Retrieval.json..."
scp -i ~/.ssh/digitalocean n8n/workflows/VividWalls-Prompt-Chain-Image-Retrieval.json ${DROPLET_USER}@${DROPLET_IP}:/home/vivid/vivid_mas/n8n/workflows/import/

echo "📁 Transferring VividWalls-Database-Integration-Workflow.json..."
scp -i ~/.ssh/digitalocean n8n/workflows/VividWalls-Database-Integration-Workflow.json ${DROPLET_USER}@${DROPLET_IP}:/home/vivid/vivid_mas/n8n/workflows/import/

echo "📁 Transferring chatbot-workflow.json..."
scp -i ~/.ssh/digitalocean n8n/workflows/chatbot-workflow.json ${DROPLET_USER}@${DROPLET_IP}:/home/vivid/vivid_mas/n8n/workflows/import/

# Set proper permissions
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas/n8n/workflows/import
chown vivid:vivid *.json
chmod 644 *.json
ls -la
EOF

echo "✅ All workflow files transferred successfully!"

# Step 2: Provide import instructions
echo ""
echo "🎯 WORKFLOW IMPORT INSTRUCTIONS"
echo "==============================="
echo ""
echo "The workflow files have been transferred to your droplet at:"
echo "📂 /home/vivid/vivid_mas/n8n/workflows/import/"
echo ""
echo "To import these workflows into n8n:"
echo ""
echo "1. 🌐 Open n8n in your browser:"
echo "   https://n8n.vividwalls.blog"
echo ""
echo "2. 📥 Import each workflow:"
echo "   a) Click the '+ Add workflow' button or go to existing workflow"
echo "   b) Click the '⋯' menu (three dots) in the top right"
echo "   c) Select 'Import from file'"
echo "   d) Upload the JSON files from your local machine or copy content"
echo ""
echo "3. 🔧 Workflows to import:"
echo "   ✨ Enhanced-VividWalls-CopilotKit-Workflow.json"
echo "      - WordPress CopilotKit integration with AI image analysis"
echo "      - Webhook: /vividwalls-copilot"
echo ""
echo "   🔗 VividWalls-Prompt-Chain-Image-Retrieval.json"
echo "      - Advanced prompt chain with workflow bifurcation"
echo "      - Webhook: /prompt-chain-retrieval"
echo ""
echo "   🗄️ VividWalls-Database-Integration-Workflow.json"
echo "      - Database search with multiple query methods"
echo "      - Webhook: /vividwalls-database-search"
echo "      - ⚠️  Requires PostgreSQL credentials setup"
echo ""
echo "   💬 chatbot-workflow.json"
echo "      - Simple WordPress chatbot with OpenAI"
echo "      - Webhook: /chatbot"
echo "      - ⚠️  Requires OpenAI API credentials"
echo ""
echo "4. 🔑 Required Credentials Setup:"
echo "   - OpenAI API Key (for AI features)"
echo "   - PostgreSQL Connection (for database workflows)"
echo ""
echo "5. 🧪 Test Webhooks:"
echo "   After import, test each webhook endpoint:"
echo "   • https://n8n.vividwalls.blog/webhook/vividwalls-copilot"
echo "   • https://n8n.vividwalls.blog/webhook/prompt-chain-retrieval"
echo "   • https://n8n.vividwalls.blog/webhook/vividwalls-database-search"
echo "   • https://n8n.vividwalls.blog/webhook/chatbot"
echo ""

# Step 3: Create sample test requests
echo "📋 SAMPLE TEST REQUESTS"
echo "======================="
echo ""
echo "Test the CopilotKit workflow:"
cat << 'COPILOT_TEST'
curl -X POST https://n8n.vividwalls.blog/webhook/vividwalls-copilot \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "I need artwork for my modern living room with blue accents",
    "sessionId": "test_session_123",
    "source": "wordpress",
    "page_url": "https://vividwalls.blog/test"
  }'
COPILOT_TEST

echo ""
echo "Test the Database Integration workflow:"
cat << 'DATABASE_TEST'
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
DATABASE_TEST

echo ""
echo "Test the Chatbot workflow:"
cat << 'CHATBOT_TEST'
curl -X POST https://n8n.vividwalls.blog/webhook/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What types of artwork do you offer for bedrooms?"
  }'
CHATBOT_TEST

echo ""
echo "🎉 Workflow Import Process Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Import the workflows in n8n web interface"
echo "2. Configure required credentials (OpenAI, PostgreSQL)"
echo "3. Test each workflow with the sample requests above"
echo "4. Integrate with your WordPress site using the webhook URLs"
echo ""
echo "🔗 n8n Dashboard: https://n8n.vividwalls.blog"
echo "📚 Workflow Documentation: Available in each workflow's notes" 