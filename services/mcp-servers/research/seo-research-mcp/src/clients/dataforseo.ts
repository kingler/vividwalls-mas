/**
 * DataForSEO API Client
 * 
 * Comprehensive client for DataForSEO APIs including Keywords Data, SERP, and Backlinks
 * Based on DataForSEO API v3 documentation
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { config } from '../config/index.js';
import { logger } from '../server/logger.js';
import { 
  ApiResponse, 
  KeywordData, 
  BacklinkData, 
  SerpData, 
  ErrorType, 
  SeoResearchError 
} from '../types/index.js';

/**
 * DataForSEO API response structure
 */
interface DataForSEOResponse<T = any> {
  version: string;
  status_code: number;
  status_message: string;
  time: string;
  cost: number;
  tasks_count: number;
  tasks_error: number;
  tasks: Array<{
    id: string;
    status_code: number;
    status_message: string;
    time: string;
    cost: number;
    result_count: number;
    path: string[];
    data: T;
    result?: any[];
  }>;
}

/**
 * Keyword research parameters
 */
export interface KeywordResearchParams {
  keywords: string[];
  location_name?: string | undefined;
  location_code?: number;
  language_name?: string | undefined;
  language_code?: string;
  search_partners?: boolean;
  date_from?: string;
  date_to?: string;
  include_serp_info?: boolean;
  include_clickstream_data?: boolean;
  include_subdomains?: boolean;
  limit?: number;
  offset?: number;
}

/**
 * Backlink analysis parameters
 */
export interface BacklinkAnalysisParams {
  target: string;
  mode?: 'as_is' | 'one_per_domain' | 'one_per_anchor';
  filters?: Array<[string, string, any]>;
  order_by?: string[];
  limit?: number;
  offset?: number;
  backlinks_status_type?: 'all' | 'live' | 'lost';
  include_subdomains?: boolean;
  include_indirect_links?: boolean;
  exclude_internal_backlinks?: boolean;
}

/**
 * SERP analysis parameters
 */
export interface SerpAnalysisParams {
  keyword: string;
  location_name?: string | undefined;
  location_code?: number;
  language_name?: string | undefined;
  language_code?: string;
  device?: 'desktop' | 'mobile';
  os?: 'windows' | 'macos' | 'android' | 'ios';
  depth?: number;
  max_crawl_pages?: number;
  search_param?: string;
  calculate_rectangles?: boolean;
}

/**
 * DataForSEO API Client
 */
export class DataForSEOClient {
  private client: AxiosInstance;
  private apiConfig: ReturnType<typeof config.getApiConfig>;

  constructor() {
    this.apiConfig = config.getApiConfig('dataForSEO');
    
    // Create axios instance with authentication
    this.client = axios.create({
      baseURL: this.apiConfig.baseUrl,
      timeout: this.apiConfig.timeout,
      auth: {
        username: this.apiConfig.apiKey.split(':')[0] || '',
        password: this.apiConfig.apiKey.split(':')[1] || '',
      },
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'SEO-Research-MCP/0.1.0',
      },
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        logger.apiRequest('DataForSEO', config.url || '', config.data);
        return config;
      },
      (error) => {
        logger.error('DataForSEO request error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging and error handling
    this.client.interceptors.response.use(
      (response) => {
        logger.apiResponse('DataForSEO', response.config.url || '', response.status);
        return response;
      },
      (error) => {
        const status = error.response?.status || 0;
        logger.apiResponse('DataForSEO', error.config?.url || '', status);
        
        if (status === 401) {
          throw new SeoResearchError(
            'DataForSEO authentication failed. Please check your API credentials.',
            ErrorType.AUTHENTICATION_ERROR,
            'DATAFORSEO_AUTH_ERROR',
            { status, response: error.response?.data }
          );
        } else if (status === 429) {
          throw new SeoResearchError(
            'DataForSEO rate limit exceeded. Please try again later.',
            ErrorType.RATE_LIMIT_ERROR,
            'DATAFORSEO_RATE_LIMIT',
            { status, retryAfter: error.response?.headers['retry-after'] }
          );
        } else if (status >= 500) {
          throw new SeoResearchError(
            'DataForSEO server error. Please try again later.',
            ErrorType.API_ERROR,
            'DATAFORSEO_SERVER_ERROR',
            { status, response: error.response?.data }
          );
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * Research keywords using DataForSEO Keywords Data API
   */
  async researchKeywords(params: KeywordResearchParams): Promise<ApiResponse<KeywordData[]>> {
    const startTime = Date.now();
    
    try {
      logger.info('🔍 Starting keyword research', { keywords: params.keywords });

      // Prepare request payload for DataForSEO Keywords Data API
      const payload = [{
        keywords: params.keywords,
        location_name: params.location_name || 'United States',
        language_name: params.language_name || 'English',
        search_partners: params.search_partners ?? false,
        include_serp_info: params.include_serp_info ?? true,
        include_clickstream_data: params.include_clickstream_data ?? true,
        limit: params.limit || 1000,
        offset: params.offset || 0,
      }];

      const response: AxiosResponse<DataForSEOResponse> = await this.client.post(
        '/keywords_data/google_ads/search_volume/live',
        payload
      );

      const duration = Date.now() - startTime;
      logger.performance('keyword_research', duration, { 
        keywords_count: params.keywords.length,
        cost: response.data.cost 
      });

      // Transform DataForSEO response to our KeywordData format
      const keywordData: KeywordData[] = [];
      
      if (response.data.tasks && response.data.tasks.length > 0) {
        const task = response.data.tasks[0];
        if (task && task.result) {
          for (const result of task.result) {
            keywordData.push({
              keyword: result.keyword,
              searchVolume: result.search_volume,
              cpc: result.cpc,
              competition: result.competition_index,
              competitionLevel: result.competition,
              trends: result.monthly_searches?.map((trend: any) => ({
                month: trend.month,
                year: trend.year,
                searchVolume: trend.search_volume,
              })),
              source: 'DataForSEO',
            });
          }
        }
      }

      return {
        success: true,
        data: keywordData,
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };

    } catch (error) {
      const duration = Date.now() - startTime;
      logger.error('Keyword research failed', error);
      logger.performance('keyword_research_failed', duration);

      if (error instanceof SeoResearchError) {
        return {
          success: false,
          error: {
            code: error.code,
            message: error.message,
            details: error.details,
          },
          metadata: {
            timestamp: new Date().toISOString(),
            duration,
            source: 'DataForSEO',
            cached: false,
          },
        };
      }

      return {
        success: false,
        error: {
          code: 'KEYWORD_RESEARCH_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error occurred',
          details: error,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };
    }
  }

  /**
   * Analyze backlinks using DataForSEO Backlinks API
   */
  async analyzeBacklinks(params: BacklinkAnalysisParams): Promise<ApiResponse<BacklinkData[]>> {
    const startTime = Date.now();
    
    try {
      logger.info('🔗 Starting backlink analysis', { target: params.target });

      // Prepare request payload for DataForSEO Backlinks API
      const payload = [{
        target: params.target,
        mode: params.mode || 'as_is',
        limit: params.limit || 1000,
        offset: params.offset || 0,
        backlinks_status_type: params.backlinks_status_type || 'live',
        include_subdomains: params.include_subdomains ?? false,
        include_indirect_links: params.include_indirect_links ?? false,
        exclude_internal_backlinks: params.exclude_internal_backlinks ?? true,
      }];

      const response: AxiosResponse<DataForSEOResponse> = await this.client.post(
        '/backlinks/backlinks/live',
        payload
      );

      const duration = Date.now() - startTime;
      logger.performance('backlink_analysis', duration, { 
        target: params.target,
        cost: response.data.cost 
      });

      // Transform DataForSEO response to our BacklinkData format
      const backlinkData: BacklinkData[] = [];
      
      if (response.data.tasks && response.data.tasks.length > 0) {
        const task = response.data.tasks[0];
        if (task && task.data && task.data.results && task.data.results[0]?.items) {
          for (const item of task.data.results[0].items) {
            backlinkData.push({
              urlFrom: item.url_from,
              urlTo: item.url_to,
              domainFrom: item.domain_from,
              anchor: item.anchor || '',
              linkType: item.link_attribute === 'dofollow' ? 'dofollow' : 'nofollow',
              authority: item.page_from_rank,
              firstSeen: item.first_seen,
              lastSeen: item.last_seen,
              source: 'DataForSEO',
            });
          }
        }
      }

      return {
        success: true,
        data: backlinkData,
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };

    } catch (error) {
      const duration = Date.now() - startTime;
      logger.error('Backlink analysis failed', error);
      logger.performance('backlink_analysis_failed', duration);

      if (error instanceof SeoResearchError) {
        return {
          success: false,
          error: {
            code: error.code,
            message: error.message,
            details: error.details,
          },
          metadata: {
            timestamp: new Date().toISOString(),
            duration,
            source: 'DataForSEO',
            cached: false,
          },
        };
      }

      return {
        success: false,
        error: {
          code: 'BACKLINK_ANALYSIS_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error occurred',
          details: error,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };
    }
  }

  /**
   * Analyze SERP using DataForSEO SERP API
   */
  async analyzeSERP(params: SerpAnalysisParams): Promise<ApiResponse<SerpData>> {
    const startTime = Date.now();
    
    try {
      logger.info('📊 Starting SERP analysis', { keyword: params.keyword });

      // Prepare request payload for DataForSEO SERP API
      const payload = [{
        keyword: params.keyword,
        location_name: params.location_name || 'United States',
        language_name: params.language_name || 'English',
        device: params.device || 'desktop',
        os: params.os || 'windows',
        depth: params.depth || 100,
        calculate_rectangles: params.calculate_rectangles ?? false,
      }];

      const response: AxiosResponse<DataForSEOResponse> = await this.client.post(
        '/serp/google/organic/live/advanced',
        payload
      );

      const duration = Date.now() - startTime;
      logger.performance('serp_analysis', duration, { 
        keyword: params.keyword,
        cost: response.data.cost 
      });

      // Transform DataForSEO response to our SerpData format
      let serpData: SerpData = {
        keyword: params.keyword,
        location: params.location_name || 'United States',
        language: params.language_name || 'English',
        results: [],
        source: 'DataForSEO',
      };
      
      if (response.data.tasks && response.data.tasks.length > 0) {
        const task = response.data.tasks[0];
        if (task && task.data && task.data.results && task.data.results[0]?.items) {
          const items = task.data.results[0].items;
          
          serpData.results = items.map((item: any, index: number) => ({
            position: item.rank_group || index + 1,
            url: item.url || '',
            title: item.title || '',
            description: item.description || '',
            domain: item.domain || '',
            type: this.mapSerpItemType(item.type),
          }));

          serpData.totalResults = task.data.results[0].total_count;
          serpData.searchTime = parseFloat(task.time);
        }
      }

      return {
        success: true,
        data: serpData,
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };

    } catch (error) {
      const duration = Date.now() - startTime;
      logger.error('SERP analysis failed', error);
      logger.performance('serp_analysis_failed', duration);

      if (error instanceof SeoResearchError) {
        return {
          success: false,
          error: {
            code: error.code,
            message: error.message,
            details: error.details,
          },
          metadata: {
            timestamp: new Date().toISOString(),
            duration,
            source: 'DataForSEO',
            cached: false,
          },
        };
      }

      return {
        success: false,
        error: {
          code: 'SERP_ANALYSIS_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error occurred',
          details: error,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          duration,
          source: 'DataForSEO',
          cached: false,
        },
      };
    }
  }

  /**
   * Test API connectivity and authentication
   */
  async testConnection(): Promise<ApiResponse<{ status: string; user: string }>> {
    try {
      logger.info('🔌 Testing DataForSEO API connection...');

      const response = await this.client.get('/appendix/user_data');
      
      return {
        success: true,
        data: {
          status: 'connected',
          user: response.data.login || 'unknown',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'DataForSEO',
          cached: false,
        },
      };

    } catch (error) {
      logger.error('DataForSEO connection test failed', error);

      if (error instanceof SeoResearchError) {
        return {
          success: false,
          error: {
            code: error.code,
            message: error.message,
            details: error.details,
          },
        };
      }

      return {
        success: false,
        error: {
          code: 'CONNECTION_TEST_ERROR',
          message: error instanceof Error ? error.message : 'Connection test failed',
          details: error,
        },
      };
    }
  }

  /**
   * Map DataForSEO SERP item types to our standard types
   */
  private mapSerpItemType(type: string): 'organic' | 'paid' | 'featured_snippet' | 'local' | 'image' | 'video' {
    const typeMap: Record<string, 'organic' | 'paid' | 'featured_snippet' | 'local' | 'image' | 'video'> = {
      'organic': 'organic',
      'paid': 'paid',
      'featured_snippet': 'featured_snippet',
      'answer_box': 'featured_snippet',
      'knowledge_graph': 'featured_snippet',
      'local_pack': 'local',
      'local_services': 'local',
      'images': 'image',
      'videos': 'video',
      'video': 'video',
    };

    return typeMap[type] || 'organic';
  }
}

/**
 * Singleton DataForSEO client instance
 */
export const dataForSEOClient = new DataForSEOClient(); 