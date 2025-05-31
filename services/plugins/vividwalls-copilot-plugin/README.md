# VividWalls WordPress Frontend Copilot Experience

A comprehensive AI-powered WordPress plugin that provides personalized art recommendations through an advanced copilot interface with masonry grid layouts, integrated WordPress content management, and seamless n8n workflow integration.

## 🎨 Features

### Frontend Copilot Interface
- **AI-Powered Chat Interface**: Interactive AI assistant for personalized art recommendations
- **Image Upload & Analysis**: Room photo analysis using advanced AI vision
- **Style Preference Engine**: Quick filter tags and detailed preference collection
- **Real-time Recommendations**: Dynamic artwork suggestions based on user input

### Standalone Recommendations Page
- **Masonry Grid Layout**: Beautiful, responsive CSS Grid masonry display
- **Advanced Filtering**: Price, size, style, and color filtering options
- **Interactive Cards**: Hover effects, quick view, and social sharing
- **Progressive Loading**: Infinite scroll and lazy loading for performance
- **Mobile Responsive**: Fully optimized for all device sizes

### WordPress Content Integration
- **MCP Server Integration**: Seamless WordPress content management through MCP tools
- **Dynamic Content Creation**: Auto-generated blog posts, artist spotlights, and guides
- **Customer Story Features**: Automated customer success story creation
- **SEO Optimization**: Built-in SEO optimization for all generated content

### n8n Workflow Integration
- **Enhanced Sales Agent**: WordPress-integrated sales workflow with content capabilities
- **Real-time Content Generation**: Create blog content during customer conversations
- **Analytics Integration**: Advanced analytics for content performance and sales correlation
- **Multi-Agent Coordination**: Seamless communication between sales and content agents

## 📁 Project Structure

```
vividwalls-copilot-plugin/
├── vividwalls-copilot.php                 # Main plugin file
├── vividwalls-recommendations-page.php    # Standalone recommendations page
├── assets/
│   ├── vividwalls-copilot.css            # Original copilot styles
│   ├── vividwalls-copilot-enhanced.js    # Enhanced copilot functionality
│   ├── vividwalls-recommendations.css    # Masonry grid styles
│   └── vividwalls-recommendations.js     # Recommendations page logic
└── README.md                             # This documentation
```

## 🚀 Installation & Setup

### Prerequisites
- WordPress 5.0 or higher
- PHP 7.4 or higher
- MySQL 5.7 or higher
- n8n workflow platform
- VividWalls MCP servers (WordPress, Shopify, Pictorem)

### Plugin Installation

1. **Download and Install Plugin**
   ```bash
   # Upload the plugin folder to your WordPress plugins directory
   cp -r vividwalls-copilot-plugin /path/to/wordpress/wp-content/plugins/
   ```

2. **Activate Plugin**
   - Go to WordPress Admin → Plugins
   - Find "VividWalls AI Sales Agent"
   - Click "Activate"

3. **Configure Plugin Settings**
   - Go to Settings → VividWalls AI
   - Configure n8n webhook URLs
   - Set position and theme preferences
   - Test connection status

### n8n Workflow Setup

1. **Import Enhanced Sales Agent Workflow**
   ```bash
   # Import the enhanced WordPress workflow
   curl -X POST http://localhost:5678/api/v1/workflows \
     -H "Content-Type: application/json" \
     -d @services/n8n/workflows/VividWalls-Sales-Agent-WordPress-Enhanced.json
   ```

2. **Configure Environment Variables**
   ```env
   WORDPRESS_URL=https://your-wordpress-site.com
   WORDPRESS_USERNAME=your-wp-username
   WORDPRESS_PASSWORD=your-application-password
   ```

3. **Deploy WordPress MCP Server**
   ```bash
   cd services/mcp-servers/core/wordpress-mcp-server
   npm install
   npm run build
   # Configure with your WordPress credentials
   ```

## 🎯 Usage Guide

### Creating the Recommendations Page

Use the WordPress MCP server to create a complete recommendations page:

```javascript
// Example MCP tool call
{
  "tool": "create-recommendation-page",
  "arguments": {
    "page_title": "Discover Your Perfect Art",
    "hero_title": "AI-Curated Art Recommendations",
    "hero_subtitle": "Let our advanced AI help you find the perfect pieces for your space",
    "enable_image_upload": true,
    "enable_style_filters": true,
    "n8n_webhook_url": "http://localhost:5678/webhook/sales-chat-wordpress",
    "analytics_tracking": true
  }
}
```

### Using Shortcodes

Embed recommendations anywhere with the shortcode system:

```html
<!-- Basic shortcode -->
[vividwalls_recommendations]

<!-- Advanced configuration -->
[vividwalls_recommendations 
  layout="grid" 
  items="9" 
  theme="minimal" 
  filters="true" 
  auto_load="false"]
```

### Copilot Interface Integration

The copilot automatically integrates with your site:

```php
// Add to any post or page
echo do_shortcode('[vividwalls_copilot position="inline" theme="default"]');
```

## 🔧 Configuration Options

### Plugin Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Enable Copilot | Show/hide the AI assistant | Enabled |
| Position | Copilot button position | Bottom Right |
| Theme | Visual theme (default/dark/minimal) | Default |
| n8n Chat Webhook | URL for chat processing | Required |
| n8n Image Webhook | URL for image analysis | Optional |

### Masonry Grid Options

| Option | Description | Values |
|--------|-------------|--------|
| Layout | Display layout | grid, list, carousel |
| Items per Page | Number of recommendations | 6, 9, 12, 15 |
| Theme | Visual styling | default, minimal, dark |
| Filters | Enable filter controls | true, false |
| Auto Load | Load recommendations immediately | true, false |

### MCP Server Configuration

```env
# WordPress Connection
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Optional: Custom endpoints
WORDPRESS_REST_BASE=/wp-json/wp/v2
WORDPRESS_TIMEOUT=30000
```

## 🎨 Customization

### CSS Customization

Override styles in your theme:

```css
/* Customize recommendation cards */
.recommendation-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

/* Customize masonry grid spacing */
.recommendations-grid {
  gap: 40px;
}

/* Custom color scheme */
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-accent-color;
}
```

### JavaScript Hooks

Extend functionality with custom events:

```javascript
// Listen for recommendation events
document.addEventListener('vividwalls:recommendations:loaded', function(event) {
  console.log('Recommendations loaded:', event.detail.items);
});

// Custom recommendation processing
window.VividWallsRecommendations.customProcessor = function(data) {
  // Your custom logic here
  return processedData;
};
```

### WordPress Hooks

Customize server-side behavior:

```php
// Filter recommendation results
add_filter('vividwalls_recommendations_response', function($response) {
  // Modify response data
  return $response;
});

// Add custom recommendation sources
add_action('vividwalls_get_recommendations', function($request) {
  // Your custom recommendation logic
});
```

## 🔄 Workflow Integration

### Sales Agent Enhanced Features

The WordPress-enhanced sales agent provides:

- **Real-time Content Creation**: Generate blog posts during conversations
- **Customer Story Automation**: Create customer feature stories
- **SEO Content Integration**: Link recommendations to relevant blog content
- **Analytics Integration**: Track content performance vs. sales

### Content Marketing Automation

Automatic content creation based on:

- Customer questions → Educational blog posts
- Art interest → Artist spotlight features
- Room design queries → Styling guides
- Purchase success → Customer case studies

### Multi-Agent Coordination

The system coordinates between:

- **Sales Agent**: Customer interaction and recommendations
- **Content Agent**: Blog post and content creation
- **Business Manager**: Analytics and strategy optimization
- **Marketing Agent**: Campaign creation and social media

## 📊 Analytics & Performance

### Key Metrics Tracked

- **Conversion Metrics**
  - Chat engagement rate: >20%
  - Content click-through rate: >15%
  - Blog-to-purchase conversion: >8%
  - Overall conversion rate: >4.0%

- **Content Performance**
  - Blog post engagement
  - Customer story interactions
  - Artist spotlight views
  - SEO content effectiveness

- **User Experience**
  - Page load times
  - Image analysis speed
  - Recommendation accuracy
  - Customer satisfaction scores

### Performance Optimization

- **Lazy Loading**: Images load as needed
- **Progressive Enhancement**: Works without JavaScript
- **Caching**: Intelligent recommendation caching
- **CDN Integration**: Optimized asset delivery

## 🛠️ Troubleshooting

### Common Issues

**1. Recommendations Not Loading**
```bash
# Check n8n webhook connectivity
curl -X POST http://localhost:5678/webhook/sales-chat-wordpress \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "customer_id": "test"}'
```

**2. WordPress MCP Connection Failed**
```bash
# Test WordPress credentials
curl -u username:password \
  https://your-site.com/wp-json/wp/v2/users/me
```

**3. Image Upload Issues**
- Check file size limits (max 5MB)
- Verify supported formats (JPEG, PNG, WebP)
- Ensure proper upload permissions

**4. Masonry Grid Layout Issues**
```javascript
// Manually trigger masonry layout
jQuery('#recommendations-grid').masonry('layout');
```

### Debug Mode

Enable debug mode for detailed logging:

```php
// Add to wp-config.php
define('VIVIDWALLS_DEBUG', true);

// Check debug logs
tail -f wp-content/debug.log | grep "VividWalls"
```

## 🔒 Security Considerations

### Data Protection
- All customer data encrypted in transit
- Secure WordPress Application Password authentication
- Rate limiting on AI API calls
- Input sanitization and validation

### Privacy Compliance
- GDPR-compliant data handling
- User consent for image analysis
- Data retention policies
- Cookie consent integration

## 🚀 Deployment Guide

### Production Deployment

1. **Environment Setup**
   ```bash
   # Production environment variables
   export WORDPRESS_URL=https://production-site.com
   export N8N_WEBHOOK_URL=https://n8n.yourdomain.com/webhook/
   export MCP_SERVER_URL=https://mcp.yourdomain.com
   ```

2. **Performance Optimization**
   ```bash
   # Enable caching
   wp plugin install wp-rocket --activate
   
   # Optimize images
   wp plugin install smush --activate
   
   # CDN setup
   wp plugin install cloudflare --activate
   ```

3. **Monitoring Setup**
   ```bash
   # Add performance monitoring
   wp plugin install query-monitor --activate
   
   # Error tracking
   wp plugin install wp-sentry --activate
   ```

### Scaling Considerations

- **CDN Integration**: Serve assets from CDN
- **Database Optimization**: Index recommendation queries
- **Caching Strategy**: Redis/Memcached for recommendations
- **Load Balancing**: Multiple n8n instances if needed

## 📚 API Reference

### WordPress REST API Extensions

```http
POST /wp-json/vividwalls/v1/recommendations
GET /wp-json/vividwalls/v1/analytics
POST /wp-json/vividwalls/v1/preferences
```

### n8n Webhook Endpoints

```http
POST /webhook/sales-chat-wordpress
POST /webhook/wordpress-content-analytics
POST /webhook/recommendation-feedback
```

### MCP Server Tools

- `create-recommendation-page`: Generate complete recommendation pages
- `create-recommendation-shortcode`: Create embeddable recommendation widgets
- `create-art-spotlight`: Generate artist feature content
- `search-content`: Find relevant existing content
- `optimize-seo`: Enhance content for search engines

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create feature branches
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review n8n workflow logs
- Test MCP server connectivity

---

**VividWalls WordPress Frontend Copilot Experience** - Transforming art discovery through intelligent AI integration and seamless WordPress content management.