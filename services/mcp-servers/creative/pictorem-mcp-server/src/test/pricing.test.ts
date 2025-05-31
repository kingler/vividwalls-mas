/**
 * Test suite for VividWalls pricing calculations
 * Tests the core business logic for canvas print pricing
 */

import { describe, it, expect } from 'vitest';

/**
 * VividWalls pricing calculation function (extracted for testing)
 * This mirrors the pricing logic in the MCP server
 */
function calculateVividWallsPricing(
  basePrice: number,
  productType: 'canvas' | 'canvas_roll',
  size: { width: number; height: number }
) {
  // VividWalls pricing logic
  const proDiscount = 0.15; // 15% Pro account discount
  const canvasRollDiscount = productType === 'canvas_roll' ? 0.25 : 0; // 25% additional for canvas roll
  const vividwallsMarkup = 2.065; // 106.5% markup
  
  const totalDiscount = proDiscount + canvasRollDiscount;
  const discountedPrice = basePrice * (1 - totalDiscount);
  const finalPrice = discountedPrice * vividwallsMarkup;
  
  // Calculate square inches for size validation
  const squareInches = size.width * size.height;
  
  return {
    base_price: basePrice,
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

describe('VividWalls Pricing Logic', () => {
  describe('Canvas Stretched Pricing', () => {
    it('should calculate correct pricing for 12x12 canvas stretched', () => {
      const result = calculateVividWallsPricing(36.00, 'canvas', { width: 12, height: 12 });
      
      expect(result.base_price).toBe(36.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0);
      expect(result.total_discount).toBe(0.15);
      expect(result.discounted_price).toBeCloseTo(30.60, 2); // 36 * (1 - 0.15)
      expect(result.final_price).toBeCloseTo(63.19, 2); // 30.60 * 2.065
      expect(result.square_inches).toBe(144);
      expect(result.size_category).toBe('small');
    });

    it('should calculate correct pricing for 24x16 canvas stretched', () => {
      const result = calculateVividWallsPricing(57.00, 'canvas', { width: 24, height: 16 });
      
      expect(result.base_price).toBe(57.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0);
      expect(result.total_discount).toBe(0.15);
      expect(result.discounted_price).toBeCloseTo(48.45, 2); // 57 * (1 - 0.15)
      expect(result.final_price).toBeCloseTo(100.05, 2); // 48.45 * 2.065
      expect(result.square_inches).toBe(384);
      expect(result.size_category).toBe('medium');
    });

    it('should calculate correct pricing for 36x24 canvas stretched', () => {
      const result = calculateVividWallsPricing(108.00, 'canvas', { width: 36, height: 24 });
      
      expect(result.base_price).toBe(108.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0);
      expect(result.total_discount).toBe(0.15);
      expect(result.discounted_price).toBe(91.80); // 108 * (1 - 0.15)
      expect(result.final_price).toBeCloseTo(189.57, 2); // 91.80 * 2.065
      expect(result.square_inches).toBe(864);
      expect(result.size_category).toBe('large');
    });
  });

  describe('Canvas Roll Pricing (Additional 25% Discount)', () => {
    it('should calculate correct pricing for 24x16 canvas roll', () => {
      const result = calculateVividWallsPricing(57.00, 'canvas_roll', { width: 24, height: 16 });
      
      expect(result.base_price).toBe(57.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0.25);
      expect(result.total_discount).toBe(0.40); // 15% + 25%
      expect(result.discounted_price).toBeCloseTo(34.20, 2); // 57 * (1 - 0.40)
      expect(result.final_price).toBeCloseTo(70.62, 2); // 34.20 * 2.065
      expect(result.square_inches).toBe(384);
      expect(result.size_category).toBe('medium');
    });

    it('should apply maximum discounts for large canvas roll', () => {
      const result = calculateVividWallsPricing(200.00, 'canvas_roll', { width: 48, height: 32 });
      
      expect(result.base_price).toBe(200.00);
      expect(result.pro_discount).toBe(0.15);
      expect(result.canvas_roll_discount).toBe(0.25);
      expect(result.total_discount).toBe(0.40);
      expect(result.discounted_price).toBe(120.00); // 200 * (1 - 0.40)
      expect(result.final_price).toBeCloseTo(247.80, 2); // 120 * 2.065
      expect(result.square_inches).toBe(1536);
      expect(result.size_category).toBe('large');
    });
  });

  describe('Size Categories', () => {
    it('should classify small sizes correctly (≤144 sq in)', () => {
      const result = calculateVividWallsPricing(30.00, 'canvas', { width: 12, height: 12 });
      expect(result.size_category).toBe('small');
      expect(result.square_inches).toBe(144);
    });

    it('should classify medium sizes correctly (145-576 sq in)', () => {
      const result = calculateVividWallsPricing(50.00, 'canvas', { width: 16, height: 20 });
      expect(result.size_category).toBe('medium');
      expect(result.square_inches).toBe(320);
    });

    it('should classify large sizes correctly (>576 sq in)', () => {
      const result = calculateVividWallsPricing(100.00, 'canvas', { width: 30, height: 20 });
      expect(result.size_category).toBe('large');
      expect(result.square_inches).toBe(600);
    });
  });

  describe('Edge Cases', () => {
    it('should handle minimum size (1x1)', () => {
      const result = calculateVividWallsPricing(10.00, 'canvas', { width: 1, height: 1 });
      
      expect(result.discounted_price).toBe(8.50); // 10 * (1 - 0.15)
      expect(result.final_price).toBeCloseTo(17.55, 2); // 8.50 * 2.065
      expect(result.square_inches).toBe(1);
      expect(result.size_category).toBe('small');
    });

    it('should handle maximum size (120x120)', () => {
      const result = calculateVividWallsPricing(500.00, 'canvas_roll', { width: 120, height: 120 });
      
      expect(result.discounted_price).toBe(300.00); // 500 * (1 - 0.40)
      expect(result.final_price).toBeCloseTo(619.50, 2); // 300 * 2.065
      expect(result.square_inches).toBe(14400);
      expect(result.size_category).toBe('large');
    });

    it('should handle decimal pricing accurately', () => {
      const result = calculateVividWallsPricing(36.99, 'canvas', { width: 12, height: 12 });
      
      expect(result.discounted_price).toBeCloseTo(31.44, 2); // 36.99 * (1 - 0.15)
      expect(result.final_price).toBeCloseTo(64.93, 2); // More accurate expectation
    });
  });

  describe('Pricing Formula Validation', () => {
    it('should maintain correct markup percentage', () => {
      const basePrice = 100.00;
      const result = calculateVividWallsPricing(basePrice, 'canvas', { width: 20, height: 20 });
      
      // Verify markup is exactly 106.5%
      const expectedMarkup = 2.065;
      expect(result.vividwalls_markup).toBe(expectedMarkup);
      
      // Verify final price calculation
      const expectedFinalPrice = result.discounted_price * expectedMarkup;
      expect(result.final_price).toBeCloseTo(expectedFinalPrice, 2);
    });

    it('should apply discounts in correct order', () => {
      const basePrice = 100.00;
      
      // Test canvas stretched (15% discount only)
      const canvasResult = calculateVividWallsPricing(basePrice, 'canvas', { width: 20, height: 20 });
      expect(canvasResult.total_discount).toBe(0.15);
      
      // Test canvas roll (15% + 25% = 40% total discount)
      const rollResult = calculateVividWallsPricing(basePrice, 'canvas_roll', { width: 20, height: 20 });
      expect(rollResult.total_discount).toBe(0.40);
      
      // Verify canvas roll is cheaper than canvas stretched
      expect(rollResult.final_price).toBeLessThan(canvasResult.final_price);
    });
  });

  describe('Business Logic Validation', () => {
    it('should ensure profitable margins', () => {
      const testCases = [
        { price: 30, type: 'canvas' as const, size: { width: 12, height: 12 } },
        { price: 50, type: 'canvas_roll' as const, size: { width: 16, height: 16 } },
        { price: 100, type: 'canvas' as const, size: { width: 24, height: 24 } }
      ];
      
      testCases.forEach(({ price, type, size }) => {
        const result = calculateVividWallsPricing(price, type, size);
        
        // Final price should always be higher than base price (profitable)
        expect(result.final_price).toBeGreaterThan(result.base_price);
        
        // Markup should provide at least 100% increase even after max discounts
        const maxDiscountedPrice = price * 0.60; // Worst case: 40% discount
        expect(result.final_price).toBeGreaterThan(maxDiscountedPrice * 2);
      });
    });

    it('should maintain consistent discount rates', () => {
      const PRO_DISCOUNT = 0.15;
      const CANVAS_ROLL_DISCOUNT = 0.25;
      const VIVIDWALLS_MARKUP = 2.065;
      
      const result = calculateVividWallsPricing(100, 'canvas_roll', { width: 20, height: 20 });
      
      expect(result.pro_discount).toBe(PRO_DISCOUNT);
      expect(result.canvas_roll_discount).toBe(CANVAS_ROLL_DISCOUNT);
      expect(result.vividwalls_markup).toBe(VIVIDWALLS_MARKUP);
    });
  });
}); 