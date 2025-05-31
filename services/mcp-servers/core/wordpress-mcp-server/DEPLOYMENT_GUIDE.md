# WordPress MCP Server Deployment Guide

This guide covers the complete deployment and configuration of the WordPress MCP Server for VividWalls' Art of Space blog automation.

## Prerequisites

### WordPress Site Requirements
- WordPress 5.0+ with REST API enabled
- HTTPS enabled (required for security)
- Application Password support enabled
- User account with appropriate permissions

### System Requirements
- Node.js 18.0 or higher
- npm or yarn package manager
- Git (for version control)
- SSL certificates for production

## Step 1: WordPress Configuration

### 1.1 Enable REST API
Most WordPress installations have the REST API enabled by default. Verify by visiting:
```
https://your-wordpress-site.com/wp-json/wp/v2/
```

You should see a JSON response with API information.

### 1.2 Create Application Password

1. **Login to WordPress Admin**
   - Go to Users → Your Profile
   - Scroll to "Application Passwords" section

2. **Generate Application Password**
   - Application Name: "VividWalls MCP Server"
   - Click "Add New Application Password"
   - **Important**: Copy the generated password immediately - you won't see it again!

3. **Format**: Application passwords are formatted as: `xxxx xxxx xxxx xxxx xxxx xxxx`

### 1.3 Set User Permissions

Ensure your user account has these capabilities:
```
Core Permissions:
- read
- edit_posts
- publish_posts
- delete_posts
- edit_pages
- publish_pages
- delete_pages
- upload_files
- edit_files

Taxonomy Permissions:
- manage_categories
- assign_categories
- manage_tags
- assign_tags

User Management:
- list_users
- edit_users (optional)

Site Management:
- manage_options (for site settings)
- customize (for theme management)
```

## Step 2: Server Installation

### 2.1 Clone and Setup
```bash
# Navigate to MCP directory
cd /Users/kinglerbercy/Projects/vivid_mas/mcp

# Verify WordPress MCP server exists
ls -la wordpress-mcp-server/

# Install dependencies
cd wordpress-mcp-server
npm install
```

### 2.2 Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 2.3 Required Environment Variables
```env
# WordPress Connection
WORDPRESS_URL=https://vividwalls.com
WORDPRESS_USERNAME=your-admin-username
WORDPRESS_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Optional Performance Settings
WORDPRESS_TIMEOUT=30000
WORDPRESS_RETRIES=3
WORDPRESS_USER_AGENT=VividWalls WordPress MCP Server/1.0.0

# Art of Space Branding
ART_OF_SPACE_BRAND=Art of Space
ART_OF_SPACE_TAGLINE=Curated Art for Your Space
ART_OF_SPACE_CONTACT_EMAIL=hello@vividwalls.com
ART_OF_SPACE_WEBSITE=https://vividwalls.com/art-of-space

# Content Defaults
DEFAULT_AUTHOR_ID=1
DEFAULT_CATEGORY_ID=1
DEFAULT_POST_STATUS=draft
DEFAULT_COMMENT_STATUS=open
DEFAULT_PING_STATUS=open

# SEO Configuration
SEO_TITLE_MAX_LENGTH=60
SEO_EXCERPT_MAX_LENGTH=155
SEO_FOCUS_KEYWORDS=art,wall art,home decor,interior design

# Social Media URLs
FACEBOOK_PAGE_URL=https://facebook.com/vividwalls
INSTAGRAM_URL=https://instagram.com/vividwalls
PINTEREST_URL=https://pinterest.com/vividwalls
TWITTER_URL=https://twitter.com/vividwalls
```

## Step 3: Build and Test

### 3.1 Build the Server
```bash
# Compile TypeScript
npm run build

# Verify build succeeded
ls -la build/
```

### 3.2 Test Connection
```bash
# Start server
npm start

# In another terminal, test health check
echo '{"method":"tools/call","params":{"name":"wordpress-health-check","arguments":{}}}' | npm start
```

Expected response:
```json
{
  "content": [
    {
      "type": "text",
      "text": "WordPress Health Check: ok\nConnected as Your Name (username)\n\nDetails: {...}"
    }
  ]
}
```

## Step 4: Integration with Claude Code

### 4.1 MCP Configuration
Add to your Claude Code MCP configuration file (`~/.claude/mcp.json`):

```json
{
  "servers": {
    "wordpress": {
      "command": "node",
      "args": ["/Users/kinglerbercy/Projects/vivid_mas/mcp/wordpress-mcp-server/build/index.js"],
      "env": {
        "WORDPRESS_URL": "https://vividwalls.com",
        "WORDPRESS_USERNAME": "your-username",
        "WORDPRESS_PASSWORD": "your-app-password"
      }
    }
  }
}
```

### 4.2 Verify Integration
1. Restart Claude Code
2. Check available tools: You should see all WordPress tools listed
3. Test with: `wordpress-health-check`

## Step 5: n8n Workflow Integration

### 5.1 Configure n8n MCP Node
```json
{
  "serverName": "wordpress",
  "tool": "create-post",
  "arguments": {
    "title": "{{ $json.title }}",
    "content": "{{ $json.content }}",
    "status": "draft",
    "categories": "{{ $json.categories }}",
    "tags": "{{ $json.tags }}"
  }
}
```

### 5.2 Create Workflow Templates

#### Content Publishing Workflow
```
Trigger (Webhook/Schedule) 
  → Content Generation (Claude)
  → WordPress Create Post (MCP)
  → Media Upload (MCP)
  → SEO Optimization (MCP)
  → Social Media Posting
  → Analytics Tracking
```

#### Art of Space Automation
```
Artist Data Input
  → Generate Artist Spotlight (MCP)
  → Upload Artist Images (MCP)
  → Schedule Publication (MCP)
  → Email Newsletter Update
  → Social Media Campaign
```

## Step 6: Content Templates Setup

### 6.1 Create WordPress Categories
```bash
# Using the MCP server
echo '{
  "method": "tools/call",
  "params": {
    "name": "create-category",
    "arguments": {
      "name": "Artist Spotlight",
      "description": "Featured artists and their remarkable artworks"
    }
  }
}' | npm start
```

### 6.2 Setup Default Tags
```bash
# Create common art tags
for tag in "contemporary art" "abstract" "landscape" "portrait" "sculpture" "photography"; do
  echo "{
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"create-tag\",
      \"arguments\": {
        \"name\": \"$tag\"
      }
    }
  }" | npm start
done
```

## Step 7: Security Configuration

### 7.1 WordPress Security
```php
// In wp-config.php - Add these constants
define('WP_POST_REVISIONS', 10);
define('AUTOSAVE_INTERVAL', 300);
define('WP_ALLOW_MULTISITE', false);

// Limit login attempts
define('WP_FAIL2BAN_LOG_SECURITY', true);
```

### 7.2 Server Security
```bash
# Set proper file permissions
chmod 600 .env
chmod 755 build/
chmod 644 build/*.js

# Restrict access
echo "node_modules/" >> .gitignore
echo ".env" >> .gitignore
```

### 7.3 Network Security
- Use HTTPS only for WordPress site
- Configure firewall rules for production
- Set up rate limiting in reverse proxy
- Monitor for suspicious API activity

## Step 8: Monitoring and Logging

### 8.1 Health Monitoring
Create a monitoring script:
```bash
#!/bin/bash
# monitor-wordpress-mcp.sh

echo "Checking WordPress MCP Server health..."
HEALTH_CHECK=$(echo '{"method":"tools/call","params":{"name":"wordpress-health-check","arguments":{}}}' | npm start)

if [[ $HEALTH_CHECK == *"ok"* ]]; then
    echo "✓ WordPress MCP Server is healthy"
    exit 0
else
    echo "✗ WordPress MCP Server health check failed"
    echo "$HEALTH_CHECK"
    exit 1
fi
```

### 8.2 Log Monitoring
```bash
# Monitor application logs
tail -f /var/log/wordpress-mcp.log

# Monitor WordPress logs
tail -f /path/to/wordpress/wp-content/debug.log
```

## Step 9: Backup and Recovery

### 9.1 Configuration Backup
```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)
cp package.json package.json.backup.$(date +%Y%m%d)

# Backup custom modifications
tar -czf wordpress-mcp-backup-$(date +%Y%m%d).tar.gz src/ build/ .env package.json
```

### 9.2 WordPress Backup
```bash
# Database backup
mysqldump -u username -p wordpress_db > wp_backup_$(date +%Y%m%d).sql

# File backup
tar -czf wp_files_backup_$(date +%Y%m%d).tar.gz /path/to/wordpress/
```

## Step 10: Performance Optimization

### 10.1 WordPress Optimization
```php
// In wp-config.php
define('WP_CACHE', true);
define('COMPRESS_CSS', true);
define('COMPRESS_SCRIPTS', true);
define('ENFORCE_GZIP', true);
```

### 10.2 MCP Server Optimization
```env
# In .env - Adjust timeouts for performance
WORDPRESS_TIMEOUT=15000
WORDPRESS_RETRIES=2
WORDPRESS_CACHE_TTL=300
```

### 10.3 Database Optimization
```sql
-- Optimize WordPress database
OPTIMIZE TABLE wp_posts;
OPTIMIZE TABLE wp_postmeta;
OPTIMIZE TABLE wp_options;
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
```bash
# Test credentials manually
curl -u username:app-password https://vividwalls.com/wp-json/wp/v2/users/me

# Check application password format
# Should be: xxxx xxxx xxxx xxxx xxxx xxxx (spaces included)
```

#### 2. Connection Timeout
```bash
# Test WordPress API availability
curl -I https://vividwalls.com/wp-json/wp/v2/

# Check SSL certificate
openssl s_client -connect vividwalls.com:443 -servername vividwalls.com
```

#### 3. Permission Denied
```bash
# Check user capabilities
wp user list --fields=ID,user_login,roles
wp cap list administrator
```

#### 4. Media Upload Failed
```bash
# Check upload directory permissions
ls -la wp-content/uploads/
stat wp-content/uploads/

# Check PHP upload limits
php -i | grep upload_max_filesize
php -i | grep post_max_size
```

### Debug Mode
```bash
# Enable debug logging
WORDPRESS_DEBUG=true npm start 2>&1 | tee debug.log

# Test specific functionality
echo '{"method":"tools/call","params":{"name":"get-posts","arguments":{"per_page":1}}}' | npm start
```

### Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 401 | Authentication failed | Check username/password |
| 403 | Permission denied | Verify user capabilities |
| 404 | Endpoint not found | Check WordPress version/plugins |
| 413 | Payload too large | Increase upload limits |
| 429 | Rate limited | Implement request throttling |
| 500 | Server error | Check WordPress error logs |

## Production Deployment

### 1. Environment Setup
```bash
# Production environment
NODE_ENV=production
WORDPRESS_TIMEOUT=10000
WORDPRESS_RETRIES=1
LOG_LEVEL=warn
```

### 2. Process Management
```bash
# Using PM2 for process management
npm install -g pm2

# Start with PM2
pm2 start build/index.js --name wordpress-mcp

# Monitor
pm2 status
pm2 logs wordpress-mcp
```

### 3. Load Balancing
```nginx
# Nginx configuration for multiple instances
upstream wordpress_mcp {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

location /mcp/ {
    proxy_pass http://wordpress_mcp;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

## Maintenance

### Regular Tasks
- **Daily**: Monitor health checks and error logs
- **Weekly**: Review performance metrics and API usage
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full backup and disaster recovery test

### Updates
```bash
# Update dependencies
npm update

# Rebuild after updates
npm run build

# Test after updates
npm test
```

---

**VividWalls WordPress MCP Server** is now ready for production use with comprehensive Art of Space blog automation capabilities.