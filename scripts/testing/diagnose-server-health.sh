#!/bin/bash

# Server Health Diagnostic Script
# Run this when SSH is working to check server health

echo "🔍 VividMAS Server Health Check"
echo "================================"
echo ""

echo "📊 System Information:"
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo ""

echo "💾 Memory Usage:"
free -h
echo ""

echo "💽 Disk Usage:"
df -h
echo ""

echo "🔥 CPU Load:"
top -bn1 | head -5
echo ""

echo "🐳 Docker Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "🔌 Network Connections:"
netstat -tuln | grep -E ':22|:80|:443|:5678|:3000|:8080'
echo ""

echo "📝 SSH Connections:"
who
echo ""

echo "🔍 SSH Process Status:"
ps aux | grep sshd | head -5
echo ""

echo "📊 System Load Average:"
cat /proc/loadavg
echo ""

echo "🔧 SSH Service Status:"
systemctl status ssh --no-pager
echo ""

echo "🐳 Docker Compose Services:"
cd /home/vivid/vivid_mas
docker-compose ps
echo ""

echo "📈 Top Processes by CPU:"
ps aux --sort=-%cpu | head -10
echo ""

echo "📈 Top Processes by Memory:"
ps aux --sort=-%mem | head -10
echo ""

echo "🔍 Recent SSH Logs:"
journalctl -u ssh --since "10 minutes ago" --no-pager | tail -10
echo ""

echo "✅ Health check complete!"
echo ""
echo "🔧 If issues found, try:"
echo "  - Restart SSH: sudo systemctl restart ssh"
echo "  - Restart Docker: docker-compose restart"
echo "  - Free memory: docker system prune -f"
echo "  - Reboot server: sudo reboot" 