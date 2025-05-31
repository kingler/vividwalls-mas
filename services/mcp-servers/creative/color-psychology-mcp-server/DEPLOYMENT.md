# Color Psychology MCP Server Deployment Guide

## Overview
This guide explains how to deploy the Color Psychology MCP Server for use with the n8n workflow.

## Requirements
- Python 3.9+
- PostgreSQL with pgvector extension (already configured)
- Access to VividWalls database
- Network connectivity between n8n and MCP server

## Local Development Setup

### 1. Install Dependencies
```bash
cd services/mcp-servers/creative/color-psychology-mcp-server
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your actual values:
# - Database connection string
# - OpenAI API key (if using Vision features)
```

### 3. Run the Server
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or using the main.py entry point
python main.py
```

### 4. Test the Endpoint
```bash
# Test health check
curl http://localhost:8000/health

# Test analyze endpoint
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/tmp/test_image.jpg"}'
```

## Production Deployment (on DigitalOcean Droplet)

### 1. Create Systemd Service
```bash
sudo nano /etc/systemd/system/color-psychology-mcp.service
```

```ini
[Unit]
Description=VividWalls Color Psychology MCP Server
After=network.target

[Service]
Type=simple
User=vivid
WorkingDirectory=/home/vivid/vivid_mas/services/mcp-servers/creative/color-psychology-mcp-server
Environment="PATH=/home/vivid/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable color-psychology-mcp
sudo systemctl start color-psychology-mcp
sudo systemctl status color-psychology-mcp
```

### 3. Configure Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name mcp.vividwalls.blog;

    location /color-psychology/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }
}
```

## Docker Deployment (Alternative)

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### 2. Add to docker-compose.yml
```yaml
color-psychology-mcp:
  build: ./services/mcp-servers/creative/color-psychology-mcp-server
  container_name: color-psychology-mcp
  ports:
    - "8000:8000"
  environment:
    - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/vividwalls
    - PORT=8000
  depends_on:
    - postgres
  restart: unless-stopped
```

## n8n Workflow Configuration

### Update Workflow URLs
1. Open the n8n workflow `VividWalls-Artwork-Color-Analysis-MCP.json`
2. Update the "Call Color Psychology MCP Agent" node:
   - Development: `http://localhost:8000/analyze`
   - Production: `http://mcp.vividwalls.blog/color-psychology/analyze`
   - Docker: `http://color-psychology-mcp:8000/analyze`

### Test the Integration
```bash
# Send test request to n8n webhook
curl -X POST https://n8n.vividwalls.blog/webhook/artwork-color-analysis-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "artworkId": "test-001",
    "title": "Test Artwork",
    "collection": "Test Collection",
    "imageUrl": "https://cdn.shopify.com/s/files/1/0270/2098/3788/files/test.jpg"
  }'
```

## Monitoring

### View Logs
```bash
# Systemd logs
sudo journalctl -u color-psychology-mcp -f

# Docker logs
docker logs -f color-psychology-mcp
```

### Health Checks
```bash
# Check if service is running
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/health/db
```

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'fastmcp'**
   - The server gracefully falls back to vanilla FastAPI
   - This is expected in development without the enterprise package

2. **Database Connection Failed**
   - Verify DATABASE_URL in .env
   - Check pgvector extension is installed
   - Ensure network connectivity to PostgreSQL

3. **Image Processing Errors**
   - Check file permissions for /tmp directory
   - Verify PIL/Pillow is installed correctly
   - Ensure sufficient disk space for image processing

### Performance Optimization

1. **Enable Response Caching**
   - Add Redis for caching color analysis results
   - Cache embeddings to reduce API calls

2. **Batch Processing**
   - Use the bulk endpoint for multiple images
   - Implement queue system for large batches

3. **Resource Limits**
   - Set appropriate memory limits in Docker
   - Configure worker processes for concurrent requests

## Security Considerations

1. **API Authentication**
   - Implement API key authentication for production
   - Use environment variables for sensitive data

2. **Input Validation**
   - Validate image file types and sizes
   - Sanitize file paths to prevent directory traversal

3. **Network Security**
   - Use HTTPS for all external endpoints
   - Restrict access to internal services

## Integration with Other Agents

The Color Psychology MCP Server can be accessed by:
- **Color Palette Agent**: For artwork recommendations
- **Sales Agent**: For personalized suggestions
- **Customer Relationship Agent**: For preference tracking

Each agent can call the MCP server through:
- Direct HTTP requests to the `/analyze` endpoint
- n8n workflow integration
- Future: Native MCP protocol integration 