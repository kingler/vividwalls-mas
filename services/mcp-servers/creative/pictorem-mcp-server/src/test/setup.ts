/**
 * Test setup file for Pictorem MCP Server tests
 * Configures environment variables and global mocks
 */

import { vi, beforeEach } from 'vitest';

// Set up test environment variables
process.env.PICTOREM_USERNAME = "test@vividwalls.com";
process.env.PICTOREM_PASSWORD = "testpassword123";

// Global test utilities
global.console = {
  ...console,
  // Mock console.error to prevent noise in test output unless explicitly testing errors
  error: vi.fn(),
};

// Clean up any global state between tests
beforeEach(() => {
  vi.clearAllMocks();
}); 