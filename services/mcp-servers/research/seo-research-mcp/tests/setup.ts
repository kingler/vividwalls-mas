/**
 * Jest Test Setup
 * Configures global test environment, mocks, and utilities for TDD
 */

import { jest } from '@jest/globals';

// Global test timeout
jest.setTimeout(10000);

// Mock environment variables for testing
process.env['NODE_ENV'] = 'test';
process.env['DATAFORSEO_API_KEY'] = 'test-dataforseo-key';
process.env['BRAVE_API_KEY'] = 'test-brave-key';
process.env['PERPLEXITY_API_KEY'] = 'test-perplexity-key';
process.env['TAVILY_API_KEY'] = 'test-tavily-key';
process.env['SERPAPI_KEY'] = 'test-serpapi-key';
process.env['OPENAI_API_KEY'] = 'test-openai-key';
process.env['REDIS_URL'] = 'redis://localhost:6379/1'; // Test database

// Global test utilities
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidMCPResponse(): R;
      toHaveValidKeywordData(): R;
      toHaveValidBacklinkData(): R;
    }
  }
}

// Custom Jest matchers for MCP responses
expect.extend({
  toBeValidMCPResponse(received: any) {
    const pass = received && 
                 typeof received === 'object' &&
                 'success' in received &&
                 typeof received.success === 'boolean';
    
    if (pass) {
      return {
        message: () => `Expected ${received} not to be a valid MCP response`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected ${received} to be a valid MCP response with success property`,
        pass: false,
      };
    }
  },

  toHaveValidKeywordData(received: any) {
    const pass = received &&
                 Array.isArray(received.keywords) &&
                 received.keywords.every((kw: any) => 
                   typeof kw.keyword === 'string' &&
                   typeof kw.searchVolume === 'number'
                 );
    
    if (pass) {
      return {
        message: () => `Expected ${received} not to have valid keyword data`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected ${received} to have valid keyword data structure`,
        pass: false,
      };
    }
  },

  toHaveValidBacklinkData(received: any) {
    const pass = received &&
                 Array.isArray(received.backlinks) &&
                 received.backlinks.every((bl: any) => 
                   typeof bl.url === 'string' &&
                   typeof bl.anchorText === 'string'
                 );
    
    if (pass) {
      return {
        message: () => `Expected ${received} not to have valid backlink data`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected ${received} to have valid backlink data structure`,
        pass: false,
      };
    }
  },
});

// Mock console methods to reduce noise in tests
const originalConsole = { ...console };
beforeAll(() => {
  console.log = jest.fn();
  console.info = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  Object.assign(console, originalConsole);
});

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
});

export {}; 