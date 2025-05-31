/**
 * Test suite for Zod Schema Validation
 * Tests all Zod schemas used in the Pictorem MCP server
 */

import { describe, it, expect } from 'vitest';
import { z } from 'zod';

// Re-define schemas for testing (these should match the ones in index.ts)
const OrderConfigSchema = z.object({
  shopify_order_id: z.string().describe("Shopify order ID for reference"),
  order_number: z.string().describe("Human-readable order number"),
  customer_info: z.object({
    email: z.string().email().describe("Customer email address"),
    name: z.string().describe("Customer full name"),
    shipping_address: z.object({
      address1: z.string().describe("Primary address line"),
      address2: z.string().optional().describe("Secondary address line"),
      city: z.string().describe("City"),
      province: z.string().describe("State/Province"),
      country: z.string().describe("Country"),
      zip: z.string().describe("Postal/ZIP code")
    })
  }),
  product_configuration: z.object({
    product_type: z.enum([
      "canvas", "framed", "canvas_roll", "mural", "panel", 
      "acrylic", "metal", "wood", "poster"
    ]).describe("Type of print product"),
    size: z.object({
      width: z.number().min(1).max(120).describe("Width in inches"),
      height: z.number().min(1).max(120).describe("Height in inches"),
      unit: z.literal("inches").describe("Size unit")
    }),
    canvas_type: z.enum(["stretched", "roll"]).optional().describe("Canvas type for canvas products"),
    frame_options: z.object({
      frame_type: z.enum(["none", "standard", "premium_white", "truffle"]).describe("Frame type"),
      frame_cost: z.number().optional().describe("Additional frame cost")
    }).optional(),
    quantity: z.number().min(1).describe("Quantity to order")
  }),
  image_data: z.object({
    file_path: z.string().describe("Local or remote file path"),
    file_name: z.string().describe("Original filename"),
    file_format: z.enum(["jpg", "png", "pdf", "ai", "eps"]).describe("File format"),
    file_size: z.number().max(100 * 1024 * 1024).describe("File size in bytes (max 100MB)"),
    upload_url: z.string().url().describe("URL to the image file")
  }),
  pricing: z.object({
    base_price: z.number().describe("Base price from Pictorem"),
    pro_discount: z.number().default(0.15).describe("Pro account discount rate"),
    canvas_roll_discount: z.number().default(0.25).describe("Canvas roll additional discount"),
    vividwalls_markup: z.number().default(2.065).describe("VividWalls markup multiplier"),
    shipping_cost: z.number().optional().describe("Shipping cost if applicable")
  })
});

const PricingCalculationSchema = z.object({
  basePrice: z.number().positive().describe("Base price from Pictorem"),
  productType: z.enum(["canvas", "canvas_roll"]).describe("Product type for discount calculation"),
  size: z.object({
    width: z.number().positive().describe("Product width in inches"),
    height: z.number().positive().describe("Product height in inches")
  }).describe("Product dimensions")
});

const OrderStatusSchema = z.object({
  pictoremOrderId: z.string().min(1).describe("Pictorem order ID to check status for")
});

const ImageUploadSchema = z.object({
  imageUrl: z.string().url().describe("URL of the image to upload"),
  fileName: z.string().min(1).describe("Name of the file"),
  orderReference: z.string().min(1).describe("Reference to associate with the upload")
});

describe('Zod Schema Validation', () => {
  describe('OrderConfigSchema', () => {
    const validOrderData = {
      shopify_order_id: "1234567890",
      order_number: "VW-2024-001",
      customer_info: {
        email: "customer@example.com",
        name: "John Doe",
        shipping_address: {
          address1: "123 Main St",
          address2: "Apt 4B",
          city: "Anytown",
          province: "CA",
          country: "US",
          zip: "12345"
        }
      },
      product_configuration: {
        product_type: "canvas",
        size: {
          width: 24,
          height: 16,
          unit: "inches"
        },
        canvas_type: "stretched",
        frame_options: {
          frame_type: "none",
          frame_cost: 0
        },
        quantity: 1
      },
      image_data: {
        file_path: "/path/to/image.jpg",
        file_name: "artwork.jpg",
        file_format: "jpg",
        file_size: 2048000,
        upload_url: "https://example.com/images/artwork.jpg"
      },
      pricing: {
        base_price: 57.00,
        pro_discount: 0.15,
        canvas_roll_discount: 0,
        vividwalls_markup: 2.065,
        shipping_cost: 12.99
      }
    };

    it('should validate correct order data', () => {
      const result = OrderConfigSchema.safeParse(validOrderData);
      expect(result.success).toBe(true);
      
      if (result.success) {
        expect(result.data.shopify_order_id).toBe("1234567890");
        expect(result.data.customer_info.email).toBe("customer@example.com");
        expect(result.data.product_configuration.product_type).toBe("canvas");
      }
    });

    it('should reject invalid email format', () => {
      const invalidData = {
        ...validOrderData,
        customer_info: {
          ...validOrderData.customer_info,
          email: "invalid-email"
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('email');
      }
    });

    it('should reject invalid product type', () => {
      const invalidData = {
        ...validOrderData,
        product_configuration: {
          ...validOrderData.product_configuration,
          product_type: "invalid_type"
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('product_type');
      }
    });

    it('should reject invalid size constraints', () => {
      const invalidData = {
        ...validOrderData,
        product_configuration: {
          ...validOrderData.product_configuration,
          size: {
            width: 0, // Invalid: must be >= 1
            height: 16,
            unit: "inches"
          }
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      
      if (!result.success) {
        expect(result.error.issues[0].path).toContain('width');
      }
    });

    it('should reject oversized dimensions', () => {
      const invalidData = {
        ...validOrderData,
        product_configuration: {
          ...validOrderData.product_configuration,
          size: {
            width: 150, // Invalid: max is 120
            height: 16,
            unit: "inches"
          }
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject oversized files', () => {
      const invalidData = {
        ...validOrderData,
        image_data: {
          ...validOrderData.image_data,
          file_size: 101 * 1024 * 1024 // > 100MB
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should accept optional fields as undefined', () => {
      const dataWithoutOptionals = {
        ...validOrderData,
        customer_info: {
          ...validOrderData.customer_info,
          shipping_address: {
            address1: "123 Main St",
            // address2 is optional - omitting it
            city: "Anytown",
            province: "CA",
            country: "US",
            zip: "12345"
          }
        },
        product_configuration: {
          product_type: validOrderData.product_configuration.product_type,
          size: validOrderData.product_configuration.size,
          quantity: validOrderData.product_configuration.quantity
          // canvas_type and frame_options are optional - omitting them
        }
      };

      const result = OrderConfigSchema.safeParse(dataWithoutOptionals);
      expect(result.success).toBe(true);
    });

    it('should reject invalid URL format', () => {
      const invalidData = {
        ...validOrderData,
        image_data: {
          ...validOrderData.image_data,
          upload_url: "not-a-valid-url"
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('PricingCalculationSchema', () => {
    it('should validate correct pricing data', () => {
      const validData = {
        basePrice: 57.00,
        productType: "canvas",
        size: {
          width: 24,
          height: 16
        }
      };

      const result = PricingCalculationSchema.safeParse(validData);
      expect(result.success).toBe(true);
      
      if (result.success) {
        expect(result.data.basePrice).toBe(57.00);
        expect(result.data.productType).toBe("canvas");
      }
    });

    it('should reject negative base price', () => {
      const invalidData = {
        basePrice: -10,
        productType: "canvas",
        size: { width: 24, height: 16 }
      };

      const result = PricingCalculationSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject zero base price', () => {
      const invalidData = {
        basePrice: 0,
        productType: "canvas",
        size: { width: 24, height: 16 }
      };

      const result = PricingCalculationSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject invalid product type', () => {
      const invalidData = {
        basePrice: 57.00,
        productType: "invalid_type",
        size: { width: 24, height: 16 }
      };

      const result = PricingCalculationSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject invalid size dimensions', () => {
      const invalidData = {
        basePrice: 57.00,
        productType: "canvas",
        size: { width: 0, height: 16 }
      };

      const result = PricingCalculationSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should accept canvas_roll product type', () => {
      const validData = {
        basePrice: 57.00,
        productType: "canvas_roll",
        size: { width: 24, height: 16 }
      };

      const result = PricingCalculationSchema.safeParse(validData);
      expect(result.success).toBe(true);
      
      if (result.success) {
        expect(result.data.productType).toBe("canvas_roll");
      }
    });
  });

  describe('OrderStatusSchema', () => {
    it('should validate correct order status request', () => {
      const validData = {
        pictoremOrderId: "PICT-ORD-2024-001"
      };

      const result = OrderStatusSchema.safeParse(validData);
      expect(result.success).toBe(true);
      
      if (result.success) {
        expect(result.data.pictoremOrderId).toBe("PICT-ORD-2024-001");
      }
    });

    it('should reject missing order ID', () => {
      const invalidData = {};

      const result = OrderStatusSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject empty order ID', () => {
      const invalidData = {
        pictoremOrderId: ""
      };

      const result = OrderStatusSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('ImageUploadSchema', () => {
    it('should validate correct image upload data', () => {
      const validData = {
        imageUrl: "https://example.com/image.jpg",
        fileName: "artwork.jpg",
        orderReference: "VW-2024-001"
      };

      const result = ImageUploadSchema.safeParse(validData);
      expect(result.success).toBe(true);
      
      if (result.success) {
        expect(result.data.imageUrl).toBe("https://example.com/image.jpg");
        expect(result.data.fileName).toBe("artwork.jpg");
        expect(result.data.orderReference).toBe("VW-2024-001");
      }
    });

    it('should reject invalid URL format', () => {
      const invalidData = {
        imageUrl: "not-a-valid-url",
        fileName: "artwork.jpg",
        orderReference: "VW-2024-001"
      };

      const result = ImageUploadSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject missing fields', () => {
      const invalidData = {
        imageUrl: "https://example.com/image.jpg"
        // Missing fileName and orderReference
      };

      const result = ImageUploadSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });

    it('should reject empty strings', () => {
      const invalidData = {
        imageUrl: "https://example.com/image.jpg",
        fileName: "",
        orderReference: "VW-2024-001"
      };

      const result = ImageUploadSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
    });
  });

  describe('Edge Cases and Error Messages', () => {
    it('should provide detailed error messages', () => {
      const invalidData = {
        shopify_order_id: "", // Empty string
        customer_info: {
          email: "invalid-email", // Invalid email
          name: "",
          shipping_address: {
            address1: "",
            city: "",
            province: "",
            country: "",
            zip: ""
          }
        },
        product_configuration: {
          product_type: "invalid", // Invalid enum
          size: {
            width: -5, // Negative number
            height: 200, // Too large
            unit: "cm" // Wrong unit
          },
          quantity: 0 // Invalid quantity
        }
      };

      const result = OrderConfigSchema.safeParse(invalidData);
      expect(result.success).toBe(false);
      
      if (!result.success) {
        expect(result.error.issues.length).toBeGreaterThan(1);
        // Should have multiple validation errors
      }
    });

    it('should handle type coercion appropriately', () => {
      const dataWithStringNumbers = {
        basePrice: "57.00", // String instead of number
        productType: "canvas",
        size: { width: "24", height: "16" }
      };

      // Zod should NOT coerce these automatically in strict mode
      const result = PricingCalculationSchema.safeParse(dataWithStringNumbers);
      expect(result.success).toBe(false);
    });
  });
}); 