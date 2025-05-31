import axios, { AxiosInstance, AxiosResponse } from "axios";
import FormData from "form-data";
import { readFileSync } from "fs";
import { parse } from "node-html-parser";
import slug from "slug";
import {
  WordPressConfig,
  WordPressPost,
  WordPressPage,
  WordPressMedia,
  WordPressCategory,
  WordPressTag,
  WordPressUser,
  WordPressPlugin,
  WordPressTheme,
  WordPressSiteInfo,
  WordPressError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  PostStatus,
  MediaType
} from "./types.js";

export class WordPressClient {
  private axios: AxiosInstance;
  private config: WordPressConfig;

  constructor(config: WordPressConfig) {
    this.config = {
      timeout: 30000,
      retries: 3,
      userAgent: "VividWalls WordPress MCP Server/1.0.0",
      ...config
    };

    this.axios = axios.create({
      baseURL: `${this.config.baseUrl}/wp-json/wp/v2`,
      timeout: this.config.timeout,
      headers: {
        "User-Agent": this.config.userAgent,
        "Content-Type": "application/json"
      },
      auth: {
        username: this.config.username,
        password: this.config.password
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for logging
    this.axios.interceptors.request.use(
      (config) => {
        console.error(`WordPress API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          const { status, data } = error.response;
          
          switch (status) {
            case 401:
            case 403:
              throw new AuthenticationError(
                data?.message || "Authentication failed. Check your username and application password."
              );
            case 404:
              throw new NotFoundError(data?.message || "Resource not found");
            case 400:
              throw new ValidationError(data?.message || "Invalid request data");
            default:
              throw new WordPressError(
                data?.message || `HTTP ${status} error`,
                status,
                data
              );
          }
        } else if (error.request) {
          throw new WordPressError(
            "Network error: Unable to reach WordPress site. Check your baseUrl.",
            0
          );
        } else {
          throw new WordPressError(error.message);
        }
      }
    );
  }

  // Posts Management
  async getPosts(params: {
    page?: number;
    per_page?: number;
    search?: string;
    author?: number;
    categories?: number[];
    tags?: number[];
    status?: PostStatus[];
    orderby?: string;
    order?: "asc" | "desc";
    before?: string;
    after?: string;
  } = {}): Promise<{ posts: WordPressPost[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/posts", { params });
      
      return {
        posts: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch posts", error);
    }
  }

  async getPost(id: number): Promise<WordPressPost> {
    try {
      const response = await this.axios.get(`/posts/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to fetch post ${id}`, error);
    }
  }

  async createPost(postData: Partial<WordPressPost>): Promise<WordPressPost> {
    try {
      const response = await this.axios.post("/posts", postData);
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to create post", error);
    }
  }

  async updatePost(id: number, postData: Partial<WordPressPost>): Promise<WordPressPost> {
    try {
      const response = await this.axios.post(`/posts/${id}`, postData);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update post ${id}`, error);
    }
  }

  async deletePost(id: number, force: boolean = false): Promise<{ deleted: boolean; previous: WordPressPost }> {
    try {
      const response = await this.axios.delete(`/posts/${id}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete post ${id}`, error);
    }
  }

  async schedulePost(id: number, publishDate: string): Promise<WordPressPost> {
    try {
      const response = await this.axios.post(`/posts/${id}`, {
        status: "future",
        date: publishDate
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to schedule post ${id}`, error);
    }
  }

  // Pages Management
  async getPages(params: {
    page?: number;
    per_page?: number;
    search?: string;
    author?: number;
    parent?: number;
    status?: PostStatus[];
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ pages: WordPressPage[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/pages", { params });
      
      return {
        pages: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch pages", error);
    }
  }

  async createPage(pageData: Partial<WordPressPage>): Promise<WordPressPage> {
    try {
      const response = await this.axios.post("/pages", pageData);
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to create page", error);
    }
  }

  async updatePage(id: number, pageData: Partial<WordPressPage>): Promise<WordPressPage> {
    try {
      const response = await this.axios.post(`/pages/${id}`, pageData);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update page ${id}`, error);
    }
  }

  async deletePage(id: number, force: boolean = false): Promise<{ deleted: boolean; previous: WordPressPage }> {
    try {
      const response = await this.axios.delete(`/pages/${id}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete page ${id}`, error);
    }
  }

  // Media Management
  async getMedia(params: {
    page?: number;
    per_page?: number;
    search?: string;
    author?: number;
    parent?: number;
    media_type?: MediaType;
    mime_type?: string;
  } = {}): Promise<{ media: WordPressMedia[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/media", { params });
      
      return {
        media: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch media", error);
    }
  }

  async uploadMedia(file: {
    content: Buffer | string;
    filename: string;
    title?: string;
    caption?: string;
    alt_text?: string;
    description?: string;
    post_id?: number;
  }): Promise<WordPressMedia> {
    try {
      const formData = new FormData();
      
      // Handle file content
      let fileBuffer: Buffer;
      if (typeof file.content === "string") {
        // Check if it's a base64 string
        if (file.content.startsWith("data:")) {
          const base64Data = file.content.split(",")[1];
          fileBuffer = Buffer.from(base64Data, "base64");
        } else {
          // Assume it's a file path
          fileBuffer = readFileSync(file.content);
        }
      } else {
        fileBuffer = file.content;
      }

      formData.append("file", fileBuffer, file.filename);
      
      if (file.title) formData.append("title", file.title);
      if (file.caption) formData.append("caption", file.caption);
      if (file.alt_text) formData.append("alt_text", file.alt_text);
      if (file.description) formData.append("description", file.description);
      if (file.post_id) formData.append("post", file.post_id.toString());

      const response = await this.axios.post("/media", formData, {
        headers: {
          ...formData.getHeaders(),
          "Content-Type": "multipart/form-data"
        }
      });

      return response.data;
    } catch (error) {
      throw this.handleError("Failed to upload media", error);
    }
  }

  async deleteMedia(id: number, force: boolean = false): Promise<{ deleted: boolean; previous: WordPressMedia }> {
    try {
      const response = await this.axios.delete(`/media/${id}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete media ${id}`, error);
    }
  }

  // Categories Management
  async getCategories(params: {
    page?: number;
    per_page?: number;
    search?: string;
    parent?: number;
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ categories: WordPressCategory[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/categories", { params });
      
      return {
        categories: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch categories", error);
    }
  }

  async createCategory(categoryData: {
    name: string;
    description?: string;
    slug?: string;
    parent?: number;
  }): Promise<WordPressCategory> {
    try {
      const data = {
        ...categoryData,
        slug: categoryData.slug || slug(categoryData.name)
      };
      
      const response = await this.axios.post("/categories", data);
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to create category", error);
    }
  }

  async updateCategory(id: number, categoryData: Partial<WordPressCategory>): Promise<WordPressCategory> {
    try {
      const response = await this.axios.post(`/categories/${id}`, categoryData);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update category ${id}`, error);
    }
  }

  async deleteCategory(id: number, force: boolean = false): Promise<{ deleted: boolean; previous: WordPressCategory }> {
    try {
      const response = await this.axios.delete(`/categories/${id}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete category ${id}`, error);
    }
  }

  // Tags Management
  async getTags(params: {
    page?: number;
    per_page?: number;
    search?: string;
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ tags: WordPressTag[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/tags", { params });
      
      return {
        tags: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch tags", error);
    }
  }

  async createTag(tagData: {
    name: string;
    description?: string;
    slug?: string;
  }): Promise<WordPressTag> {
    try {
      const data = {
        ...tagData,
        slug: tagData.slug || slug(tagData.name)
      };
      
      const response = await this.axios.post("/tags", data);
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to create tag", error);
    }
  }

  // Users Management
  async getUsers(params: {
    page?: number;
    per_page?: number;
    search?: string;
    roles?: string[];
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ users: WordPressUser[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/users", { params });
      
      return {
        users: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch users", error);
    }
  }

  async getCurrentUser(): Promise<WordPressUser> {
    try {
      const response = await this.axios.get("/users/me");
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to fetch current user", error);
    }
  }

  // Site Management
  async getSiteInfo(): Promise<WordPressSiteInfo> {
    try {
      const response = await this.axios.get("/settings");
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to fetch site info", error);
    }
  }

  async updateSiteInfo(settings: Partial<WordPressSiteInfo>): Promise<WordPressSiteInfo> {
    try {
      const response = await this.axios.post("/settings", settings);
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to update site info", error);
    }
  }

  // API Discovery - Inspired by server-wp-mcp
  async discoverEndpoints(): Promise<{
    namespaces: string[];
    routes: Record<string, any>;
    site_info: {
      name: string;
      description: string;
      url: string;
      home: string;
      gmt_offset: number;
      timezone_string: string;
    };
  }> {
    try {
      const response = await this.axios.get("/", {
        baseURL: `${this.config.baseUrl}/wp-json`
      });
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to discover API endpoints", error);
    }
  }

  async callEndpoint(params: {
    endpoint: string;
    method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
    data?: any;
    query_params?: Record<string, any>;
  }): Promise<any> {
    try {
      const { endpoint, method = "GET", data, query_params } = params;
      
      const config: any = {
        method: method.toLowerCase(),
        url: endpoint,
        baseURL: `${this.config.baseUrl}/wp-json`,
      };

      if (query_params) {
        config.params = query_params;
      }

      if (data && ["POST", "PUT", "PATCH"].includes(method)) {
        config.data = data;
      }

      const response = await this.axios.request(config);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to call endpoint ${params.endpoint}`, error);
    }
  }

  // Enhanced Plugin Management with installation support
  async getPlugins(): Promise<WordPressPlugin[]> {
    try {
      const response = await this.axios.get("/plugins", {
        baseURL: `${this.config.baseUrl}/wp-json/wp/v2`
      });
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to fetch plugins", error);
    }
  }

  async getPlugin(plugin: string): Promise<WordPressPlugin> {
    try {
      const response = await this.axios.get(`/plugins/${plugin}`, {
        baseURL: `${this.config.baseUrl}/wp-json/wp/v2`
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to fetch plugin ${plugin}`, error);
    }
  }

  async activatePlugin(plugin: string): Promise<WordPressPlugin> {
    try {
      const response = await this.axios.post(`/plugins/${plugin}`, {
        status: "active"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to activate plugin ${plugin}`, error);
    }
  }

  async deactivatePlugin(plugin: string): Promise<WordPressPlugin> {
    try {
      const response = await this.axios.post(`/plugins/${plugin}`, {
        status: "inactive"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to deactivate plugin ${plugin}`, error);
    }
  }

  async updatePlugin(plugin: string): Promise<WordPressPlugin> {
    try {
      const response = await this.axios.post(`/plugins/${plugin}`, {
        // WordPress REST API doesn't directly support plugin updates
        // This would typically require WP CLI or additional plugin
        action: "update"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update plugin ${plugin}`, error);
    }
  }

  async deletePlugin(plugin: string): Promise<{ deleted: boolean; previous: WordPressPlugin }> {
    try {
      const response = await this.axios.delete(`/plugins/${plugin}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete plugin ${plugin}`, error);
    }
  }

  // Enhanced Theme Management
  async getThemes(): Promise<WordPressTheme[]> {
    try {
      const response = await this.axios.get("/themes");
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to fetch themes", error);
    }
  }

  async getTheme(theme: string): Promise<WordPressTheme> {
    try {
      const response = await this.axios.get(`/themes/${theme}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to fetch theme ${theme}`, error);
    }
  }

  async getActiveTheme(): Promise<WordPressTheme> {
    try {
      const themes = await this.getThemes();
      const activeTheme = themes.find(theme => theme.status === "active");
      if (!activeTheme) {
        throw new NotFoundError("No active theme found");
      }
      return activeTheme;
    } catch (error) {
      throw this.handleError("Failed to fetch active theme", error);
    }
  }

  async activateTheme(theme: string): Promise<WordPressTheme> {
    try {
      const response = await this.axios.post(`/themes/${theme}`, {
        status: "active"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to activate theme ${theme}`, error);
    }
  }

  async updateTheme(theme: string): Promise<WordPressTheme> {
    try {
      const response = await this.axios.post(`/themes/${theme}`, {
        action: "update"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update theme ${theme}`, error);
    }
  }

  async deleteTheme(theme: string): Promise<{ deleted: boolean; previous: WordPressTheme }> {
    try {
      const response = await this.axios.delete(`/themes/${theme}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete theme ${theme}`, error);
    }
  }

  // Custom Post Types Management
  async getPostTypes(): Promise<any[]> {
    try {
      const response = await this.axios.get("/types");
      return Object.values(response.data);
    } catch (error) {
      throw this.handleError("Failed to fetch post types", error);
    }
  }

  async getPostType(type: string): Promise<any> {
    try {
      const response = await this.axios.get(`/types/${type}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to fetch post type ${type}`, error);
    }
  }

  async getCustomPosts(postType: string, params: {
    page?: number;
    per_page?: number;
    search?: string;
    author?: number;
    status?: PostStatus[];
    orderby?: string;
    order?: "asc" | "desc";
    meta_query?: any;
  } = {}): Promise<{ posts: any[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get(`/${postType}`, { params });
      
      return {
        posts: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError(`Failed to fetch ${postType} posts`, error);
    }
  }

  async createCustomPost(postType: string, postData: any): Promise<any> {
    try {
      const response = await this.axios.post(`/${postType}`, postData);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to create ${postType} post`, error);
    }
  }

  async updateCustomPost(postType: string, id: number, postData: any): Promise<any> {
    try {
      const response = await this.axios.post(`/${postType}/${id}`, postData);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update ${postType} post ${id}`, error);
    }
  }

  async deleteCustomPost(postType: string, id: number, force: boolean = false): Promise<{ deleted: boolean; previous: any }> {
    try {
      const response = await this.axios.delete(`/${postType}/${id}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete ${postType} post ${id}`, error);
    }
  }

  // Custom Fields (Meta) Management
  async getPostMeta(postId: number): Promise<Record<string, any>> {
    try {
      const response = await this.axios.get(`/posts/${postId}/meta`);
      const metaArray = response.data;
      const metaObject: Record<string, any> = {};
      
      metaArray.forEach((meta: any) => {
        metaObject[meta.key] = meta.value;
      });
      
      return metaObject;
    } catch (error) {
      throw this.handleError(`Failed to fetch meta for post ${postId}`, error);
    }
  }

  async updatePostMeta(postId: number, metaKey: string, metaValue: any): Promise<any> {
    try {
      const response = await this.axios.post(`/posts/${postId}/meta`, {
        key: metaKey,
        value: metaValue
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to update meta ${metaKey} for post ${postId}`, error);
    }
  }

  async deletePostMeta(postId: number, metaId: number): Promise<{ deleted: boolean; previous: any }> {
    try {
      const response = await this.axios.delete(`/posts/${postId}/meta/${metaId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete meta ${metaId} for post ${postId}`, error);
    }
  }

  // Taxonomies Management (Categories and Tags extended)
  async getTaxonomies(): Promise<any[]> {
    try {
      const response = await this.axios.get("/taxonomies");
      return Object.values(response.data);
    } catch (error) {
      throw this.handleError("Failed to fetch taxonomies", error);
    }
  }

  async getTaxonomy(taxonomy: string): Promise<any> {
    try {
      const response = await this.axios.get(`/taxonomies/${taxonomy}`);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to fetch taxonomy ${taxonomy}`, error);
    }
  }

  async getTerms(taxonomy: string, params: {
    page?: number;
    per_page?: number;
    search?: string;
    parent?: number;
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ terms: any[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get(`/${taxonomy}`, { params });
      
      return {
        terms: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError(`Failed to fetch ${taxonomy} terms`, error);
    }
  }

  async createTerm(taxonomy: string, termData: {
    name: string;
    description?: string;
    slug?: string;
    parent?: number;
  }): Promise<any> {
    try {
      const data = {
        ...termData,
        slug: termData.slug || slug(termData.name)
      };
      
      const response = await this.axios.post(`/${taxonomy}`, data);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to create ${taxonomy} term`, error);
    }
  }

  // Comments Management
  async getComments(params: {
    page?: number;
    per_page?: number;
    search?: string;
    author?: number;
    author_email?: string;
    post?: number;
    parent?: number;
    status?: string;
    type?: string;
    orderby?: string;
    order?: "asc" | "desc";
  } = {}): Promise<{ comments: any[]; totalPages: number; total: number }> {
    try {
      const response = await this.axios.get("/comments", { params });
      
      return {
        comments: response.data,
        totalPages: parseInt(response.headers["x-wp-totalpages"] || "1"),
        total: parseInt(response.headers["x-wp-total"] || "0")
      };
    } catch (error) {
      throw this.handleError("Failed to fetch comments", error);
    }
  }

  async approveComment(commentId: number): Promise<any> {
    try {
      const response = await this.axios.post(`/comments/${commentId}`, {
        status: "approved"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to approve comment ${commentId}`, error);
    }
  }

  async rejectComment(commentId: number): Promise<any> {
    try {
      const response = await this.axios.post(`/comments/${commentId}`, {
        status: "hold"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to reject comment ${commentId}`, error);
    }
  }

  async spamComment(commentId: number): Promise<any> {
    try {
      const response = await this.axios.post(`/comments/${commentId}`, {
        status: "spam"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to mark comment ${commentId} as spam`, error);
    }
  }

  async deleteComment(commentId: number, force: boolean = false): Promise<{ deleted: boolean; previous: any }> {
    try {
      const response = await this.axios.delete(`/comments/${commentId}`, {
        params: { force }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to delete comment ${commentId}`, error);
    }
  }

  // Utility Methods
  async searchContent(query: string, types: ("posts" | "pages" | "media")[] = ["posts", "pages"]): Promise<{
    posts?: WordPressPost[];
    pages?: WordPressPage[];
    media?: WordPressMedia[];
  }> {
    const results: any = {};

    try {
      for (const type of types) {
        const response = await this.axios.get(`/${type}`, {
          params: { search: query, per_page: 20 }
        });
        results[type] = response.data;
      }
      return results;
    } catch (error) {
      throw this.handleError(`Failed to search content for "${query}"`, error);
    }
  }

  async getPostStats(id: number): Promise<{
    views?: number;
    comments: number;
    likes?: number;
    shares?: number;
  }> {
    try {
      // Get basic post data
      const post = await this.getPost(id);
      
      // Get comments count
      const commentsResponse = await this.axios.get("/comments", {
        params: { post: id, per_page: 1 }
      });
      const commentsCount = parseInt(commentsResponse.headers["x-wp-total"] || "0");

      return {
        comments: commentsCount
      };
    } catch (error) {
      throw this.handleError(`Failed to get stats for post ${id}`, error);
    }
  }

  async bulkUpdatePosts(updates: Array<{ id: number; data: Partial<WordPressPost> }>): Promise<WordPressPost[]> {
    try {
      const promises = updates.map(update => 
        this.updatePost(update.id, update.data)
      );
      return await Promise.all(promises);
    } catch (error) {
      throw this.handleError("Failed to bulk update posts", error);
    }
  }

  // Content optimization helpers
  generateSEOTitle(title: string, maxLength: number = 60): string {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength - 3) + "...";
  }

  generateExcerpt(content: string, maxLength: number = 155): string {
    // Strip HTML tags
    const textContent = parse(content).text;
    if (textContent.length <= maxLength) return textContent;
    
    // Find the last complete sentence within the limit
    const truncated = textContent.substring(0, maxLength);
    const lastSentence = truncated.lastIndexOf(".");
    
    if (lastSentence > maxLength * 0.7) {
      return truncated.substring(0, lastSentence + 1);
    }
    
    return truncated.substring(0, maxLength - 3) + "...";
  }

  generateSlug(title: string): string {
    return slug(title, { lower: true });
  }

  private handleError(message: string, error: any): WordPressError {
    if (error instanceof WordPressError) {
      return error;
    }
    
    console.error(`WordPress API Error: ${message}`, error);
    return new WordPressError(message, error?.response?.status, error?.response?.data);
  }

  // Gutenberg Block Editor Support
  async getBlocks(postId: number): Promise<any[]> {
    try {
      const post = await this.getPost(postId);
      const content = post.content?.rendered || "";
      
      // Parse Gutenberg blocks from content
      // This is a simplified parser - in production, you'd want to use wp-block-parser
      const blockPattern = /<!-- wp:([^/\s]+)(?:\s+({[^}]*}))?\s*(?:\/-->|-->)/g;
      const blocks: any[] = [];
      let match;
      
      while ((match = blockPattern.exec(content)) !== null) {
        const blockName = match[1];
        const attributes = match[2] ? JSON.parse(match[2]) : {};
        
        blocks.push({
          blockName: `core/${blockName}`,
          attrs: attributes,
          innerBlocks: [],
          innerHTML: '',
          innerContent: []
        });
      }
      
      return blocks;
    } catch (error) {
      throw this.handleError(`Failed to get blocks for post ${postId}`, error);
    }
  }

  async updateBlocks(postId: number, blocks: any[]): Promise<WordPressPost> {
    try {
      // Convert blocks back to HTML
      // This is a simplified converter - in production, you'd want to use proper serialization
      let content = blocks.map(block => {
        const attributes = Object.keys(block.attrs || {}).length > 0 
          ? ` ${JSON.stringify(block.attrs)}` 
          : '';
        return `<!-- wp:${block.blockName.replace('core/', '')}${attributes} -->
${block.innerHTML || ''}
<!-- /wp:${block.blockName.replace('core/', '')} -->`;
      }).join('\n\n');

      return await this.updatePost(postId, {
        content: { rendered: content, protected: false }
      });
    } catch (error) {
      throw this.handleError(`Failed to update blocks for post ${postId}`, error);
    }
  }

  async addBlock(postId: number, blockData: {
    blockName: string;
    attrs?: any;
    innerHTML?: string;
    position?: number;
  }): Promise<WordPressPost> {
    try {
      const blocks = await this.getBlocks(postId);
      const newBlock = {
        blockName: blockData.blockName,
        attrs: blockData.attrs || {},
        innerHTML: blockData.innerHTML || '',
        innerBlocks: [],
        innerContent: []
      };

      if (blockData.position !== undefined && blockData.position < blocks.length) {
        blocks.splice(blockData.position, 0, newBlock);
      } else {
        blocks.push(newBlock);
      }

      return await this.updateBlocks(postId, blocks);
    } catch (error) {
      throw this.handleError(`Failed to add block to post ${postId}`, error);
    }
  }

  async removeBlock(postId: number, blockIndex: number): Promise<WordPressPost> {
    try {
      const blocks = await this.getBlocks(postId);
      
      if (blockIndex >= 0 && blockIndex < blocks.length) {
        blocks.splice(blockIndex, 1);
        return await this.updateBlocks(postId, blocks);
      } else {
        throw new ValidationError("Invalid block index");
      }
    } catch (error) {
      throw this.handleError(`Failed to remove block from post ${postId}`, error);
    }
  }

  // WordPress Multisite Support
  async getNetworkSites(): Promise<any[]> {
    try {
      // WordPress multisite network sites endpoint
      const response = await this.axios.get("/sites", {
        baseURL: `${this.config.baseUrl}/wp-json/wp/v2`
      });
      return response.data;
    } catch (error) {
      // If not a multisite or endpoint doesn't exist, return current site info
      const siteInfo = await this.getSiteInfo();
      return [{
        id: 1,
        url: this.config.baseUrl,
        name: siteInfo.name,
        description: siteInfo.description
      }];
    }
  }

  async switchToSite(siteId: number): Promise<void> {
    try {
      // This would require updating the base URL for multisite
      // In a real implementation, you'd manage multiple configurations
      console.log(`Switching to site ${siteId} - functionality requires proper multisite setup`);
    } catch (error) {
      throw this.handleError(`Failed to switch to site ${siteId}`, error);
    }
  }

  async getNetworkPlugins(): Promise<any[]> {
    try {
      const response = await this.axios.get("/plugins", {
        baseURL: `${this.config.baseUrl}/wp-json/wp/v2`,
        params: { status: "network-active" }
      });
      return response.data;
    } catch (error) {
      throw this.handleError("Failed to fetch network plugins", error);
    }
  }

  async networkActivatePlugin(plugin: string): Promise<any> {
    try {
      const response = await this.axios.post(`/plugins/${plugin}`, {
        status: "network-active"
      });
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to network activate plugin ${plugin}`, error);
    }
  }

  // Advanced WordPress Features for VividWalls
  async createProductPost(productData: {
    title: string;
    description: string;
    price: number;
    artist: string;
    dimensions: string;
    medium: string;
    year?: string;
    image_gallery: number[];
    featured_image: number;
    categories: string[];
    tags: string[];
    availability: "available" | "sold" | "on_hold";
    sku?: string;
  }): Promise<WordPressPost> {
    try {
      const postData: Partial<WordPressPost> = {
        title: { rendered: productData.title },
        content: { rendered: this.generateProductDescription(productData), protected: false },
        status: "publish" as PostStatus,
        featured_media: productData.featured_image,
        meta: {
          _product_price: productData.price,
          _product_artist: productData.artist,
          _product_dimensions: productData.dimensions,
          _product_medium: productData.medium,
          _product_year: productData.year,
          _product_gallery: productData.image_gallery,
          _product_availability: productData.availability,
          _product_sku: productData.sku || this.generateSKU(productData.title)
        }
      };

      // Create or get categories
      const categoryIds = await this.ensureCategories(productData.categories);
      const tagIds = await this.ensureTags(productData.tags);

      postData.categories = categoryIds;
      postData.tags = tagIds;

      return await this.createPost(postData);
    } catch (error) {
      throw this.handleError("Failed to create product post", error);
    }
  }

  private generateProductDescription(productData: any): string {
    return `
<div class="product-description">
  <h3>About This Artwork</h3>
  <p>${productData.description}</p>
  
  <div class="product-details">
    <h4>Artwork Details</h4>
    <ul>
      <li><strong>Artist:</strong> ${productData.artist}</li>
      <li><strong>Dimensions:</strong> ${productData.dimensions}</li>
      <li><strong>Medium:</strong> ${productData.medium}</li>
      ${productData.year ? `<li><strong>Year:</strong> ${productData.year}</li>` : ''}
      <li><strong>Availability:</strong> ${productData.availability}</li>
    </ul>
  </div>
  
  <div class="product-pricing">
    <h4>Pricing</h4>
    <p class="price">$${productData.price.toLocaleString()}</p>
  </div>
</div>
    `.trim();
  }

  private generateSKU(title: string): string {
    const cleanTitle = title.replace(/[^a-zA-Z0-9]/g, '').substring(0, 8).toUpperCase();
    const timestamp = Date.now().toString().slice(-4);
    return `VW-${cleanTitle}-${timestamp}`;
  }

  private async ensureCategories(categoryNames: string[]): Promise<number[]> {
    const categoryIds: number[] = [];
    
    for (const name of categoryNames) {
      try {
        const existingCats = await this.getCategories({ search: name });
        let categoryId: number;
        
        if (existingCats.categories.length > 0) {
          categoryId = existingCats.categories[0].id;
        } else {
          const newCategory = await this.createCategory({ name });
          categoryId = newCategory.id;
        }
        
        categoryIds.push(categoryId);
      } catch (error) {
        console.warn(`Failed to create/find category "${name}":`, error);
      }
    }
    
    return categoryIds;
  }

  private async ensureTags(tagNames: string[]): Promise<number[]> {
    const tagIds: number[] = [];
    
    for (const name of tagNames) {
      try {
        const existingTags = await this.getTags({ search: name });
        let tagId: number;
        
        if (existingTags.tags.length > 0) {
          tagId = existingTags.tags[0].id;
        } else {
          const newTag = await this.createTag({ name });
          tagId = newTag.id;
        }
        
        tagIds.push(tagId);
      } catch (error) {
        console.warn(`Failed to create/find tag "${name}":`, error);
      }
    }
    
    return tagIds;
  }

  // SEO and Performance optimization for VividWalls
  async optimizeImageSEO(mediaId: number, optimizations: {
    alt_text?: string;
    title?: string;
    caption?: string;
    description?: string;
  }): Promise<WordPressMedia> {
    try {
      const response = await this.axios.post(`/media/${mediaId}`, optimizations);
      return response.data;
    } catch (error) {
      throw this.handleError(`Failed to optimize SEO for media ${mediaId}`, error);
    }
  }

  async generateSchemaMarkup(postId: number): Promise<string> {
    try {
      const post = await this.getPost(postId);
      const meta = await this.getPostMeta(postId);
      
      if (meta._product_price) {
        // Generate product schema for artwork
        const schema = {
          "@context": "https://schema.org/",
          "@type": "Product",
          "name": post.title.rendered,
          "description": this.generateExcerpt(post.content.rendered, 160),
          "image": post.featured_media ? `${this.config.baseUrl}/wp-content/uploads/...` : undefined,
          "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": meta._product_price,
            "availability": meta._product_availability === "available" 
              ? "https://schema.org/InStock" 
              : "https://schema.org/OutOfStock"
          },
          "brand": {
            "@type": "Brand",
            "name": "VividWalls"
          },
          "category": "Artwork"
        };
        
        return JSON.stringify(schema, null, 2);
      }
      
      return "";
    } catch (error) {
      throw this.handleError(`Failed to generate schema markup for post ${postId}`, error);
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: "ok" | "error"; message: string; details?: any }> {
    try {
      const user = await this.getCurrentUser();
      const endpoints = await this.discoverEndpoints();
      
      return {
        status: "ok",
        message: `Connected as ${user.name} (${user.username})`,
        details: {
          user: user.username,
          roles: user.roles,
          site: this.config.baseUrl,
          namespaces: endpoints.namespaces,
          capabilities: {
            plugins: endpoints.namespaces.includes("wp/v2"),
            themes: endpoints.namespaces.includes("wp/v2"),
            customPosts: endpoints.namespaces.includes("wp/v2"),
            multisite: endpoints.routes["/wp/v2/sites"] !== undefined
          }
        }
      };
    } catch (error) {
      return {
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
        details: error
      };
    }
  }
}