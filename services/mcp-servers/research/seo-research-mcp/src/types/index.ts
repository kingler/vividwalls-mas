/**
 * Type Definitions
 * 
 * Common TypeScript types and interfaces for the SEO Research MCP Server
 */

/**
 * API Response wrapper type
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: string;
    duration?: number;
    source?: string;
    cached?: boolean;
  };
}

/**
 * Keyword research data structure
 */
export interface KeywordData {
  keyword: string;
  searchVolume?: number;
  cpc?: number;
  competition?: number;
  competitionLevel?: 'LOW' | 'MEDIUM' | 'HIGH';
  difficulty?: number;
  trends?: Array<{
    month: number;
    year: number;
    searchVolume: number;
  }>;
  relatedKeywords?: string[];
  source: string;
}

/**
 * Backlink data structure
 */
export interface BacklinkData {
  urlFrom: string;
  urlTo: string;
  domainFrom: string;
  anchor: string;
  linkType: 'dofollow' | 'nofollow';
  authority?: number;
  firstSeen?: string;
  lastSeen?: string;
  source: string;
}

/**
 * SERP (Search Engine Results Page) data structure
 */
export interface SerpData {
  keyword: string;
  location?: string;
  language?: string;
  results: Array<{
    position: number;
    url: string;
    title: string;
    description: string;
    domain: string;
    type: 'organic' | 'paid' | 'featured_snippet' | 'local' | 'image' | 'video';
  }>;
  totalResults?: number;
  searchTime?: number;
  source: string;
}

/**
 * Content extraction result
 */
export interface ContentData {
  url: string;
  title?: string;
  content: string;
  metadata?: {
    description?: string;
    keywords?: string[];
    author?: string;
    publishDate?: string;
    wordCount?: number;
    language?: string;
  };
  extractedAt: string;
  source: string;
}

/**
 * Competitor analysis data
 */
export interface CompetitorData {
  domain: string;
  keywords: KeywordData[];
  backlinks: BacklinkData[];
  rankings: Array<{
    keyword: string;
    position: number;
    url: string;
  }>;
  metrics?: {
    domainAuthority?: number;
    organicTraffic?: number;
    organicKeywords?: number;
    backlinksCount?: number;
  };
  source: string;
}

/**
 * Cache entry structure
 */
export interface CacheEntry<T = any> {
  key: string;
  data: T;
  timestamp: number;
  ttl: number;
  source?: string;
}

/**
 * Rate limiting information
 */
export interface RateLimitInfo {
  service: string;
  limit: number;
  remaining: number;
  resetTime: number;
  windowMs: number;
}

/**
 * API client configuration
 */
export interface ApiClientConfig {
  apiKey: string;
  baseUrl: string;
  timeout: number;
  retries?: number;
  retryDelay?: number;
}

/**
 * Search parameters for various APIs
 */
export interface SearchParams {
  query?: string;
  keywords?: string[];
  location?: string;
  language?: string;
  country?: string;
  limit?: number;
  offset?: number;
  includeSubdomains?: boolean;
  dateRange?: {
    from: string;
    to: string;
  };
}

/**
 * Error types for better error handling
 */
export enum ErrorType {
  API_ERROR = 'API_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  CACHE_ERROR = 'CACHE_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

/**
 * Custom error class for API operations
 */
export class SeoResearchError extends Error {
  public readonly type: ErrorType;
  public readonly code: string;
  public readonly details?: any;

  constructor(
    message: string,
    type: ErrorType = ErrorType.UNKNOWN_ERROR,
    code?: string,
    details?: any
  ) {
    super(message);
    this.name = 'SeoResearchError';
    this.type = type;
    this.code = code || type;
    this.details = details;
  }
}

/**
 * Health check status
 */
export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  server: {
    name: string;
    version: string;
    uptime: number;
    memory: NodeJS.MemoryUsage;
  };
  apis: {
    configured: string[];
    count: number;
    connectivity?: Record<string, 'configured' | 'not_configured' | 'error'>;
  };
  cache?: {
    status: 'connected' | 'disconnected' | 'error';
    hitRate?: number;
    size?: number;
  };
} 