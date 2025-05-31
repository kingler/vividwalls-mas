# MCP Server Deployment Template

## For Each New MCP Server:

### 1. Port Assignment
- Color Psychology: 8001
- Sales Agent: 8002  
- Customer Relationship: 8003
- [Next Agent]: 8004+

### 2. Systemd Service Template
```bash
[Unit]
Description=VividWalls [Agent Name] MCP Server
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/vivid/vivid_mas/services/mcp-servers/[category]/[agent-name]-mcp-server
Environment="PATH=/home/vivid/vivid_mas/services/mcp-servers/[category]/[agent-name]-mcp-server/venv/bin:/usr/bin"
ExecStart=/home/vivid/vivid_mas/services/mcp-servers/[category]/[agent-name]-mcp-server/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Environment Variables (.env)
```
DATABASE_URL=postgresql://postgres:Vividwalls2024!@localhost:5433/vividwalls
HOST=0.0.0.0
PORT=800X
ENVIRONMENT=production
LOG_LEVEL=info
```

### 4. n8n Integration
In n8n workflows, use the **Function** node with:
```javascript
const serviceConfig = {
  "color_psychology": "http://host.docker.internal:8001",
  "sales_agent": "http://host.docker.internal:8002",
  "customer_relationship": "http://host.docker.internal:8003"
};

const mcpServer = serviceConfig[items[0].json.agent_type];
const endpoint = items[0].json.endpoint || '/analyze';

return {
  url: `${mcpServer}${endpoint}`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: items[0].json.payload
};
```

### 5. Health Monitoring
Each MCP server should expose `/health` endpoint for monitoring. 