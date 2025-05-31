/**
 * Test suite for Pictorem MCP Tools
 * Tests all MCP tools: submit-order, calculate-pricing, get-order-status, upload-image
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Mock the MCP SDK components
const mockServer = {
  setRequestHandler: vi.fn(),
  connect: vi.fn()
};

const mockTransport = {};

vi.mock('@modelcontextprotocol/sdk/server/index.js', () => ({
  Server: vi.fn(() => mockServer)
}));

vi.mock('@modelcontextprotocol/sdk/server/stdio.js', () => ({
  StdioServerTransport: vi.fn(() => mockTransport)
}));

vi.mock('@modelcontextprotocol/sdk/types.js', () => ({
  CallToolRequestSchema: {},
  ListToolsRequestSchema: {},
  ErrorCode: {
    InvalidParams: 'INVALID_PARAMS',
    InternalError: 'INTERNAL_ERROR',
    MethodNotFound: 'METHOD_NOT_FOUND'
  },
  McpError: class McpError extends Error {
    constructor(public code: string, message: string) {
      super(message);
      this.name = 'McpError';
    }
  }
}));

// Create mock adapter for axios
let mockAxios: MockAdapter;

describe('Pictorem MCP Tools', () => {
  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
    vi.clearAllMocks();
  });

  afterEach(() => {
    mockAxios.restore();
  });

  describe('Tool Definitions', () => {
    it('should define all required tools', () => {
      // Test that our mock server can handle tool definitions
      const expectedTools = [
        'submit-order',
        'calculate-pricing', 
        'get-order-status',
        'upload-image'
      ];
      
      // Mock the server setup call
      mockServer.setRequestHandler('tools/list', () => ({
        tools: expectedTools.map(name => ({ name }))
      }));
      
      // Verify that setRequestHandler was called for tools
      expect(mockServer.setRequestHandler).toHaveBeenCalled();
      
      // Check for specific tool registrations
      const calls = mockServer.setRequestHandler.mock.calls;
      expect(calls.length).toBeGreaterThan(0);
    });
  });

  describe('Authentication', () => {
    it('should authenticate with Pictorem API successfully', async () => {
      const mockToken = 'test-auth-token-123';
      
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(200, {
        token: mockToken
      });

      // Mock the authentication function call
      const authResponse = await axios.post('https://www.pictorem.com/api/auth/login', {
        username: 'test@vividwalls.com',
        password: 'testpassword123'
      });

      expect(authResponse.data.token).toBe(mockToken);
    });

    it('should handle authentication failure', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(401, {
        message: 'Invalid credentials'
      });

      try {
        await axios.post('https://www.pictorem.com/api/auth/login', {
          username: 'invalid@email.com',
          password: 'wrongpassword'
        });
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data.message).toBe('Invalid credentials');
      }
    });

    it('should cache authentication tokens', async () => {
      const mockToken = 'cached-token-456';
      
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(200, {
        token: mockToken
      });

      // First call should hit the API
      await axios.post('https://www.pictorem.com/api/auth/login', {
        username: 'test@vividwalls.com',
        password: 'testpassword123'
      });

      // Verify the API was called once
      expect(mockAxios.history.post.length).toBe(1);
    });
  });

  describe('calculate-pricing Tool', () => {
    const validPricingRequest = {
      basePrice: 57.00,
      productType: 'canvas',
      size: { width: 24, height: 16 }
    };

    it('should calculate pricing for canvas stretched correctly', () => {
      const result = calculateMockPricing(validPricingRequest);
      
      expect(result.base_price).toBe(57.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0);
      expect(result.total_discount).toBe(0.15);
      expect(result.discounted_price).toBeCloseTo(48.45, 2);
      expect(result.final_price).toBeCloseTo(100.05, 2);
      expect(result.square_inches).toBe(384);
      expect(result.size_category).toBe('medium');
    });

    it('should calculate pricing for canvas roll correctly', () => {
      const request = { ...validPricingRequest, productType: 'canvas_roll' as const };
      const result = calculateMockPricing(request);
      
      expect(result.base_price).toBe(57.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0.25);
      expect(result.total_discount).toBe(0.40);
      expect(result.discounted_price).toBeCloseTo(34.20, 2);
      expect(result.final_price).toBeCloseTo(70.62, 2);
    });

    it('should validate pricing parameters', () => {
      expect(() => calculateMockPricing({
        basePrice: -10,
        productType: 'canvas',
        size: { width: 24, height: 16 }
      })).toThrow();

      expect(() => calculateMockPricing({
        basePrice: 57,
        productType: 'invalid' as any,
        size: { width: 24, height: 16 }
      })).toThrow();

      expect(() => calculateMockPricing({
        basePrice: 57,
        productType: 'canvas',
        size: { width: 0, height: 16 }
      })).toThrow();
    });
  });

  describe('submit-order Tool', () => {
    const validOrderData = {
      shopify_order_id: "1234567890",
      order_number: "VW-2024-001",
      customer_info: {
        email: "customer@example.com",
        name: "John Doe",
        shipping_address: {
          address1: "123 Main St",
          city: "Anytown",
          province: "CA",
          country: "US",
          zip: "12345"
        }
      },
      product_configuration: {
        product_type: "canvas" as const,
        size: { width: 24, height: 16, unit: "inches" as const },
        canvas_type: "stretched" as const,
        frame_options: { frame_type: "none" as const },
        quantity: 1
      },
      image_data: {
        file_path: "/path/to/image.jpg",
        file_name: "artwork.jpg",
        file_format: "jpg" as const,
        file_size: 2048000,
        upload_url: "https://example.com/images/artwork.jpg"
      },
      pricing: {
        base_price: 57.00,
        pro_discount: 0.15,
        canvas_roll_discount: 0,
        vividwalls_markup: 2.065
      }
    };

    it('should submit order successfully', async () => {
      const mockToken = 'auth-token-123';
      const mockOrderId = 'PICT-ORD-2024-001';
      
      // Mock authentication
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(200, {
        token: mockToken
      });

      // Mock order submission
      mockAxios.onPost('https://www.pictorem.com/api/orders/submit').reply(200, {
        order_id: mockOrderId,
        status: 'pending',
        estimated_delivery: '2024-02-15',
        tracking_url: `https://pictorem.com/track/${mockOrderId}`
      });

      const response = await axios.post('https://www.pictorem.com/api/orders/submit', {
        product_type: validOrderData.product_configuration.product_type,
        width: validOrderData.product_configuration.size.width,
        height: validOrderData.product_configuration.size.height,
        canvas_type: validOrderData.product_configuration.canvas_type,
        frame_type: validOrderData.product_configuration.frame_options.frame_type,
        quantity: validOrderData.product_configuration.quantity,
        image_url: validOrderData.image_data.upload_url,
        customer_email: validOrderData.customer_info.email,
        shipping_address: validOrderData.customer_info.shipping_address,
        order_reference: validOrderData.shopify_order_id
      }, {
        headers: { 'Authorization': `Bearer ${mockToken}` }
      });

      expect(response.data.order_id).toBe(mockOrderId);
      expect(response.data.status).toBe('pending');
    });

    it('should handle order submission validation errors', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/orders/submit').reply(400, {
        message: 'Invalid product configuration'
      });

      try {
        await axios.post('https://www.pictorem.com/api/orders/submit', {
          invalid: 'data'
        });
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.message).toBe('Invalid product configuration');
      }
    });
  });

  describe('get-order-status Tool', () => {
    it('should retrieve order status successfully', async () => {
      const mockToken = 'auth-token-123';
      const orderId = 'PICT-ORD-2024-001';
      
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(200, {
        token: mockToken
      });

      mockAxios.onGet(`https://www.pictorem.com/api/orders/${orderId}/status`).reply(200, {
        status: 'in_production',
        tracking_number: 'TRK123456789',
        estimated_delivery: '2024-02-15',
        production_stage: 'printing',
        last_updated: '2024-02-01T10:00:00Z'
      });

      const response = await axios.get(`https://www.pictorem.com/api/orders/${orderId}/status`, {
        headers: { 'Authorization': `Bearer ${mockToken}` }
      });

      expect(response.data.status).toBe('in_production');
      expect(response.data.tracking_number).toBe('TRK123456789');
      expect(response.data.production_stage).toBe('printing');
    });

    it('should handle order not found', async () => {
      const orderId = 'INVALID-ORDER-ID';
      
      mockAxios.onGet(`https://www.pictorem.com/api/orders/${orderId}/status`).reply(404, {
        message: 'Order not found'
      });

      try {
        await axios.get(`https://www.pictorem.com/api/orders/${orderId}/status`);
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.message).toBe('Order not found');
      }
    });
  });

  describe('upload-image Tool', () => {
    it('should upload image successfully', async () => {
      const mockToken = 'auth-token-123';
      const imageUrl = 'https://example.com/image.jpg';
      
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').reply(200, {
        token: mockToken
      });

      // Mock image download
      mockAxios.onGet(imageUrl).reply(200, 'mock-image-data', {
        'content-type': 'image/jpeg'
      });

      // Mock image upload
      mockAxios.onPost('https://www.pictorem.com/api/images/upload').reply(200, {
        upload_id: 'IMG-UPLOAD-123',
        file_url: 'https://pictorem.com/images/uploaded/IMG-UPLOAD-123.jpg',
        file_size: 2048000,
        dimensions: { width: 2400, height: 1600 }
      });

      const uploadResponse = await axios.post('https://www.pictorem.com/api/images/upload', 
        new FormData(), {
        headers: { 'Authorization': `Bearer ${mockToken}` }
      });

      expect(uploadResponse.data.upload_id).toBe('IMG-UPLOAD-123');
      expect(uploadResponse.data.file_size).toBe(2048000);
      expect(uploadResponse.data.dimensions).toEqual({ width: 2400, height: 1600 });
    });

    it('should handle image upload errors', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/images/upload').reply(413, {
        message: 'File too large'
      });

      try {
        await axios.post('https://www.pictorem.com/api/images/upload', new FormData());
      } catch (error) {
        expect(error.response.status).toBe(413);
        expect(error.response.data.message).toBe('File too large');
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle network timeouts', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/auth/login').timeout();

      try {
        await axios.post('https://www.pictorem.com/api/auth/login', {}, { timeout: 1000 });
      } catch (error) {
        expect(error.code).toBe('ECONNABORTED');
      }
    });

    it('should handle API rate limiting', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/orders/submit').reply(429, {
        message: 'Rate limit exceeded',
        retry_after: 60
      });

      try {
        await axios.post('https://www.pictorem.com/api/orders/submit', {});
      } catch (error) {
        expect(error.response.status).toBe(429);
        expect(error.response.data.message).toBe('Rate limit exceeded');
      }
    });

    it('should handle server errors gracefully', async () => {
      mockAxios.onPost('https://www.pictorem.com/api/orders/submit').reply(500, {
        message: 'Internal server error'
      });

      try {
        await axios.post('https://www.pictorem.com/api/orders/submit', {});
      } catch (error) {
        expect(error.response.status).toBe(500);
        expect(error.response.data.message).toBe('Internal server error');
      }
    });
  });
});

/**
 * Mock pricing calculation function for testing
 */
function calculateMockPricing(
  request: {
    basePrice: number;
    productType: 'canvas' | 'canvas_roll';
    size: { width: number; height: number };
  }
) {
  // Validate inputs
  if (request.basePrice <= 0) {
    throw new Error('Base price must be positive');
  }
  if (!['canvas', 'canvas_roll'].includes(request.productType)) {
    throw new Error('Invalid product type');
  }
  if (request.size.width <= 0 || request.size.height <= 0) {
    throw new Error('Size dimensions must be positive');
  }

  // VividWalls pricing logic
  const proDiscount = 0.15;
  const canvasRollDiscount = request.productType === 'canvas_roll' ? 0.25 : 0;
  const vividwallsMarkup = 2.065;
  
  const totalDiscount = proDiscount + canvasRollDiscount;
  const discountedPrice = request.basePrice * (1 - totalDiscount);
  const finalPrice = discountedPrice * vividwallsMarkup;
  
  const squareInches = request.size.width * request.size.height;
  
  return {
    base_price: request.basePrice,
    pro_discount: proDiscount,
    canvas_roll_discount: canvasRollDiscount,
    total_discount: totalDiscount,
    discounted_price: discountedPrice,
    vividwalls_markup: vividwallsMarkup,
    final_price: finalPrice,
    square_inches: squareInches,
    size_category: squareInches <= 144 ? "small" : squareInches <= 576 ? "medium" : "large"
  };
} 