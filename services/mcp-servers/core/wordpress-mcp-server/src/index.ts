#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { WordPressClient } from "./WordPressClient.js";
import { ArtOfSpaceGenerators } from "./ArtOfSpaceGenerators.js";
import {
  CreatePostSchema,
  CreatePageSchema,
  UpdatePostSchema,
  MediaUploadSchema,
  CreateCategorySchema,
  CreateTagSchema,
  ArtSpotlightSchema,
  CollectionAnnouncementSchema,
  HowToGuideSchema,
  SeasonalContentSchema,
  ArtistInterviewSchema,
  WordPressError,
  AuthenticationError,
  NotFoundError,
  ValidationError
} from "./types.js";

const server = new McpServer({
  name: "wordpress-tools",
  version: "1.0.0",
});

// Environment variables validation
const WORDPRESS_URL = process.env.WORDPRESS_URL;
const WORDPRESS_USERNAME = process.env.WORDPRESS_USERNAME;
const WORDPRESS_PASSWORD = process.env.WORDPRESS_PASSWORD;

if (!WORDPRESS_URL) {
  console.error("Error: WORDPRESS_URL environment variable is required");
  process.exit(1);
}

if (!WORDPRESS_USERNAME) {
  console.error("Error: WORDPRESS_USERNAME environment variable is required");
  process.exit(1);
}

if (!WORDPRESS_PASSWORD) {
  console.error("Error: WORDPRESS_PASSWORD environment variable is required (use Application Password)");
  process.exit(1);
}

// Initialize WordPress client and generators
const wordpressClient = new WordPressClient({
  baseUrl: WORDPRESS_URL,
  username: WORDPRESS_USERNAME,
  password: WORDPRESS_PASSWORD
});

const artOfSpaceGenerators = new ArtOfSpaceGenerators(wordpressClient);

// Utility function to handle errors
function handleError(
  defaultMessage: string,
  error: unknown
): {
  content: { type: "text"; text: string }[];
  isError: boolean;
} {
  let errorMessage = defaultMessage;
  
  if (error instanceof WordPressError) {
    errorMessage = `${defaultMessage}: ${error.message}`;
  } else if (error instanceof Error) {
    errorMessage = `${defaultMessage}: ${error.message}`;
  }
  
  console.error("WordPress MCP Error:", errorMessage, error);
  
  return {
    content: [{ type: "text", text: errorMessage }],
    isError: true,
  };
}

// Format post output
function formatPost(post: any): string {
  return `
Post: ${post.title?.rendered || post.title}
ID: ${post.id}
Status: ${post.status}
Date: ${post.date}
Slug: ${post.slug}
URL: ${post.link}
Author: ${post.author}
Categories: ${Array.isArray(post.categories) ? post.categories.join(", ") : "None"}
Tags: ${Array.isArray(post.tags) ? post.tags.join(", ") : "None"}
Excerpt: ${post.excerpt?.rendered ? post.excerpt.rendered.replace(/<[^>]*>/g, '').substring(0, 150) + "..." : "No excerpt"}
  `.trim();
}

// Health Check Tool
server.tool(
  "wordpress-health-check",
  "Check WordPress connection and authentication status",
  {},
  async () => {
    try {
      const health = await wordpressClient.healthCheck();
      return {
        content: [{ 
          type: "text", 
          text: `WordPress Health Check: ${health.status}\n${health.message}\n\nDetails: ${JSON.stringify(health.details, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError("WordPress health check failed", error);
    }
  }
);

// Posts Management Tools
server.tool(
  "get-posts",
  "Retrieve WordPress posts with filtering options",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of posts per page (max 100)"),
    search: z.string().optional().describe("Search term to filter posts"),
    author: z.number().optional().describe("Author ID to filter posts"),
    categories: z.array(z.number()).optional().describe("Category IDs to filter posts"),
    tags: z.array(z.number()).optional().describe("Tag IDs to filter posts"),
    status: z.array(z.enum(["publish", "draft", "private", "future", "trash"])).optional().describe("Post statuses to include"),
    orderby: z.string().optional().default("date").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("desc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getPosts(params);
      const formattedPosts = result.posts.map(formatPost);
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} posts (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedPosts.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve posts", error);
    }
  }
);

server.tool(
  "get-post",
  "Retrieve a specific WordPress post by ID",
  {
    id: z.number().describe("Post ID to retrieve"),
  },
  async ({ id }) => {
    try {
      const post = await wordpressClient.getPost(id);
      return {
        content: [{ 
          type: "text", 
          text: `${formatPost(post)}\n\nContent:\n${post.content?.rendered || "No content"}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to retrieve post ${id}`, error);
    }
  }
);

server.tool(
  "create-post",
  "Create a new WordPress post",
  {
    title: z.string().min(1).describe("Post title"),
    content: z.string().min(1).describe("Post content (HTML allowed)"),
    status: z.enum(["publish", "draft", "private", "future"]).default("draft").describe("Post status"),
    excerpt: z.string().optional().describe("Post excerpt"),
    author: z.number().optional().describe("Author ID"),
    featured_media: z.number().optional().describe("Featured image media ID"),
    categories: z.array(z.number()).optional().describe("Category IDs"),
    tags: z.array(z.number()).optional().describe("Tag IDs"),
    date: z.string().optional().describe("Publish date (ISO format)"),
    slug: z.string().optional().describe("Post slug"),
    comment_status: z.enum(["open", "closed"]).default("open").describe("Comment status"),
    ping_status: z.enum(["open", "closed"]).default("open").describe("Ping status"),
    sticky: z.boolean().default(false).describe("Sticky post"),
    format: z.string().optional().describe("Post format"),
  },
  async (params) => {
    try {
      const postData = {
        title: { rendered: params.title },
        content: { rendered: params.content, protected: false },
        status: params.status,
        excerpt: params.excerpt ? { rendered: params.excerpt, protected: false } : undefined,
        author: params.author,
        featured_media: params.featured_media,
        categories: params.categories,
        tags: params.tags,
        date: params.date,
        slug: params.slug,
        comment_status: params.comment_status,
        ping_status: params.ping_status,
        sticky: params.sticky,
        format: params.format,
      };

      const post = await wordpressClient.createPost(postData);
      return {
        content: [{ 
          type: "text", 
          text: `Post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create post", error);
    }
  }
);

server.tool(
  "update-post",
  "Update an existing WordPress post",
  {
    id: z.number().describe("Post ID to update"),
    title: z.string().optional().describe("Post title"),
    content: z.string().optional().describe("Post content (HTML allowed)"),
    status: z.enum(["publish", "draft", "private", "future", "trash"]).optional().describe("Post status"),
    excerpt: z.string().optional().describe("Post excerpt"),
    author: z.number().optional().describe("Author ID"),
    featured_media: z.number().optional().describe("Featured image media ID"),
    categories: z.array(z.number()).optional().describe("Category IDs"),
    tags: z.array(z.number()).optional().describe("Tag IDs"),
    date: z.string().optional().describe("Publish date (ISO format)"),
    slug: z.string().optional().describe("Post slug"),
    comment_status: z.enum(["open", "closed"]).optional().describe("Comment status"),
    ping_status: z.enum(["open", "closed"]).optional().describe("Ping status"),
    sticky: z.boolean().optional().describe("Sticky post"),
    format: z.string().optional().describe("Post format"),
  },
  async (params) => {
    try {
      const { id, ...updateData } = params;
      const postData: any = {};

      if (updateData.title) postData.title = { rendered: updateData.title };
      if (updateData.content) postData.content = { rendered: updateData.content };
      if (updateData.excerpt) postData.excerpt = { rendered: updateData.excerpt };
      
      Object.assign(postData, {
        status: updateData.status,
        author: updateData.author,
        featured_media: updateData.featured_media,
        categories: updateData.categories,
        tags: updateData.tags,
        date: updateData.date,
        slug: updateData.slug,
        comment_status: updateData.comment_status,
        ping_status: updateData.ping_status,
        sticky: updateData.sticky,
        format: updateData.format,
      });

      const post = await wordpressClient.updatePost(id, postData);
      return {
        content: [{ 
          type: "text", 
          text: `Post updated successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to update post ${params.id}`, error);
    }
  }
);

server.tool(
  "delete-post",
  "Delete a WordPress post",
  {
    id: z.number().describe("Post ID to delete"),
    force: z.boolean().default(false).describe("Whether to permanently delete (bypass trash)"),
  },
  async ({ id, force }) => {
    try {
      const result = await wordpressClient.deletePost(id, force);
      return {
        content: [{ 
          type: "text", 
          text: `Post ${id} ${force ? "permanently deleted" : "moved to trash"} successfully!\n\nPrevious data:\n${formatPost(result.previous)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to delete post ${id}`, error);
    }
  }
);

server.tool(
  "schedule-post",
  "Schedule a post for future publication",
  {
    id: z.number().describe("Post ID to schedule"),
    publish_date: z.string().describe("Future publish date (ISO format)"),
  },
  async ({ id, publish_date }) => {
    try {
      const post = await wordpressClient.schedulePost(id, publish_date);
      return {
        content: [{ 
          type: "text", 
          text: `Post ${id} scheduled for publication on ${publish_date}\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to schedule post ${id}`, error);
    }
  }
);

// Pages Management Tools
server.tool(
  "get-pages",
  "Retrieve WordPress pages with filtering options",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of pages per page"),
    search: z.string().optional().describe("Search term to filter pages"),
    author: z.number().optional().describe("Author ID to filter pages"),
    parent: z.number().optional().describe("Parent page ID"),
    status: z.array(z.enum(["publish", "draft", "private", "future", "trash"])).optional().describe("Page statuses"),
    orderby: z.string().optional().default("menu_order").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("asc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getPages(params);
      const formattedPages = result.pages.map(formatPost);
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} pages (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedPages.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve pages", error);
    }
  }
);

server.tool(
  "create-page",
  "Create a new WordPress page",
  {
    title: z.string().min(1).describe("Page title"),
    content: z.string().min(1).describe("Page content (HTML allowed)"),
    status: z.enum(["publish", "draft", "private", "future"]).default("draft").describe("Page status"),
    excerpt: z.string().optional().describe("Page excerpt"),
    author: z.number().optional().describe("Author ID"),
    featured_media: z.number().optional().describe("Featured image media ID"),
    parent: z.number().default(0).describe("Parent page ID"),
    menu_order: z.number().default(0).describe("Menu order"),
    slug: z.string().optional().describe("Page slug"),
    comment_status: z.enum(["open", "closed"]).default("closed").describe("Comment status"),
    ping_status: z.enum(["open", "closed"]).default("closed").describe("Ping status"),
    template: z.string().optional().describe("Page template"),
  },
  async (params) => {
    try {
      const pageData = {
        title: { rendered: params.title },
        content: { rendered: params.content, protected: false },
        status: params.status,
        excerpt: params.excerpt ? { rendered: params.excerpt, protected: false } : undefined,
        author: params.author,
        featured_media: params.featured_media,
        parent: params.parent,
        menu_order: params.menu_order,
        slug: params.slug,
        comment_status: params.comment_status,
        ping_status: params.ping_status,
        template: params.template,
      };

      const page = await wordpressClient.createPage(pageData);
      return {
        content: [{ 
          type: "text", 
          text: `Page created successfully!\n\n${formatPost(page)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create page", error);
    }
  }
);

// Media Management Tools
server.tool(
  "get-media",
  "Retrieve WordPress media files",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of media items per page"),
    search: z.string().optional().describe("Search term to filter media"),
    author: z.number().optional().describe("Author ID to filter media"),
    parent: z.number().optional().describe("Parent post ID"),
    media_type: z.enum(["image", "video", "audio", "file"]).optional().describe("Media type filter"),
    mime_type: z.string().optional().describe("MIME type filter"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getMedia(params);
      const formattedMedia = result.media.map(media => `
Media: ${media.title?.rendered || "Untitled"}
ID: ${media.id}
Type: ${media.media_type}
MIME: ${media.mime_type}
URL: ${media.source_url}
Date: ${media.date}
Alt Text: ${media.alt_text || "None"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} media items (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedMedia.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve media", error);
    }
  }
);

server.tool(
  "upload-media",
  "Upload a media file to WordPress",
  {
    filename: z.string().min(1).describe("Filename for the uploaded file"),
    content: z.string().describe("File content as base64 string or file path"),
    title: z.string().optional().describe("Media title"),
    caption: z.string().optional().describe("Media caption"),
    alt_text: z.string().optional().describe("Alt text for accessibility"),
    description: z.string().optional().describe("Media description"),
    post_id: z.number().optional().describe("Post ID to attach media to"),
  },
  async (params) => {
    try {
      const media = await wordpressClient.uploadMedia({
        filename: params.filename,
        content: params.content,
        title: params.title,
        caption: params.caption,
        alt_text: params.alt_text,
        description: params.description,
        post_id: params.post_id,
      });

      return {
        content: [{ 
          type: "text", 
          text: `Media uploaded successfully!\n\nMedia ID: ${media.id}\nTitle: ${media.title?.rendered}\nURL: ${media.source_url}\nType: ${media.media_type}\nMIME: ${media.mime_type}`
        }],
      };
    } catch (error) {
      return handleError("Failed to upload media", error);
    }
  }
);

// Categories Management Tools
server.tool(
  "get-categories",
  "Retrieve WordPress categories",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of categories per page"),
    search: z.string().optional().describe("Search term to filter categories"),
    parent: z.number().optional().describe("Parent category ID"),
    orderby: z.string().optional().default("name").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("asc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getCategories(params);
      const formattedCategories = result.categories.map(cat => `
Category: ${cat.name}
ID: ${cat.id}
Slug: ${cat.slug}
Description: ${cat.description || "None"}
Posts: ${cat.count}
Parent: ${cat.parent || "None"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} categories (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedCategories.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve categories", error);
    }
  }
);

server.tool(
  "create-category",
  "Create a new WordPress category",
  {
    name: z.string().min(1).describe("Category name"),
    description: z.string().optional().describe("Category description"),
    slug: z.string().optional().describe("Category slug"),
    parent: z.number().default(0).describe("Parent category ID"),
  },
  async (params) => {
    try {
      const category = await wordpressClient.createCategory(params);
      return {
        content: [{ 
          type: "text", 
          text: `Category created successfully!\n\nName: ${category.name}\nID: ${category.id}\nSlug: ${category.slug}\nDescription: ${category.description || "None"}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create category", error);
    }
  }
);

// Tags Management Tools
server.tool(
  "get-tags",
  "Retrieve WordPress tags",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of tags per page"),
    search: z.string().optional().describe("Search term to filter tags"),
    orderby: z.string().optional().default("name").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("asc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getTags(params);
      const formattedTags = result.tags.map(tag => `
Tag: ${tag.name}
ID: ${tag.id}
Slug: ${tag.slug}
Description: ${tag.description || "None"}
Posts: ${tag.count}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} tags (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedTags.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve tags", error);
    }
  }
);

server.tool(
  "create-tag",
  "Create a new WordPress tag",
  {
    name: z.string().min(1).describe("Tag name"),
    description: z.string().optional().describe("Tag description"),
    slug: z.string().optional().describe("Tag slug"),
  },
  async (params) => {
    try {
      const tag = await wordpressClient.createTag(params);
      return {
        content: [{ 
          type: "text", 
          text: `Tag created successfully!\n\nName: ${tag.name}\nID: ${tag.id}\nSlug: ${tag.slug}\nDescription: ${tag.description || "None"}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create tag", error);
    }
  }
);

// Users Management Tools
server.tool(
  "get-users",
  "Retrieve WordPress users",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of users per page"),
    search: z.string().optional().describe("Search term to filter users"),
    roles: z.array(z.string()).optional().describe("User roles to filter"),
    orderby: z.string().optional().default("name").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("asc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getUsers(params);
      const formattedUsers = result.users.map(user => `
User: ${user.name} (${user.username})
ID: ${user.id}
Email: ${user.email}
Roles: ${user.roles.join(", ")}
Registered: ${user.registered_date}
URL: ${user.url || "None"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} users (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedUsers.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve users", error);
    }
  }
);

server.tool(
  "get-current-user",
  "Get information about the currently authenticated user",
  {},
  async () => {
    try {
      const user = await wordpressClient.getCurrentUser();
      return {
        content: [{ 
          type: "text", 
          text: `Current User: ${user.name} (${user.username})\nID: ${user.id}\nEmail: ${user.email}\nRoles: ${user.roles.join(", ")}\nRegistered: ${user.registered_date}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve current user", error);
    }
  }
);

// Site Management Tools
server.tool(
  "get-site-info",
  "Retrieve WordPress site information and settings",
  {},
  async () => {
    try {
      const siteInfo = await wordpressClient.getSiteInfo();
      return {
        content: [{ 
          type: "text", 
          text: `Site Information:\n\nName: ${siteInfo.name}\nDescription: ${siteInfo.description}\nURL: ${siteInfo.url}\nAdmin Email: ${siteInfo.admin_email}\nTimezone: ${siteInfo.timezone}\nLanguage: ${siteInfo.language}\nPosts per Page: ${siteInfo.posts_per_page}`
        }],
      };
    } catch (error) {
      return handleError("Failed to retrieve site information", error);
    }
  }
);

// Content Search Tool
server.tool(
  "search-content",
  "Search across WordPress posts, pages, and media",
  {
    query: z.string().min(1).describe("Search query"),
    types: z.array(z.enum(["posts", "pages", "media"])).default(["posts", "pages"]).describe("Content types to search"),
  },
  async ({ query, types }) => {
    try {
      const results = await wordpressClient.searchContent(query, types);
      let output = `Search results for "${query}":\n\n`;

      if (results.posts?.length) {
        output += `Posts (${results.posts.length}):\n${results.posts.map(formatPost).join("\n---\n")}\n\n`;
      }

      if (results.pages?.length) {
        output += `Pages (${results.pages.length}):\n${results.pages.map(formatPost).join("\n---\n")}\n\n`;
      }

      if (results.media?.length) {
        output += `Media (${results.media.length}):\n${results.media.map(media => `${media.title?.rendered} - ${media.source_url}`).join("\n")}\n\n`;
      }

      if (!results.posts?.length && !results.pages?.length && !results.media?.length) {
        output += "No results found.";
      }

      return {
        content: [{ type: "text", text: output }],
      };
    } catch (error) {
      return handleError(`Failed to search for "${query}"`, error);
    }
  }
);

// Art of Space Content Generation Tools
server.tool(
  "create-art-spotlight",
  "Create an Art of Space artist spotlight post",
  {
    artist_name: z.string().min(1).describe("Artist name"),
    artist_bio: z.string().describe("Artist biography"),
    artwork_title: z.string().min(1).describe("Featured artwork title"),
    artwork_description: z.string().describe("Artwork description"),
    artwork_year: z.string().optional().describe("Year artwork was created"),
    artwork_medium: z.string().optional().describe("Artwork medium/materials"),
    artwork_dimensions: z.string().optional().describe("Artwork dimensions"),
    featured_image: z.number().optional().describe("Featured image media ID"),
    gallery_images: z.array(z.number()).optional().describe("Gallery image media IDs"),
    artist_website: z.string().url().optional().describe("Artist website URL"),
    artist_social: z.record(z.string().url()).optional().describe("Artist social media URLs"),
    price_range: z.string().optional().describe("Price range for the artwork"),
    availability: z.enum(["available", "sold", "on_hold"]).default("available").describe("Artwork availability"),
    tags: z.array(z.string()).optional().describe("Additional tags"),
    publish_date: z.string().optional().describe("Scheduled publish date (ISO format)"),
  },
  async (params) => {
    try {
      const post = await artOfSpaceGenerators.createArtSpotlight(params);
      return {
        content: [{ 
          type: "text", 
          text: `Art Spotlight post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create art spotlight post", error);
    }
  }
);

server.tool(
  "create-collection-announcement",
  "Create an Art of Space collection announcement post",
  {
    collection_name: z.string().min(1).describe("Collection name"),
    collection_description: z.string().describe("Collection description"),
    artist_name: z.string().optional().describe("Artist name (if single artist collection)"),
    launch_date: z.string().optional().describe("Collection launch date (ISO format)"),
    featured_artworks: z.array(z.object({
      title: z.string().describe("Artwork title"),
      description: z.string().describe("Artwork description"),
      image_id: z.number().optional().describe("Artwork image media ID"),
      price: z.string().optional().describe("Artwork price")
    })).optional().describe("Featured artworks in the collection"),
    collection_theme: z.string().optional().describe("Collection theme/concept"),
    inspiration: z.string().optional().describe("Artist's inspiration for the collection"),
    featured_image: z.number().optional().describe("Featured image media ID"),
    gallery_images: z.array(z.number()).optional().describe("Gallery image media IDs"),
    tags: z.array(z.string()).optional().describe("Additional tags"),
    categories: z.array(z.string()).optional().describe("Additional categories"),
  },
  async (params) => {
    try {
      const post = await artOfSpaceGenerators.createCollectionAnnouncement(params);
      return {
        content: [{ 
          type: "text", 
          text: `Collection announcement post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create collection announcement post", error);
    }
  }
);

server.tool(
  "create-how-to-guide",
  "Create an Art of Space how-to guide post",
  {
    guide_title: z.string().min(1).describe("Guide title"),
    guide_type: z.enum(["care", "display", "framing", "lighting", "maintenance", "installation"]).describe("Type of guide"),
    difficulty_level: z.enum(["beginner", "intermediate", "advanced"]).default("beginner").describe("Difficulty level"),
    time_required: z.string().optional().describe("Estimated time required"),
    materials_needed: z.array(z.string()).optional().describe("Materials/tools needed"),
    steps: z.array(z.object({
      step_number: z.number().describe("Step number"),
      title: z.string().describe("Step title"),
      description: z.string().describe("Step description"),
      image_id: z.number().optional().describe("Step image media ID"),
      tips: z.array(z.string()).optional().describe("Additional tips for this step")
    })).describe("Step-by-step instructions"),
    expert_tips: z.array(z.string()).optional().describe("Expert tips"),
    common_mistakes: z.array(z.string()).optional().describe("Common mistakes to avoid"),
    featured_image: z.number().optional().describe("Featured image media ID"),
    tags: z.array(z.string()).optional().describe("Additional tags"),
  },
  async (params) => {
    try {
      const post = await artOfSpaceGenerators.createHowToGuide(params);
      return {
        content: [{ 
          type: "text", 
          text: `How-to guide post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create how-to guide post", error);
    }
  }
);

server.tool(
  "create-seasonal-content",
  "Create Art of Space seasonal content post",
  {
    season: z.enum(["spring", "summer", "fall", "winter", "holiday", "special_occasion"]).describe("Season or occasion"),
    content_type: z.enum(["collection", "styling_tips", "gift_guide", "seasonal_trends"]).describe("Type of seasonal content"),
    title: z.string().min(1).describe("Content title"),
    description: z.string().describe("Content description"),
    featured_artworks: z.array(z.object({
      title: z.string().describe("Artwork title"),
      artist: z.string().optional().describe("Artist name"),
      description: z.string().describe("Artwork description"),
      image_id: z.number().optional().describe("Artwork image media ID"),
      seasonal_relevance: z.string().describe("Why this artwork fits the season")
    })).optional().describe("Featured seasonal artworks"),
    styling_tips: z.array(z.string()).optional().describe("Seasonal styling tips"),
    color_palette: z.array(z.string()).optional().describe("Seasonal color palette"),
    mood_description: z.string().optional().describe("Seasonal mood description"),
    featured_image: z.number().optional().describe("Featured image media ID"),
    gallery_images: z.array(z.number()).optional().describe("Gallery image media IDs"),
    tags: z.array(z.string()).optional().describe("Additional tags"),
  },
  async (params) => {
    try {
      const post = await artOfSpaceGenerators.createSeasonalContent(params);
      return {
        content: [{ 
          type: "text", 
          text: `Seasonal content post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create seasonal content post", error);
    }
  }
);

server.tool(
  "create-artist-interview",
  "Create an Art of Space artist interview post",
  {
    artist_name: z.string().min(1).describe("Artist name"),
    artist_bio: z.string().describe("Artist biography"),
    artist_photo: z.number().optional().describe("Artist photo media ID"),
    interview_questions: z.array(z.object({
      question: z.string().describe("Interview question"),
      answer: z.string().describe("Artist's answer")
    })).describe("Interview questions and answers"),
    featured_artworks: z.array(z.object({
      title: z.string().describe("Artwork title"),
      description: z.string().describe("Artwork description"),
      image_id: z.number().optional().describe("Artwork image media ID"),
      year: z.string().optional().describe("Year created")
    })).optional().describe("Featured artworks discussed in interview"),
    artist_influences: z.array(z.string()).optional().describe("Artist's influences"),
    upcoming_exhibitions: z.array(z.string()).optional().describe("Upcoming exhibitions"),
    artist_statement: z.string().optional().describe("Artist statement"),
    contact_info: z.object({
      website: z.string().url().optional().describe("Artist website"),
      social_media: z.record(z.string().url()).optional().describe("Social media profiles"),
      gallery_representation: z.string().optional().describe("Gallery representation")
    }).optional().describe("Artist contact information"),
    featured_image: z.number().optional().describe("Featured image media ID"),
    tags: z.array(z.string()).optional().describe("Additional tags"),
  },
  async (params) => {
    try {
      const post = await artOfSpaceGenerators.createArtistInterview(params);
      return {
        content: [{ 
          type: "text", 
          text: `Artist interview post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create artist interview post", error);
    }
  }
);

// Bulk Operations Tools
server.tool(
  "bulk-update-posts",
  "Update multiple posts with the same changes",
  {
    post_ids: z.array(z.number()).describe("Array of post IDs to update"),
    updates: z.object({
      status: z.enum(["publish", "draft", "private", "future", "trash"]).optional(),
      categories: z.array(z.number()).optional(),
      tags: z.array(z.number()).optional(),
      author: z.number().optional(),
      comment_status: z.enum(["open", "closed"]).optional(),
      ping_status: z.enum(["open", "closed"]).optional(),
    }).describe("Updates to apply to all posts"),
  },
  async ({ post_ids, updates }) => {
    try {
      const updatePromises = post_ids.map(id => ({
        id,
        data: updates
      }));
      
      const updatedPosts = await wordpressClient.bulkUpdatePosts(updatePromises);
      const formattedPosts = updatedPosts.map(formatPost);
      
      return {
        content: [{ 
          type: "text", 
          text: `Successfully updated ${updatedPosts.length} posts:\n\n${formattedPosts.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to bulk update posts", error);
    }
  }
);

// Post Statistics Tool
server.tool(
  "get-post-stats",
  "Get statistics for a specific post",
  {
    id: z.number().describe("Post ID to get statistics for"),
  },
  async ({ id }) => {
    try {
      const stats = await wordpressClient.getPostStats(id);
      return {
        content: [{ 
          type: "text", 
          text: `Post ${id} Statistics:\n\nComments: ${stats.comments}\nViews: ${stats.views || "Not available"}\nLikes: ${stats.likes || "Not available"}\nShares: ${stats.shares || "Not available"}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get statistics for post ${id}`, error);
    }
  }
);

// Content Optimization Tools
server.tool(
  "optimize-seo",
  "Generate SEO-optimized title and excerpt for content",
  {
    title: z.string().describe("Original title"),
    content: z.string().describe("Content to optimize"),
    max_title_length: z.number().default(60).describe("Maximum title length for SEO"),
    max_excerpt_length: z.number().default(155).describe("Maximum excerpt length for SEO"),
  },
  async ({ title, content, max_title_length, max_excerpt_length }) => {
    try {
      const optimizedTitle = wordpressClient.generateSEOTitle(title, max_title_length);
      const optimizedExcerpt = wordpressClient.generateExcerpt(content, max_excerpt_length);
      const slug = wordpressClient.generateSlug(title);
      
      return {
        content: [{ 
          type: "text", 
          text: `SEO Optimization Results:\n\nOptimized Title: ${optimizedTitle}\nGenerated Slug: ${slug}\nOptimized Excerpt: ${optimizedExcerpt}`
        }],
      };
    } catch (error) {
      return handleError("Failed to optimize content for SEO", error);
    }
  }
);

// API Discovery Tools (Inspired by server-wp-mcp)
server.tool(
  "discover-endpoints",
  "Discover all available WordPress REST API endpoints and capabilities",
  {},
  async () => {
    try {
      const discovery = await wordpressClient.discoverEndpoints();
      return {
        content: [{ 
          type: "text", 
          text: `WordPress API Discovery:\n\nNamespaces: ${discovery.namespaces.join(", ")}\n\nSite Info:\n- Name: ${discovery.site_info.name}\n- Description: ${discovery.site_info.description}\n- URL: ${discovery.site_info.url}\n- Timezone: ${discovery.site_info.timezone_string}\n\nAvailable Routes: ${Object.keys(discovery.routes).length} endpoints`
        }],
      };
    } catch (error) {
      return handleError("Failed to discover API endpoints", error);
    }
  }
);

server.tool(
  "call-endpoint",
  "Make a direct call to any WordPress REST API endpoint",
  {
    endpoint: z.string().describe("API endpoint to call (e.g., /wp/v2/posts)"),
    method: z.enum(["GET", "POST", "PUT", "DELETE", "PATCH"]).default("GET").describe("HTTP method"),
    data: z.any().optional().describe("Request body data for POST/PUT/PATCH requests"),
    query_params: z.record(z.any()).optional().describe("Query parameters"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.callEndpoint(params);
      return {
        content: [{ 
          type: "text", 
          text: `Endpoint: ${params.method} ${params.endpoint}\n\nResponse:\n${JSON.stringify(result, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to call endpoint ${params.endpoint}`, error);
    }
  }
);

// Enhanced Plugin Management Tools
server.tool(
  "get-plugin",
  "Get detailed information about a specific plugin",
  {
    plugin: z.string().describe("Plugin slug/name"),
  },
  async ({ plugin }) => {
    try {
      const pluginInfo = await wordpressClient.getPlugin(plugin);
      return {
        content: [{ 
          type: "text", 
          text: `Plugin: ${pluginInfo.name}\nStatus: ${pluginInfo.status}\nVersion: ${pluginInfo.version}\nAuthor: ${pluginInfo.author}\nDescription: ${pluginInfo.description.rendered}\nRequires WP: ${pluginInfo.requires_wp}\nRequires PHP: ${pluginInfo.requires_php}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get plugin ${plugin}`, error);
    }
  }
);

server.tool(
  "update-plugin",
  "Update a specific plugin to the latest version",
  {
    plugin: z.string().describe("Plugin slug/name to update"),
  },
  async ({ plugin }) => {
    try {
      const result = await wordpressClient.updatePlugin(plugin);
      return {
        content: [{ 
          type: "text", 
          text: `Plugin ${plugin} update initiated.\n\nResult: ${JSON.stringify(result, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to update plugin ${plugin}`, error);
    }
  }
);

server.tool(
  "delete-plugin",
  "Delete/uninstall a plugin",
  {
    plugin: z.string().describe("Plugin slug/name to delete"),
  },
  async ({ plugin }) => {
    try {
      const result = await wordpressClient.deletePlugin(plugin);
      return {
        content: [{ 
          type: "text", 
          text: `Plugin ${plugin} ${result.deleted ? "deleted successfully" : "failed to delete"}\n\nPrevious data:\n${JSON.stringify(result.previous, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to delete plugin ${plugin}`, error);
    }
  }
);

// Enhanced Theme Management Tools
server.tool(
  "get-theme",
  "Get detailed information about a specific theme",
  {
    theme: z.string().describe("Theme slug/name"),
  },
  async ({ theme }) => {
    try {
      const themeInfo = await wordpressClient.getTheme(theme);
      return {
        content: [{ 
          type: "text", 
          text: `Theme: ${themeInfo.name.rendered}\nStatus: ${themeInfo.status}\nVersion: ${themeInfo.version}\nAuthor: ${themeInfo.author}\nDescription: ${themeInfo.description.rendered}\nRequires WP: ${themeInfo.requires_wp}\nRequires PHP: ${themeInfo.requires_php}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get theme ${theme}`, error);
    }
  }
);

server.tool(
  "activate-theme",
  "Activate a specific theme",
  {
    theme: z.string().describe("Theme slug/name to activate"),
  },
  async ({ theme }) => {
    try {
      const result = await wordpressClient.activateTheme(theme);
      return {
        content: [{ 
          type: "text", 
          text: `Theme ${theme} activated successfully!\n\nTheme: ${result.name.rendered}\nStatus: ${result.status}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to activate theme ${theme}`, error);
    }
  }
);

server.tool(
  "update-theme",
  "Update a specific theme to the latest version",
  {
    theme: z.string().describe("Theme slug/name to update"),
  },
  async ({ theme }) => {
    try {
      const result = await wordpressClient.updateTheme(theme);
      return {
        content: [{ 
          type: "text", 
          text: `Theme ${theme} update initiated.\n\nResult: ${JSON.stringify(result, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to update theme ${theme}`, error);
    }
  }
);

server.tool(
  "delete-theme",
  "Delete/uninstall a theme",
  {
    theme: z.string().describe("Theme slug/name to delete"),
  },
  async ({ theme }) => {
    try {
      const result = await wordpressClient.deleteTheme(theme);
      return {
        content: [{ 
          type: "text", 
          text: `Theme ${theme} ${result.deleted ? "deleted successfully" : "failed to delete"}\n\nPrevious data:\n${JSON.stringify(result.previous, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to delete theme ${theme}`, error);
    }
  }
);

// Custom Post Types Management Tools
server.tool(
  "get-post-types",
  "Get all available post types",
  {},
  async () => {
    try {
      const postTypes = await wordpressClient.getPostTypes();
      const formattedTypes = postTypes.map(type => `
Type: ${type.name}
Slug: ${type.slug}
Description: ${type.description || "No description"}
Hierarchical: ${type.hierarchical ? "Yes" : "No"}
Public: ${type.public ? "Yes" : "No"}
REST Base: ${type.rest_base || "Not available"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${postTypes.length} post types:\n\n${formattedTypes.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to get post types", error);
    }
  }
);

server.tool(
  "get-custom-posts",
  "Get posts from a custom post type",
  {
    post_type: z.string().describe("Custom post type slug"),
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of posts per page"),
    search: z.string().optional().describe("Search term"),
    status: z.array(z.enum(["publish", "draft", "private", "future", "trash"])).optional().describe("Post statuses"),
    orderby: z.string().optional().default("date").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("desc").describe("Sort order"),
  },
  async (params) => {
    try {
      const { post_type, ...queryParams } = params;
      const result = await wordpressClient.getCustomPosts(post_type, queryParams);
      const formattedPosts = result.posts.map(formatPost);
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} ${post_type} posts (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedPosts.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get ${params.post_type} posts`, error);
    }
  }
);

server.tool(
  "create-custom-post",
  "Create a post in a custom post type",
  {
    post_type: z.string().describe("Custom post type slug"),
    title: z.string().min(1).describe("Post title"),
    content: z.string().min(1).describe("Post content"),
    status: z.enum(["publish", "draft", "private", "future"]).default("draft").describe("Post status"),
    meta: z.record(z.any()).optional().describe("Custom field values"),
  },
  async (params) => {
    try {
      const { post_type, ...postData } = params;
      const post = await wordpressClient.createCustomPost(post_type, {
        title: { rendered: postData.title },
        content: { rendered: postData.content },
        status: postData.status,
        meta: postData.meta
      });
      
      return {
        content: [{ 
          type: "text", 
          text: `${post_type} post created successfully!\n\n${formatPost(post)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to create ${params.post_type} post`, error);
    }
  }
);

// Custom Fields (Meta) Management Tools
server.tool(
  "get-post-meta",
  "Get all custom field values for a post",
  {
    post_id: z.number().describe("Post ID"),
  },
  async ({ post_id }) => {
    try {
      const meta = await wordpressClient.getPostMeta(post_id);
      const formattedMeta = Object.entries(meta).map(([key, value]) => 
        `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`
      ).join("\n");
      
      return {
        content: [{ 
          type: "text", 
          text: `Custom fields for post ${post_id}:\n\n${formattedMeta || "No custom fields found"}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get meta for post ${post_id}`, error);
    }
  }
);

server.tool(
  "update-post-meta",
  "Update a custom field value for a post",
  {
    post_id: z.number().describe("Post ID"),
    meta_key: z.string().describe("Custom field key"),
    meta_value: z.any().describe("Custom field value"),
  },
  async ({ post_id, meta_key, meta_value }) => {
    try {
      const result = await wordpressClient.updatePostMeta(post_id, meta_key, meta_value);
      return {
        content: [{ 
          type: "text", 
          text: `Custom field ${meta_key} updated for post ${post_id}\n\nResult: ${JSON.stringify(result, null, 2)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to update meta ${meta_key} for post ${post_id}`, error);
    }
  }
);

// Gutenberg Block Editor Tools
server.tool(
  "get-blocks",
  "Get all Gutenberg blocks from a post",
  {
    post_id: z.number().describe("Post ID"),
  },
  async ({ post_id }) => {
    try {
      const blocks = await wordpressClient.getBlocks(post_id);
      const formattedBlocks = blocks.map((block, index) => 
        `Block ${index + 1}: ${block.blockName}\nAttributes: ${JSON.stringify(block.attrs, null, 2)}`
      ).join("\n---\n");
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${blocks.length} blocks in post ${post_id}:\n\n${formattedBlocks || "No blocks found"}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to get blocks for post ${post_id}`, error);
    }
  }
);

server.tool(
  "add-block",
  "Add a Gutenberg block to a post",
  {
    post_id: z.number().describe("Post ID"),
    block_name: z.string().describe("Block name (e.g., core/paragraph, core/image)"),
    attributes: z.record(z.any()).optional().describe("Block attributes"),
    content: z.string().optional().describe("Block content/HTML"),
    position: z.number().optional().describe("Position to insert block (default: end)"),
  },
  async ({ post_id, block_name, attributes, content, position }) => {
    try {
      const result = await wordpressClient.addBlock(post_id, {
        blockName: block_name,
        attrs: attributes,
        innerHTML: content,
        position
      });
      
      return {
        content: [{ 
          type: "text", 
          text: `Block ${block_name} added to post ${post_id}\n\n${formatPost(result)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to add block to post ${post_id}`, error);
    }
  }
);

server.tool(
  "remove-block",
  "Remove a Gutenberg block from a post",
  {
    post_id: z.number().describe("Post ID"),
    block_index: z.number().describe("Index of block to remove (0-based)"),
  },
  async ({ post_id, block_index }) => {
    try {
      const result = await wordpressClient.removeBlock(post_id, block_index);
      return {
        content: [{ 
          type: "text", 
          text: `Block at index ${block_index} removed from post ${post_id}\n\n${formatPost(result)}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to remove block from post ${post_id}`, error);
    }
  }
);

// Comments Management Tools
server.tool(
  "get-comments",
  "Get WordPress comments with filtering options",
  {
    page: z.number().optional().describe("Page number for pagination"),
    per_page: z.number().optional().default(10).describe("Number of comments per page"),
    search: z.string().optional().describe("Search term"),
    post: z.number().optional().describe("Post ID to filter comments"),
    status: z.string().optional().describe("Comment status (approved, hold, spam, trash)"),
    orderby: z.string().optional().default("date_gmt").describe("Field to order by"),
    order: z.enum(["asc", "desc"]).optional().default("desc").describe("Sort order"),
  },
  async (params) => {
    try {
      const result = await wordpressClient.getComments(params);
      const formattedComments = result.comments.map(comment => `
Comment ID: ${comment.id}
Author: ${comment.author_name} (${comment.author_email})
Post: ${comment.post}
Date: ${comment.date}
Status: ${comment.status}
Content: ${comment.content.rendered.replace(/<[^>]*>/g, '').substring(0, 150)}...
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${result.total} comments (Page ${params.page || 1} of ${result.totalPages}):\n\n${formattedComments.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to get comments", error);
    }
  }
);

server.tool(
  "approve-comment",
  "Approve a pending comment",
  {
    comment_id: z.number().describe("Comment ID to approve"),
  },
  async ({ comment_id }) => {
    try {
      const result = await wordpressClient.approveComment(comment_id);
      return {
        content: [{ 
          type: "text", 
          text: `Comment ${comment_id} approved successfully!\n\nAuthor: ${result.author_name}\nStatus: ${result.status}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to approve comment ${comment_id}`, error);
    }
  }
);

server.tool(
  "reject-comment",
  "Reject/hold a comment",
  {
    comment_id: z.number().describe("Comment ID to reject"),
  },
  async ({ comment_id }) => {
    try {
      const result = await wordpressClient.rejectComment(comment_id);
      return {
        content: [{ 
          type: "text", 
          text: `Comment ${comment_id} rejected and put on hold!\n\nAuthor: ${result.author_name}\nStatus: ${result.status}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to reject comment ${comment_id}`, error);
    }
  }
);

server.tool(
  "spam-comment",
  "Mark a comment as spam",
  {
    comment_id: z.number().describe("Comment ID to mark as spam"),
  },
  async ({ comment_id }) => {
    try {
      const result = await wordpressClient.spamComment(comment_id);
      return {
        content: [{ 
          type: "text", 
          text: `Comment ${comment_id} marked as spam!\n\nAuthor: ${result.author_name}\nStatus: ${result.status}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to mark comment ${comment_id} as spam`, error);
    }
  }
);

// VividWalls Specific Tools
server.tool(
  "create-product-post",
  "Create a product post optimized for VividWalls art business",
  {
    title: z.string().min(1).describe("Artwork title"),
    description: z.string().describe("Artwork description"),
    price: z.number().min(0).describe("Artwork price in USD"),
    artist: z.string().describe("Artist name"),
    dimensions: z.string().describe("Artwork dimensions"),
    medium: z.string().describe("Artwork medium/materials"),
    year: z.string().optional().describe("Year artwork was created"),
    image_gallery: z.array(z.number()).describe("Array of media IDs for gallery"),
    featured_image: z.number().describe("Featured image media ID"),
    categories: z.array(z.string()).describe("Product categories"),
    tags: z.array(z.string()).describe("Product tags"),
    availability: z.enum(["available", "sold", "on_hold"]).describe("Artwork availability"),
    sku: z.string().optional().describe("Custom SKU (auto-generated if not provided)"),
  },
  async (params) => {
    try {
      const post = await wordpressClient.createProductPost(params);
      return {
        content: [{ 
          type: "text", 
          text: `VividWalls product post created successfully!\n\n${formatPost(post)}\n\nSKU: ${post.meta?._product_sku || "Auto-generated"}\nPrice: $${params.price.toLocaleString()}\nAvailability: ${params.availability}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create VividWalls product post", error);
    }
  }
);

// VividWalls Recommendation System Tools
server.tool(
  "create-recommendation-page",
  "Create a VividWalls AI recommendation page with masonry grid layout",
  {
    page_title: z.string().default("Art Recommendations").describe("Page title"),
    hero_title: z.string().default("Discover Your Perfect Art").describe("Hero section title"),
    hero_subtitle: z.string().optional().describe("Hero section subtitle"),
    enable_image_upload: z.boolean().default(true).describe("Enable room image upload feature"),
    enable_style_filters: z.boolean().default(true).describe("Enable quick style filter tags"),
    default_filters: z.array(z.string()).optional().describe("Default style filters to display"),
    n8n_webhook_url: z.string().url().optional().describe("n8n webhook URL for AI processing"),
    analytics_tracking: z.boolean().default(true).describe("Enable analytics tracking"),
  },
  async (params) => {
    try {
      const pageContent = `
<!-- VividWalls AI Recommendations Page -->
<div id="vividwalls-recommendations-app">
  <!-- Hero Section -->
  <section class="recommendations-hero">
    <div class="hero-content">
      <h1 class="hero-title">
        <span class="gradient-text">${params.hero_title}</span>
      </h1>
      ${params.hero_subtitle ? `<p class="hero-subtitle">${params.hero_subtitle}</p>` : ''}
    </div>
  </section>

  <!-- AI Interface -->
  <section class="ai-interface-section">
    <div class="container">
      <div class="ai-interface-card">
        <div class="interface-header">
          <div class="ai-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9L17 14L18.18 21L12 17.77L5.82 21L7 14L2 9L8.91 8.26L12 2Z"/>
            </svg>
          </div>
          <div class="interface-title">
            <h2>VividWalls AI Art Curator</h2>
            <p>Upload a room photo or describe your style preferences</p>
          </div>
        </div>

        ${params.enable_image_upload ? `
        <!-- Image Upload Section -->
        <div class="upload-section" id="upload-section">
          <div class="upload-area" id="upload-area">
            <div class="upload-content">
              <div class="upload-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z"/>
                </svg>
              </div>
              <h3>Upload Your Room Photo</h3>
              <p>Drag and drop or click to upload a photo of your space</p>
              <button class="upload-btn" id="upload-btn">Choose Photo</button>
              <input type="file" id="room-image-input" accept="image/*" style="display: none;">
            </div>
          </div>
        </div>

        <div class="divider"><span>OR</span></div>
        ` : ''}

        <!-- Text Input Section -->
        <div class="text-input-section">
          <div class="input-group">
            <label for="style-description">Describe Your Style Preferences</label>
            <textarea id="style-description" placeholder="Tell us about your style preferences, room type, color preferences..." rows="4"></textarea>
          </div>
          
          ${params.enable_style_filters ? `
          <div class="style-filters">
            <h4>Quick Style Filters</h4>
            <div class="filter-grid">
              <button class="filter-tag" data-style="modern">Modern</button>
              <button class="filter-tag" data-style="contemporary">Contemporary</button>
              <button class="filter-tag" data-style="minimalist">Minimalist</button>
              <button class="filter-tag" data-style="abstract">Abstract</button>
              <button class="filter-tag" data-style="landscape">Landscape</button>
              <button class="filter-tag" data-style="portrait">Portrait</button>
              <button class="filter-tag" data-style="colorful">Colorful</button>
              <button class="filter-tag" data-style="monochrome">Black & White</button>
            </div>
          </div>
          ` : ''}

          <button class="btn btn-primary btn-large" id="get-recommendations">
            Get AI Recommendations
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- Recommendations Display -->
  <section class="recommendations-section" id="recommendations-section" style="display: none;">
    <div class="container">
      <div class="section-header">
        <h2>Perfect Matches for Your Space</h2>
        <p>Our AI has curated these artworks specifically for you</p>
      </div>

      <!-- Filter Controls -->
      <div class="recommendations-controls">
        <div class="filter-controls">
          <select id="price-filter">
            <option value="">All Prices</option>
            <option value="0-500">Under $500</option>
            <option value="500-1000">$500 - $1,000</option>
            <option value="1000-2000">$1,000 - $2,000</option>
            <option value="2000+">$2,000+</option>
          </select>
          <select id="size-filter">
            <option value="">All Sizes</option>
            <option value="small">Small (under 16")</option>
            <option value="medium">Medium (16" - 24")</option>
            <option value="large">Large (24" - 36")</option>
            <option value="xl">Extra Large (36"+)</option>
          </select>
        </div>
        <div class="sort-controls">
          <select id="sort-options">
            <option value="relevance">Best Match</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="newest">Newest First</option>
          </select>
        </div>
      </div>

      <!-- Masonry Grid -->
      <div class="recommendations-grid" id="recommendations-grid">
        <!-- Dynamic content loaded here -->
      </div>

      <div class="load-more-section">
        <button class="btn btn-outline btn-large" id="load-more-btn">
          Load More Recommendations
        </button>
      </div>
    </div>
  </section>

  <!-- Loading Overlay -->
  <div class="loading-overlay" id="loading-overlay" style="display: none;">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <h3>Analyzing Your Space...</h3>
      <p id="loading-message">Our AI is finding perfect art matches</p>
      <div class="loading-progress">
        <div class="progress-bar" id="progress-bar"></div>
      </div>
    </div>
  </div>
</div>

${params.n8n_webhook_url ? `
<script>
  window.vividwallsConfig = {
    n8nEndpoint: '${params.n8n_webhook_url}',
    enableAnalytics: ${params.analytics_tracking}
  };
</script>
` : ''}
      `;

      const page = await wordpressClient.createPage({
        title: { rendered: params.page_title },
        content: { rendered: pageContent, protected: false },
        status: "publish",
        slug: "art-recommendations",
        comment_status: "closed",
        ping_status: "closed"
      });

      return {
        content: [{ 
          type: "text", 
          text: `VividWalls AI recommendation page created successfully!\n\n${formatPost(page)}\n\nPage URL: ${page.link}\n\nFeatures enabled:\n- Image Upload: ${params.enable_image_upload ? 'Yes' : 'No'}\n- Style Filters: ${params.enable_style_filters ? 'Yes' : 'No'}\n- Analytics: ${params.analytics_tracking ? 'Yes' : 'No'}`
        }],
      };
    } catch (error) {
      return handleError("Failed to create VividWalls recommendation page", error);
    }
  }
);

server.tool(
  "create-recommendation-shortcode",
  "Create a shortcode for embedding VividWalls recommendations anywhere",
  {
    shortcode_name: z.string().default("vividwalls_recommendations").describe("Shortcode name"),
    default_layout: z.enum(["grid", "list", "carousel"]).default("grid").describe("Default display layout"),
    items_per_page: z.number().default(9).describe("Number of items to display"),
    enable_filters: z.boolean().default(true).describe("Enable filter controls"),
    style_theme: z.enum(["default", "minimal", "dark"]).default("default").describe("Visual theme"),
    auto_load: z.boolean().default(false).describe("Auto-load recommendations on page load"),
  },
  async (params) => {
    try {
      const shortcodeContent = `
<!-- VividWalls Recommendations Shortcode -->
<div class="vividwalls-recommendations-shortcode" 
     data-layout="${params.default_layout}"
     data-items="${params.items_per_page}"
     data-theme="${params.style_theme}"
     data-filters="${params.enable_filters}"
     data-auto-load="${params.auto_load}">
  
  ${params.enable_filters ? `
  <div class="shortcode-filters">
    <div class="filter-row">
      <select class="style-filter">
        <option value="">All Styles</option>
        <option value="abstract">Abstract</option>
        <option value="landscape">Landscape</option>
        <option value="modern">Modern</option>
        <option value="contemporary">Contemporary</option>
      </select>
      <select class="price-filter">
        <option value="">All Prices</option>
        <option value="0-500">Under $500</option>
        <option value="500-1000">$500 - $1,000</option>
        <option value="1000+">$1,000+</option>
      </select>
      <button class="get-recommendations-btn">Get Recommendations</button>
    </div>
  </div>
  ` : ''}
  
  <div class="recommendations-container ${params.default_layout}-layout theme-${params.style_theme}">
    ${params.auto_load ? '' : `
    <div class="recommendation-prompt">
      <h3>Discover Your Perfect Art</h3>
      <p>Click "Get Recommendations" to see AI-curated artworks for your space</p>
    </div>
    `}
    <div class="recommendations-grid" id="shortcode-recommendations-grid">
      <!-- Recommendations will be loaded here -->
    </div>
  </div>
  
  <div class="shortcode-loading" style="display: none;">
    <div class="loading-spinner"></div>
    <p>Finding perfect art matches...</p>
  </div>
</div>

<script>
// Initialize shortcode functionality
jQuery(document).ready(function($) {
  $('.vividwalls-recommendations-shortcode').each(function() {
    var $container = $(this);
    var settings = {
      layout: $container.data('layout'),
      items: $container.data('items'),
      theme: $container.data('theme'),
      filters: $container.data('filters'),
      autoLoad: $container.data('auto-load')
    };
    
    if (settings.autoLoad) {
      loadRecommendations($container, {});
    }
    
    $container.find('.get-recommendations-btn').on('click', function() {
      var filters = {
        style: $container.find('.style-filter').val(),
        price: $container.find('.price-filter').val()
      };
      loadRecommendations($container, filters);
    });
  });
  
  function loadRecommendations($container, filters) {
    $container.find('.shortcode-loading').show();
    $container.find('.recommendation-prompt').hide();
    
    // AJAX call to get recommendations
    $.post(ajaxurl, {
      action: 'get_ai_recommendations',
      nonce: vividwalls_recs.nonce,
      request_type: 'shortcode_recommendations',
      filters: filters,
      layout: $container.data('layout'),
      items: $container.data('items')
    }, function(response) {
      $container.find('.shortcode-loading').hide();
      
      if (response.success && response.data.items) {
        displayRecommendations($container, response.data.items);
      } else {
        $container.find('.recommendations-grid').html('<p>No recommendations found. Try adjusting your preferences.</p>');
      }
    });
  }
  
  function displayRecommendations($container, items) {
    var $grid = $container.find('.recommendations-grid');
    $grid.empty();
    
    items.forEach(function(item) {
      var $card = $('<div class="rec-card">' +
        '<div class="card-image">' +
          '<img src="' + item.image_url + '" alt="' + item.title + '">' +
          '<div class="card-overlay">' +
            '<a href="' + item.product_url + '" class="view-btn">View Art</a>' +
          '</div>' +
        '</div>' +
        '<div class="card-content">' +
          '<h4>' + item.title + '</h4>' +
          '<p class="artist">by ' + item.artist + '</p>' +
          '<p class="price">$' + item.price.toLocaleString() + '</p>' +
        '</div>' +
      '</div>');
      
      $grid.append($card);
    });
    
    // Initialize masonry if grid layout
    if ($container.data('layout') === 'grid') {
      $grid.masonry({
        itemSelector: '.rec-card',
        percentPosition: true,
        gutter: 20
      });
    }
  }
});
</script>

<style>
.vividwalls-recommendations-shortcode {
  margin: 20px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.shortcode-filters {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-row select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.get-recommendations-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.get-recommendations-btn:hover {
  transform: translateY(-1px);
}

.recommendations-container.grid-layout .recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.recommendations-container.list-layout .recommendations-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.rec-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.rec-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.card-image {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.rec-card:hover .card-overlay {
  opacity: 1;
}

.view-btn {
  background: white;
  color: #333;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.view-btn:hover {
  background: #f0f0f0;
}

.card-content {
  padding: 15px;
}

.card-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.artist {
  margin: 0 0 10px 0;
  color: #666;
  font-style: italic;
  font-size: 14px;
}

.price {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.shortcode-loading {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.recommendation-prompt {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.theme-minimal {
  --primary-color: #333;
  --border-radius: 4px;
}

.theme-dark {
  background: #2d3748;
  color: white;
}

.theme-dark .rec-card {
  background: #4a5568;
  color: white;
}

.theme-dark .shortcode-filters {
  background: #4a5568;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-row select,
  .get-recommendations-btn {
    width: 100%;
  }
  
  .recommendations-container.grid-layout .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
}
</style>
      `;

      // Create a post to document the shortcode
      const post = await wordpressClient.createPost({
        title: { rendered: `VividWalls Recommendations Shortcode - [${params.shortcode_name}]` },
        content: { rendered: `
<h2>VividWalls Recommendations Shortcode</h2>

<p>Use this shortcode to embed AI-powered art recommendations anywhere on your site:</p>

<pre><code>[${params.shortcode_name}]</code></pre>

<h3>Shortcode Attributes:</h3>
<ul>
<li><strong>layout</strong>: grid, list, or carousel (default: ${params.default_layout})</li>
<li><strong>items</strong>: Number of items to display (default: ${params.items_per_page})</li>
<li><strong>theme</strong>: default, minimal, or dark (default: ${params.style_theme})</li>
<li><strong>filters</strong>: Enable filter controls (default: ${params.enable_filters})</li>
<li><strong>auto_load</strong>: Auto-load recommendations (default: ${params.auto_load})</li>
</ul>

<h3>Example Usage:</h3>
<pre><code>[${params.shortcode_name} layout="grid" items="6" theme="minimal" filters="true"]</code></pre>

<h3>Implementation Code:</h3>
<pre><code>${shortcodeContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
        `, protected: false },
        status: "draft",
        categories: [],
        tags: []
      });

      return {
        content: [{ 
          type: "text", 
          text: `VividWalls recommendations shortcode created successfully!\n\nShortcode: [${params.shortcode_name}]\n\nDocumentation post: ${formatPost(post)}\n\nConfiguration:\n- Layout: ${params.default_layout}\n- Items per page: ${params.items_per_page}\n- Theme: ${params.style_theme}\n- Filters enabled: ${params.enable_filters}\n- Auto-load: ${params.auto_load}\n\nTo use this shortcode, add it to any post or page content.`
        }],
      };
    } catch (error) {
      return handleError("Failed to create VividWalls recommendations shortcode", error);
    }
  }
);

server.tool(
  "optimize-image-seo",
  "Optimize image SEO for artwork media",
  {
    media_id: z.number().describe("Media ID to optimize"),
    alt_text: z.string().optional().describe("Alt text for accessibility"),
    title: z.string().optional().describe("Image title"),
    caption: z.string().optional().describe("Image caption"),
    description: z.string().optional().describe("Image description"),
  },
  async (params) => {
    try {
      const { media_id, ...optimizations } = params;
      const result = await wordpressClient.optimizeImageSEO(media_id, optimizations);
      return {
        content: [{ 
          type: "text", 
          text: `Image SEO optimized for media ${media_id}!\n\nTitle: ${result.title?.rendered}\nAlt Text: ${result.alt_text}\nCaption: ${result.caption?.rendered}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to optimize SEO for media ${params.media_id}`, error);
    }
  }
);

server.tool(
  "generate-schema-markup",
  "Generate structured data (schema markup) for a product post",
  {
    post_id: z.number().describe("Product post ID"),
  },
  async ({ post_id }) => {
    try {
      const schema = await wordpressClient.generateSchemaMarkup(post_id);
      return {
        content: [{ 
          type: "text", 
          text: schema ? `Schema markup for post ${post_id}:\n\n${schema}` : `No product data found for post ${post_id} - not a VividWalls product post`
        }],
      };
    } catch (error) {
      return handleError(`Failed to generate schema markup for post ${post_id}`, error);
    }
  }
);

// Multisite Management Tools
server.tool(
  "get-network-sites",
  "Get all sites in a WordPress multisite network",
  {},
  async () => {
    try {
      const sites = await wordpressClient.getNetworkSites();
      const formattedSites = sites.map(site => `
Site: ${site.name}
ID: ${site.id}
URL: ${site.url}
Description: ${site.description || "No description"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${sites.length} site(s):\n\n${formattedSites.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to get network sites", error);
    }
  }
);

server.tool(
  "get-network-plugins",
  "Get network-activated plugins in a multisite",
  {},
  async () => {
    try {
      const plugins = await wordpressClient.getNetworkPlugins();
      const formattedPlugins = plugins.map(plugin => `
Plugin: ${plugin.name}
Status: ${plugin.status}
Version: ${plugin.version}
Network Only: ${plugin.network_only ? "Yes" : "No"}
      `.trim());
      
      return {
        content: [{ 
          type: "text", 
          text: `Found ${plugins.length} network plugin(s):\n\n${formattedPlugins.join("\n---\n")}`
        }],
      };
    } catch (error) {
      return handleError("Failed to get network plugins", error);
    }
  }
);

server.tool(
  "network-activate-plugin",
  "Network activate a plugin across all sites in multisite",
  {
    plugin: z.string().describe("Plugin slug/name to network activate"),
  },
  async ({ plugin }) => {
    try {
      const result = await wordpressClient.networkActivatePlugin(plugin);
      return {
        content: [{ 
          type: "text", 
          text: `Plugin ${plugin} network activated successfully!\n\nStatus: ${result.status}\nNetwork Only: ${result.network_only ? "Yes" : "No"}`
        }],
      };
    } catch (error) {
      return handleError(`Failed to network activate plugin ${plugin}`, error);
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("WordPress MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});