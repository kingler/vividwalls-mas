# WordPress MCP Server

A comprehensive Model Context Protocol (MCP) server for WordPress management with specialized Art of Space blog content marketing automation. This server provides complete WordPress REST API integration with advanced content generation tools specifically designed for art businesses and content marketing.

## Features

### Core WordPress Management
- **Posts Management**: Create, read, update, delete, and schedule posts
- **Pages Management**: Full page lifecycle management
- **Media Management**: Upload, organize, and manage media files with SEO optimization
- **Categories & Tags**: Create and manage taxonomies and custom taxonomies
- **Users Management**: User account and role management
- **Site Settings**: Configure WordPress site settings
- **Content Search**: Advanced search across all content types

### Enhanced WordPress Capabilities (Inspired by server-wp-mcp)
- **API Discovery**: Automatically discover all available REST API endpoints
- **Direct Endpoint Calls**: Make calls to any WordPress REST API endpoint
- **Plugin Management**: Install, activate, deactivate, update, and delete plugins
- **Theme Management**: Install, activate, update, and delete themes
- **Custom Post Types**: Full support for custom post types and fields
- **Custom Fields (Meta)**: Create, update, and manage post meta data
- **Comments Management**: Approve, reject, spam, and moderate comments
- **Multisite Support**: Network administration for WordPress multisite
- **Gutenberg Block Editor**: Add, remove, and manipulate Gutenberg blocks

### VividWalls Art Business Optimization
- **Product Posts**: Specialized art product post creation with pricing, availability
- **Image SEO**: Automated alt text, captions, and descriptions for artwork
- **Schema Markup**: Generate structured data for art products
- **SKU Generation**: Automatic product SKU creation
- **Artist Management**: Advanced artist profile and artwork tracking
- **Inventory Integration**: Availability status and sales tracking

### Art of Space Blog Automation
- **Artist Spotlights**: Generate comprehensive artist feature posts
- **Collection Announcements**: Create new collection launch content
- **How-to Guides**: Art care, display, and maintenance guides
- **Seasonal Content**: Holiday and seasonal art collections
- **Artist Interviews**: In-depth interview post templates
- **Content Optimization**: SEO-optimized content generation

### Advanced Features
- **Bulk Operations**: Update multiple posts simultaneously
- **Content Statistics**: Post engagement and performance metrics
- **SEO Optimization**: Automated title, excerpt, and slug generation
- **Gutenberg Blocks**: Native WordPress block editor manipulation
- **Error Handling**: Comprehensive error reporting and validation
- **Health Monitoring**: Enhanced connection and capability detection
- **Multi-site Management**: WordPress network administration tools

## Installation

### Prerequisites
- Node.js 18+ 
- WordPress site with REST API enabled
- WordPress Application Password for authentication

### Setup

1. **Clone and Install**
   ```bash
   cd /Users/kinglerbercy/Projects/vivid_mas/mcp/wordpress-mcp-server
   npm install
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your WordPress credentials:
   ```env
   WORDPRESS_URL=https://your-wordpress-site.com
   WORDPRESS_USERNAME=your-username
   WORDPRESS_PASSWORD=your-application-password
   ```

3. **Build the Server**
   ```bash
   npm run build
   ```

4. **Test Connection**
   ```bash
   npm start
   # Use the wordpress-health-check tool to verify connection
   ```

## WordPress Application Password Setup

1. **Create Application Password**:
   - Go to WordPress Admin → Users → Your Profile
   - Scroll to "Application Passwords" section
   - Enter application name: "MCP WordPress Server"
   - Click "Add New Application Password"
   - Copy the generated password (you won't see it again)

2. **Configure Permissions**:
   - Ensure user has appropriate capabilities:
     - `edit_posts`, `publish_posts`, `delete_posts`
     - `edit_pages`, `publish_pages`, `delete_pages`
     - `upload_files`, `edit_files`
     - `manage_categories`, `manage_options`

## Usage

### Basic WordPress Operations

#### Health Check
```javascript
await wordpress.healthCheck()
```

#### Create a Post
```javascript
await wordpress.createPost({
  title: "My New Post",
  content: "<p>Post content with HTML support</p>",
  status: "publish",
  categories: [1, 2],
  tags: [3, 4],
  featured_media: 123
})
```

#### Upload Media
```javascript
await wordpress.uploadMedia({
  filename: "artwork.jpg",
  content: "base64-encoded-content-or-file-path",
  title: "Beautiful Artwork",
  alt_text: "Abstract painting with vibrant colors",
  post_id: 456
})
```

### Art of Space Content Generation

#### Create Artist Spotlight
```javascript
await artOfSpace.createArtSpotlight({
  artist_name: "Maria Rodriguez",
  artist_bio: "Contemporary abstract artist known for vibrant color palettes...",
  artwork_title: "Urban Dreams",
  artwork_description: "A stunning piece that captures the energy of city life...",
  artwork_year: "2024",
  artwork_medium: "Acrylic on canvas",
  artwork_dimensions: "36\" x 48\"",
  featured_image: 789,
  gallery_images: [790, 791, 792],
  artist_website: "https://mariarodriguez.art",
  price_range: "$2,500 - $3,500",
  availability: "available",
  tags: ["contemporary", "abstract", "colorful"]
})
```

#### Create Collection Announcement
```javascript
await artOfSpace.createCollectionAnnouncement({
  collection_name: "Spring Awakening",
  collection_description: "A vibrant collection celebrating renewal and growth...",
  artist_name: "Various Artists",
  launch_date: "2024-03-20T09:00:00Z",
  featured_artworks: [
    {
      title: "Bloom",
      description: "Delicate florals in soft pastels",
      image_id: 801,
      price: "$1,200"
    }
  ],
  collection_theme: "Spring renewal and natural beauty",
  featured_image: 800
})
```

#### Create How-to Guide
```javascript
await artOfSpace.createHowToGuide({
  guide_title: "Properly Lighting Your Art Collection",
  guide_type: "lighting",
  difficulty_level: "intermediate",
  time_required: "2-3 hours",
  materials_needed: ["Picture lights", "LED bulbs", "Measuring tape"],
  steps: [
    {
      step_number: 1,
      title: "Assess Your Space",
      description: "Evaluate the natural light and existing fixtures...",
      image_id: 802,
      tips: ["Avoid direct sunlight", "Consider room usage patterns"]
    }
  ],
  expert_tips: ["Use UV-filtering glass for valuable pieces"],
  featured_image: 803
})
```

## API Reference

### Core Tools

#### Health & Discovery
- `wordpress-health-check` - Enhanced connection and capability check
- `discover-endpoints` - Discover all available WordPress REST API endpoints
- `call-endpoint` - Make direct calls to any WordPress REST API endpoint

#### Posts Management
- `get-posts` - Retrieve posts with filtering
- `get-post` - Get specific post by ID
- `create-post` - Create new post
- `update-post` - Update existing post
- `delete-post` - Delete post
- `schedule-post` - Schedule future publication

#### Pages Management
- `get-pages` - Retrieve pages
- `create-page` - Create new page

#### Media Management
- `get-media` - Retrieve media files
- `upload-media` - Upload new media

#### Enhanced Plugin Management
- `get-plugins` - List all plugins
- `get-plugin` - Get specific plugin details
- `activate-plugin` - Activate a plugin
- `deactivate-plugin` - Deactivate a plugin
- `update-plugin` - Update plugin to latest version
- `delete-plugin` - Delete/uninstall plugin

#### Enhanced Theme Management
- `get-themes` - List all themes
- `get-theme` - Get specific theme details
- `get-active-theme` - Get currently active theme
- `activate-theme` - Activate a theme
- `update-theme` - Update theme to latest version
- `delete-theme` - Delete/uninstall theme

#### Custom Post Types
- `get-post-types` - List all available post types
- `get-custom-posts` - Retrieve posts from custom post type
- `create-custom-post` - Create post in custom post type

#### Custom Fields (Meta)
- `get-post-meta` - Get all custom fields for a post
- `update-post-meta` - Update custom field value

#### Gutenberg Block Editor
- `get-blocks` - Get all blocks from a post
- `add-block` - Add Gutenberg block to post
- `remove-block` - Remove block from post

#### Comments Management
- `get-comments` - Retrieve comments with filtering
- `approve-comment` - Approve pending comment
- `reject-comment` - Reject/hold comment
- `spam-comment` - Mark comment as spam

#### Taxonomies
- `get-categories` - Retrieve categories
- `create-category` - Create new category
- `get-tags` - Retrieve tags
- `create-tag` - Create new tag

#### Users & Site
- `get-users` - Retrieve users
- `get-current-user` - Get authenticated user info
- `get-site-info` - Get site settings

#### Search & Utilities
- `search-content` - Search across content types
- `bulk-update-posts` - Update multiple posts
- `get-post-stats` - Get post statistics
- `optimize-seo` - Generate SEO-optimized content

#### Multisite Management
- `get-network-sites` - List all sites in network
- `get-network-plugins` - List network-activated plugins
- `network-activate-plugin` - Network activate plugin

### VividWalls Art Business Tools

#### Product Management
- `create-product-post` - Create art product post with pricing and metadata
- `optimize-image-seo` - Optimize artwork images for SEO
- `generate-schema-markup` - Generate structured data for products

### Art of Space Content Generation Tools

#### Content Generation
- `create-art-spotlight` - Artist feature posts
- `create-collection-announcement` - Collection launches
- `create-how-to-guide` - Care and display guides
- `create-seasonal-content` - Seasonal collections
- `create-artist-interview` - Interview posts

## Content Templates

### Art Spotlight Post Structure
```
- Artist introduction and bio
- Featured artwork details
- Gallery of additional works
- Artist contact information
- Call-to-action for submissions
```

### Collection Announcement Structure
```
- Collection overview and description
- Featured pieces with descriptions
- Artist information (if applicable)
- Launch date and availability
- Related collections or artists
```

### How-to Guide Structure
```
- Guide overview (difficulty, time, materials)
- Step-by-step instructions with images
- Expert tips and best practices
- Common mistakes to avoid
- Related guides and resources
```

## Block Editor (Gutenberg) Support

The server generates content using WordPress Gutenberg blocks for:
- Rich text formatting
- Image galleries
- Quote blocks for testimonials
- Structured layouts with columns
- Custom styling classes
- Responsive design elements

## SEO Optimization

Automatic SEO features include:
- **Title Optimization**: Length-optimized titles (60 chars)
- **Meta Descriptions**: Compelling excerpts (155 chars)
- **Slug Generation**: SEO-friendly URLs
- **Image Alt Text**: Accessibility compliance
- **Structured Content**: Proper heading hierarchy
- **Internal Linking**: Cross-content connections

## Error Handling

The server provides comprehensive error handling:

```javascript
// Authentication errors
AuthenticationError: Invalid credentials or permissions

// Resource errors  
NotFoundError: Content or endpoint not found

// Validation errors
ValidationError: Invalid input data

// Network errors
WordPressError: Connection or API issues
```

## Security Features

- **Application Password Authentication**: Secure token-based auth
- **Input Validation**: Zod schema validation for all inputs
- **SQL Injection Protection**: WordPress REST API built-in protection
- **XSS Prevention**: Content sanitization
- **Rate Limiting**: Respect WordPress API limits
- **HTTPS Enforcement**: Secure connections only

## Development

### Building
```bash
npm run build    # Compile TypeScript
npm run dev      # Watch mode
npm run clean    # Clean build directory
```

### Testing
```bash
npm test         # Run test suite
npm run lint     # Code linting
npm run format   # Code formatting
```

### Debugging
```bash
# Enable debug logging
WORDPRESS_DEBUG=true npm start

# Test specific functionality
echo '{"tool":"wordpress-health-check","arguments":{}}' | npm start
```

## Integration with VividWalls

### n8n Workflow Integration
The server integrates seamlessly with n8n workflows for:
- Automated content scheduling
- Social media cross-posting
- Email marketing campaigns
- Analytics tracking
- Customer engagement flows

### Claude Code Integration
Perfect for use with Claude Code for:
- Content brainstorming and creation
- SEO optimization suggestions
- Social media content adaptation
- Marketing campaign development
- Art collection curation

### Database Integration
Works with VividWalls' database for:
- Product catalog integration
- Customer preference tracking
- Sales analytics
- Inventory management
- Customer relationship management

## Troubleshooting

### Common Issues

#### Authentication Failed
```bash
# Check credentials
curl -u username:app-password https://your-site.com/wp-json/wp/v2/users/me

# Verify application password format
# Should be: xxxx xxxx xxxx xxxx xxxx xxxx
```

#### Connection Refused
```bash
# Check WordPress REST API
curl https://your-site.com/wp-json/wp/v2/

# Verify SSL certificate
curl -k https://your-site.com/wp-json/wp/v2/
```

#### Permission Denied
```bash
# Check user capabilities in WordPress admin
# Ensure user has required permissions for operations
```

### Debug Mode
```bash
# Enable verbose logging
WORDPRESS_DEBUG=true npm start

# Test individual tools
echo '{"tool":"get-posts","arguments":{"per_page":1}}' | npm start
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-functionality`
3. Add tests for new features
4. Ensure all tests pass: `npm test`
5. Submit pull request with detailed description

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check WordPress REST API documentation
- Verify MCP protocol compliance
- Test with minimal reproduction case

---

**VividWalls WordPress MCP Server** - Empowering art businesses with intelligent content automation.