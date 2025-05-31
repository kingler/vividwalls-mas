/**
 * Logging System
 * 
 * Provides structured logging with different levels and output formatting
 * for the SEO Research MCP Server
 */

import { config } from '../config/index.js';

/**
 * Log levels enum
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

/**
 * Log level mapping
 */
const LOG_LEVEL_MAP: Record<string, LogLevel> = {
  debug: LogLevel.DEBUG,
  info: LogLevel.INFO,
  warn: LogLevel.WARN,
  error: LogLevel.ERROR,
};

/**
 * Color codes for console output
 */
const COLORS = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
};

/**
 * Logger class with structured logging capabilities
 */
class Logger {
  private currentLogLevel: LogLevel;

  constructor() {
    // Get log level from configuration, default to INFO
    const configLogLevel = config.get().server.logLevel;
    this.currentLogLevel = LOG_LEVEL_MAP[configLogLevel] ?? LogLevel.INFO;
  }

  /**
   * Check if a log level should be output
   */
  private shouldLog(level: LogLevel): boolean {
    return level >= this.currentLogLevel;
  }

  /**
   * Format timestamp for log entries
   */
  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  /**
   * Format log message with colors for console output
   */
  private formatMessage(level: string, message: string, data?: any): string {
    const timestamp = this.formatTimestamp();
    const colorMap = {
      DEBUG: COLORS.dim,
      INFO: COLORS.blue,
      WARN: COLORS.yellow,
      ERROR: COLORS.red,
    };

    const color = colorMap[level as keyof typeof colorMap] || COLORS.white;
    const formattedLevel = `${color}${level.padEnd(5)}${COLORS.reset}`;
    const formattedTime = `${COLORS.dim}${timestamp}${COLORS.reset}`;
    
    let formattedMessage = `${formattedTime} ${formattedLevel} ${message}`;
    
    if (data !== undefined) {
      const dataStr = typeof data === 'object' 
        ? JSON.stringify(data, null, 2)
        : String(data);
      formattedMessage += `\n${COLORS.dim}${dataStr}${COLORS.reset}`;
    }

    return formattedMessage;
  }

  /**
   * Output log entry to console
   */
  private output(level: LogLevel, levelName: string, message: string, data?: any, error?: Error): void {
    if (!this.shouldLog(level)) {
      return;
    }

    // For MCP servers, we need to be careful about stdout pollution
    // Use stderr for all log output to avoid interfering with MCP protocol
    const formattedMessage = this.formatMessage(levelName, message, data);
    
    if (error) {
      console.error(formattedMessage);
      console.error(`${COLORS.red}Error:${COLORS.reset}`, error.message);
      if (error.stack && this.shouldLog(LogLevel.DEBUG)) {
        console.error(`${COLORS.dim}Stack:${COLORS.reset}`, error.stack);
      }
    } else {
      console.error(formattedMessage);
    }
  }

  /**
   * Debug level logging
   */
  debug(message: string, data?: any): void {
    this.output(LogLevel.DEBUG, 'DEBUG', message, data);
  }

  /**
   * Info level logging
   */
  info(message: string, data?: any): void {
    this.output(LogLevel.INFO, 'INFO', message, data);
  }

  /**
   * Warning level logging
   */
  warn(message: string, data?: any): void {
    this.output(LogLevel.WARN, 'WARN', message, data);
  }

  /**
   * Error level logging
   */
  error(message: string, error?: Error | any): void {
    if (error instanceof Error) {
      this.output(LogLevel.ERROR, 'ERROR', message, undefined, error);
    } else {
      this.output(LogLevel.ERROR, 'ERROR', message, error);
    }
  }

  /**
   * Log API request start
   */
  apiRequest(service: string, endpoint: string, params?: any): void {
    this.debug(`🌐 API Request: ${service}`, {
      endpoint,
      params: params ? Object.keys(params) : undefined,
    });
  }

  /**
   * Log API response
   */
  apiResponse(service: string, endpoint: string, status: number, duration?: number): void {
    const statusColor = status >= 400 ? COLORS.red : COLORS.green;
    const durationStr = duration ? ` (${duration}ms)` : '';
    
    this.debug(`📡 API Response: ${service}`, {
      endpoint,
      status: `${statusColor}${status}${COLORS.reset}`,
      duration: durationStr,
    });
  }

  /**
   * Log cache operations
   */
  cache(operation: 'hit' | 'miss' | 'set' | 'delete', key: string, ttl?: number): void {
    const emoji = {
      hit: '🎯',
      miss: '❌',
      set: '💾',
      delete: '🗑️',
    };

    this.debug(`${emoji[operation]} Cache ${operation}: ${key}`, {
      ttl: ttl ? `${ttl}s` : undefined,
    });
  }

  /**
   * Log MCP tool execution
   */
  mcpTool(toolName: string, params?: any): void {
    this.info(`🔧 MCP Tool: ${toolName}`, {
      params: params ? Object.keys(params) : undefined,
    });
  }

  /**
   * Log performance metrics
   */
  performance(operation: string, duration: number, metadata?: any): void {
    const durationColor = duration > 5000 ? COLORS.red : 
                         duration > 2000 ? COLORS.yellow : COLORS.green;
    
    this.info(`⚡ Performance: ${operation}`, {
      duration: `${durationColor}${duration}ms${COLORS.reset}`,
      ...metadata,
    });
  }

  /**
   * Set log level dynamically
   */
  setLogLevel(level: keyof typeof LOG_LEVEL_MAP): void {
    const newLevel = LOG_LEVEL_MAP[level];
    if (newLevel !== undefined) {
      this.currentLogLevel = newLevel;
      this.info(`📊 Log level set to: ${level.toUpperCase()}`);
    }
  }

  /**
   * Get current log level
   */
  getLogLevel(): string {
    const foundLevel = Object.keys(LOG_LEVEL_MAP).find(
      key => LOG_LEVEL_MAP[key] === this.currentLogLevel
    );
    return foundLevel || 'info';
  }
}

/**
 * Singleton logger instance
 */
export const logger = new Logger(); 