/**
 * Configuration Management System
 * 
 * Handles environment variable loading, validation, and secure configuration
 * management for all integrated APIs (DataForSEO, Brave, Perplexity, etc.)
 */

import { z } from 'zod';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Configuration schema with validation rules
 */
const configSchema = z.object({
  // Server configuration
  server: z.object({
    name: z.string().default('seo-research-mcp'),
    version: z.string().default('0.1.0'),
    environment: z.enum(['development', 'production', 'test']).default('development'),
    logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  }),

  // API Keys and endpoints
  apis: z.object({
    // DataForSEO API configuration
    dataForSEO: z.object({
      apiKey: z.string().min(1, 'DataForSEO API key is required'),
      baseUrl: z.string().url().default('https://api.dataforseo.com/v3'),
      timeout: z.number().default(30000),
    }),

    // Brave Search API configuration
    brave: z.object({
      apiKey: z.string().default(''),
      baseUrl: z.string().url().default('https://api.search.brave.com/res/v1'),
      timeout: z.number().default(10000),
    }),

    // Perplexity API configuration
    perplexity: z.object({
      apiKey: z.string().default(''),
      baseUrl: z.string().url().default('https://api.perplexity.ai'),
      model: z.string().default('llama-3.1-sonar-small-128k-online'),
      timeout: z.number().default(30000),
    }),

    // Tavily API configuration
    tavily: z.object({
      apiKey: z.string().default(''),
      baseUrl: z.string().url().default('https://api.tavily.com'),
      timeout: z.number().default(20000),
    }),

    // SerpAPI configuration
    serpApi: z.object({
      apiKey: z.string().default(''),
      baseUrl: z.string().url().default('https://serpapi.com/search'),
      timeout: z.number().default(15000),
    }),

    // OpenAI API configuration (for LLM processing)
    openai: z.object({
      apiKey: z.string().default(''),
      baseUrl: z.string().url().default('https://api.openai.com/v1'),
      model: z.string().default('gpt-4'),
      timeout: z.number().default(60000),
    }),
  }),

  // Caching configuration
  cache: z.object({
    enabled: z.boolean().default(true),
    redis: z.object({
      url: z.string().default('redis://localhost:6379'),
      ttl: z.number().default(3600), // 1 hour default TTL
      maxMemory: z.string().default('100mb'),
    }),
  }),

  // Rate limiting configuration
  rateLimiting: z.object({
    enabled: z.boolean().default(true),
    windowMs: z.number().default(60000), // 1 minute window
    maxRequests: z.number().default(100), // Max requests per window
  }),
});

/**
 * Configuration type derived from schema
 */
export type Config = z.infer<typeof configSchema>;

/**
 * Load and validate configuration from environment variables
 */
function loadConfig(): Config {
  const rawConfig = {
    server: {
      name: process.env['SERVER_NAME'] || 'seo-research-mcp',
      version: process.env['SERVER_VERSION'] || '0.1.0',
      environment: process.env['NODE_ENV'] || 'development',
      logLevel: process.env['LOG_LEVEL'] || 'info',
    },
    apis: {
      dataForSEO: {
        apiKey: process.env['DATAFORSEO_API_KEY'] || '',
        baseUrl: process.env['DATAFORSEO_BASE_URL'] || 'https://api.dataforseo.com/v3',
        timeout: parseInt(process.env['DATAFORSEO_TIMEOUT'] || '30000'),
      },
      brave: {
        apiKey: process.env['BRAVE_API_KEY'] || '',
        baseUrl: process.env['BRAVE_BASE_URL'] || 'https://api.search.brave.com/res/v1',
        timeout: parseInt(process.env['BRAVE_TIMEOUT'] || '10000'),
      },
      perplexity: {
        apiKey: process.env['PERPLEXITY_API_KEY'] || '',
        baseUrl: process.env['PERPLEXITY_BASE_URL'] || 'https://api.perplexity.ai',
        model: process.env['PERPLEXITY_MODEL'] || 'llama-3.1-sonar-small-128k-online',
        timeout: parseInt(process.env['PERPLEXITY_TIMEOUT'] || '30000'),
      },
      tavily: {
        apiKey: process.env['TAVILY_API_KEY'] || '',
        baseUrl: process.env['TAVILY_BASE_URL'] || 'https://api.tavily.com',
        timeout: parseInt(process.env['TAVILY_TIMEOUT'] || '20000'),
      },
      serpApi: {
        apiKey: process.env['SERPAPI_KEY'] || '',
        baseUrl: process.env['SERPAPI_BASE_URL'] || 'https://serpapi.com/search',
        timeout: parseInt(process.env['SERPAPI_TIMEOUT'] || '15000'),
      },
      openai: {
        apiKey: process.env['OPENAI_API_KEY'] || '',
        baseUrl: process.env['OPENAI_BASE_URL'] || 'https://api.openai.com/v1',
        model: process.env['OPENAI_MODEL'] || 'gpt-4',
        timeout: parseInt(process.env['OPENAI_TIMEOUT'] || '60000'),
      },
    },
    cache: {
      enabled: process.env['CACHE_ENABLED'] !== 'false',
      redis: {
        url: process.env['REDIS_URL'] || 'redis://localhost:6379',
        ttl: parseInt(process.env['CACHE_TTL'] || '3600'),
        maxMemory: process.env['REDIS_MAX_MEMORY'] || '100mb',
      },
    },
    rateLimiting: {
      enabled: process.env['RATE_LIMITING_ENABLED'] !== 'false',
      windowMs: parseInt(process.env['RATE_LIMIT_WINDOW_MS'] || '60000'),
      maxRequests: parseInt(process.env['RATE_LIMIT_MAX_REQUESTS'] || '100'),
    },
  };

  return configSchema.parse(rawConfig);
}

/**
 * Configuration instance
 */
class ConfigManager {
  private _config: Config | null = null;

  /**
   * Get the current configuration
   */
  get(): Config {
    if (!this._config) {
      this._config = loadConfig();
    }
    return this._config;
  }

  /**
   * Validate configuration and throw detailed errors if invalid
   */
  async validate(): Promise<void> {
    try {
      this._config = loadConfig();
    } catch (error) {
      if (error instanceof z.ZodError) {
        const missingKeys = error.errors
          .filter(err => err.message.includes('required'))
          .map(err => err.path.join('.'));
        
        if (missingKeys.length > 0) {
          throw new Error(
            `Missing required environment variables: ${missingKeys.join(', ')}\n` +
            'Please check your .env file or environment configuration.'
          );
        }
      }
      throw error;
    }
  }

  /**
   * Get API configuration for a specific service
   */
  getApiConfig(service: keyof Config['apis']): Config['apis'][typeof service] {
    return this.get().apis[service];
  }

  /**
   * Check if a specific API is configured
   */
  isApiConfigured(service: keyof Config['apis']): boolean {
    try {
      const apiConfig = this.getApiConfig(service);
      return Boolean(apiConfig.apiKey);
    } catch {
      return false;
    }
  }

  /**
   * Get list of configured APIs
   */
  getConfiguredApis(): Array<keyof Config['apis']> {
    const apis: Array<keyof Config['apis']> = [
      'dataForSEO', 'brave', 'perplexity', 'tavily', 'serpApi', 'openai'
    ];
    
    return apis.filter(api => this.isApiConfigured(api));
  }
}

/**
 * Singleton configuration manager instance
 */
export const config = new ConfigManager(); 