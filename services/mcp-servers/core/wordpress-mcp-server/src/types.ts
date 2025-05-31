import { z } from "zod";

// WordPress API Response Types
export interface WordPressPost {
  id: number;
  date: string;
  date_gmt: string;
  guid: { rendered: string };
  modified: string;
  modified_gmt: string;
  slug: string;
  status: "publish" | "draft" | "private" | "future" | "trash";
  type: string;
  link: string;
  title: { rendered: string };
  content: { rendered: string; protected: boolean };
  excerpt: { rendered: string; protected: boolean };
  author: number;
  featured_media: number;
  comment_status: "open" | "closed";
  ping_status: "open" | "closed";
  sticky: boolean;
  template: string;
  format: string;
  meta: Record<string, any>;
  categories: number[];
  tags: number[];
  acf?: Record<string, any>;
}

export interface WordPressPage {
  id: number;
  date: string;
  date_gmt: string;
  guid: { rendered: string };
  modified: string;
  modified_gmt: string;
  slug: string;
  status: "publish" | "draft" | "private" | "future" | "trash";
  type: string;
  link: string;
  title: { rendered: string };
  content: { rendered: string; protected: boolean };
  excerpt: { rendered: string; protected: boolean };
  author: number;
  featured_media: number;
  comment_status: "open" | "closed";
  ping_status: "open" | "closed";
  template: string;
  parent: number;
  menu_order: number;
  meta: Record<string, any>;
}

export interface WordPressMedia {
  id: number;
  date: string;
  date_gmt: string;
  guid: { rendered: string };
  modified: string;
  modified_gmt: string;
  slug: string;
  status: string;
  type: string;
  link: string;
  title: { rendered: string };
  author: number;
  comment_status: string;
  ping_status: string;
  template: string;
  meta: Record<string, any>;
  description: { rendered: string };
  caption: { rendered: string };
  alt_text: string;
  media_type: "image" | "video" | "audio" | "file";
  mime_type: string;
  media_details: {
    width?: number;
    height?: number;
    file: string;
    sizes?: Record<string, {
      file: string;
      width: number;
      height: number;
      mime_type: string;
      source_url: string;
    }>;
    image_meta?: Record<string, any>;
  };
  source_url: string;
}

export interface WordPressCategory {
  id: number;
  count: number;
  description: string;
  link: string;
  name: string;
  slug: string;
  taxonomy: string;
  parent: number;
  meta: Record<string, any>;
}

export interface WordPressTag {
  id: number;
  count: number;
  description: string;
  link: string;
  name: string;
  slug: string;
  taxonomy: string;
  meta: Record<string, any>;
}

export interface WordPressUser {
  id: number;
  username: string;
  name: string;
  first_name: string;
  last_name: string;
  email: string;
  url: string;
  description: string;
  link: string;
  locale: string;
  nickname: string;
  slug: string;
  roles: string[];
  registered_date: string;
  capabilities: Record<string, boolean>;
  extra_capabilities: Record<string, boolean>;
  avatar_urls: Record<string, string>;
  meta: Record<string, any>;
}

export interface WordPressPlugin {
  plugin: string;
  status: "inactive" | "active" | "network-active";
  name: string;
  plugin_uri: string;
  author: string;
  author_uri: string;
  description: { rendered: string };
  version: string;
  network_only: boolean;
  requires_wp: string;
  requires_php: string;
  text_domain: string;
  domain_path: string;
}

export interface WordPressTheme {
  stylesheet: string;
  template: string;
  author: string;
  author_uri: string;
  description: { rendered: string };
  name: { rendered: string };
  requires_php: string;
  requires_wp: string;
  screenshot: string;
  status: "inactive" | "active";
  tags: string[];
  text_domain: string;
  version: string;
}

export interface WordPressSiteInfo {
  name: string;
  description: string;
  url: string;
  admin_email: string;
  timezone: string;
  date_format: string;
  time_format: string;
  start_of_week: number;
  language: string;
  use_smilies: boolean;
  default_category: number;
  default_post_format: string;
  posts_per_page: number;
  default_ping_status: "open" | "closed";
  default_comment_status: "open" | "closed";
}

// Zod Schemas for Validation
export const CreatePostSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().min(1, "Content is required"),
  status: z.enum(["publish", "draft", "private", "future"]).default("draft"),
  excerpt: z.string().optional(),
  author: z.number().optional(),
  featured_media: z.number().optional(),
  comment_status: z.enum(["open", "closed"]).default("open"),
  ping_status: z.enum(["open", "closed"]).default("open"),
  sticky: z.boolean().default(false),
  categories: z.array(z.number()).optional(),
  tags: z.array(z.number()).optional(),
  meta: z.record(z.any()).optional(),
  date: z.string().optional(),
  slug: z.string().optional(),
  format: z.string().optional()
});

export const CreatePageSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().min(1, "Content is required"),
  status: z.enum(["publish", "draft", "private", "future"]).default("draft"),
  excerpt: z.string().optional(),
  author: z.number().optional(),
  featured_media: z.number().optional(),
  comment_status: z.enum(["open", "closed"]).default("closed"),
  ping_status: z.enum(["open", "closed"]).default("closed"),
  parent: z.number().default(0),
  menu_order: z.number().default(0),
  meta: z.record(z.any()).optional(),
  slug: z.string().optional(),
  template: z.string().optional()
});

export const UpdatePostSchema = z.object({
  id: z.number(),
  title: z.string().optional(),
  content: z.string().optional(),
  status: z.enum(["publish", "draft", "private", "future", "trash"]).optional(),
  excerpt: z.string().optional(),
  author: z.number().optional(),
  featured_media: z.number().optional(),
  comment_status: z.enum(["open", "closed"]).optional(),
  ping_status: z.enum(["open", "closed"]).optional(),
  sticky: z.boolean().optional(),
  categories: z.array(z.number()).optional(),
  tags: z.array(z.number()).optional(),
  meta: z.record(z.any()).optional(),
  date: z.string().optional(),
  slug: z.string().optional(),
  format: z.string().optional()
});

export const MediaUploadSchema = z.object({
  file: z.string().describe("Base64 encoded file content or file path"),
  filename: z.string().min(1, "Filename is required"),
  title: z.string().optional(),
  caption: z.string().optional(),
  alt_text: z.string().optional(),
  description: z.string().optional(),
  post_id: z.number().optional()
});

export const CreateCategorySchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  slug: z.string().optional(),
  parent: z.number().default(0),
  meta: z.record(z.any()).optional()
});

export const CreateTagSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  slug: z.string().optional(),
  meta: z.record(z.any()).optional()
});

// Art of Space Specific Schemas
export const ArtSpotlightSchema = z.object({
  artist_name: z.string().min(1, "Artist name is required"),
  artist_bio: z.string(),
  artwork_title: z.string().min(1, "Artwork title is required"),
  artwork_description: z.string(),
  artwork_year: z.string().optional(),
  artwork_medium: z.string().optional(),
  artwork_dimensions: z.string().optional(),
  featured_image: z.number().optional(),
  gallery_images: z.array(z.number()).optional(),
  artist_website: z.string().url().optional(),
  artist_social: z.record(z.string().url()).optional(),
  price_range: z.string().optional(),
  availability: z.enum(["available", "sold", "on_hold"]).default("available"),
  tags: z.array(z.string()).optional(),
  publish_date: z.string().optional()
});

export const CollectionAnnouncementSchema = z.object({
  collection_name: z.string().min(1, "Collection name is required"),
  collection_description: z.string(),
  artist_name: z.string().optional(),
  launch_date: z.string().optional(),
  featured_artworks: z.array(z.object({
    title: z.string(),
    description: z.string(),
    image_id: z.number().optional(),
    price: z.string().optional()
  })).optional(),
  collection_theme: z.string().optional(),
  inspiration: z.string().optional(),
  featured_image: z.number().optional(),
  gallery_images: z.array(z.number()).optional(),
  tags: z.array(z.string()).optional(),
  categories: z.array(z.string()).optional()
});

export const HowToGuideSchema = z.object({
  guide_title: z.string().min(1, "Guide title is required"),
  guide_type: z.enum(["care", "display", "framing", "lighting", "maintenance", "installation"]),
  difficulty_level: z.enum(["beginner", "intermediate", "advanced"]).default("beginner"),
  time_required: z.string().optional(),
  materials_needed: z.array(z.string()).optional(),
  steps: z.array(z.object({
    step_number: z.number(),
    title: z.string(),
    description: z.string(),
    image_id: z.number().optional(),
    tips: z.array(z.string()).optional()
  })),
  expert_tips: z.array(z.string()).optional(),
  common_mistakes: z.array(z.string()).optional(),
  featured_image: z.number().optional(),
  tags: z.array(z.string()).optional()
});

export const SeasonalContentSchema = z.object({
  season: z.enum(["spring", "summer", "fall", "winter", "holiday", "special_occasion"]),
  content_type: z.enum(["collection", "styling_tips", "gift_guide", "seasonal_trends"]),
  title: z.string().min(1, "Title is required"),
  description: z.string(),
  featured_artworks: z.array(z.object({
    title: z.string(),
    artist: z.string().optional(),
    description: z.string(),
    image_id: z.number().optional(),
    seasonal_relevance: z.string()
  })).optional(),
  styling_tips: z.array(z.string()).optional(),
  color_palette: z.array(z.string()).optional(),
  mood_description: z.string().optional(),
  featured_image: z.number().optional(),
  gallery_images: z.array(z.number()).optional(),
  tags: z.array(z.string()).optional()
});

export const ArtistInterviewSchema = z.object({
  artist_name: z.string().min(1, "Artist name is required"),
  artist_bio: z.string(),
  artist_photo: z.number().optional(),
  interview_questions: z.array(z.object({
    question: z.string(),
    answer: z.string()
  })),
  featured_artworks: z.array(z.object({
    title: z.string(),
    description: z.string(),
    image_id: z.number().optional(),
    year: z.string().optional()
  })).optional(),
  artist_influences: z.array(z.string()).optional(),
  upcoming_exhibitions: z.array(z.string()).optional(),
  artist_statement: z.string().optional(),
  contact_info: z.object({
    website: z.string().url().optional(),
    social_media: z.record(z.string().url()).optional(),
    gallery_representation: z.string().optional()
  }).optional(),
  featured_image: z.number().optional(),
  tags: z.array(z.string()).optional()
});

// Error Types
export class WordPressError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public data?: any
  ) {
    super(message);
    this.name = "WordPressError";
  }
}

export class AuthenticationError extends WordPressError {
  constructor(message: string = "Authentication failed") {
    super(message, 401);
    this.name = "AuthenticationError";
  }
}

export class NotFoundError extends WordPressError {
  constructor(message: string = "Resource not found") {
    super(message, 404);
    this.name = "NotFoundError";
  }
}

export class ValidationError extends WordPressError {
  constructor(message: string = "Validation failed") {
    super(message, 400);
    this.name = "ValidationError";
  }
}

// Configuration Types
export interface WordPressConfig {
  baseUrl: string;
  username: string;
  password: string; // Application Password
  timeout?: number;
  retries?: number;
  userAgent?: string;
}

export type PostStatus = "publish" | "draft" | "private" | "future" | "trash";
export type CommentStatus = "open" | "closed";
export type PostFormat = "standard" | "aside" | "chat" | "gallery" | "link" | "image" | "quote" | "status" | "video" | "audio";
export type MediaType = "image" | "video" | "audio" | "file";
export type UserRole = "administrator" | "editor" | "author" | "contributor" | "subscriber";