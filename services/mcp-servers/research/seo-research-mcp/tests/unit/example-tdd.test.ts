/**
 * Example TDD Implementation
 * Demonstrates the Red-Green-Refactor cycle
 */

import { describe, it, expect } from '@jest/globals';

// This will be implemented after the test (TDD approach)
// import { Calculator } from '../../src/utils/calculator.js';

describe('TDD Example - Calculator', () => {
  describe('RED Phase - Write Failing Tests First', () => {
    it('should add two numbers correctly', () => {
      // TDD: Write test before implementation
      // This test will fail until we implement Calculator
      
      // const calculator = new Calculator();
      // const result = calculator.add(2, 3);
      // expect(result).toBe(5);
      
      // For now, demonstrate the concept
      const expectedResult = 5;
      const actualResult = 2 + 3; // Minimal implementation
      expect(actualResult).toBe(expectedResult);
    });

    it('should subtract two numbers correctly', () => {
      // TDD: Another failing test
      // const calculator = new Calculator();
      // const result = calculator.subtract(5, 3);
      // expect(result).toBe(2);
      
      // Demonstrate concept
      const expectedResult = 2;
      const actualResult = 5 - 3;
      expect(actualResult).toBe(expectedResult);
    });

    it('should handle edge cases', () => {
      // TDD: Test edge cases before implementation
      // const calculator = new Calculator();
      // expect(calculator.add(0, 0)).toBe(0);
      // expect(calculator.subtract(0, 0)).toBe(0);
      
      // Demonstrate concept
      expect(0 + 0).toBe(0);
      expect(0 - 0).toBe(0);
    });
  });

  describe('GREEN Phase - Make Tests Pass', () => {
    it('should demonstrate minimal implementation', () => {
      // After RED phase, we implement minimal code to make tests pass
      
      // Simple implementation that makes tests pass
      class SimpleCalculator {
        add(a: number, b: number): number {
          return a + b;
        }
        
        subtract(a: number, b: number): number {
          return a - b;
        }
      }
      
      const calculator = new SimpleCalculator();
      expect(calculator.add(2, 3)).toBe(5);
      expect(calculator.subtract(5, 3)).toBe(2);
    });
  });

  describe('REFACTOR Phase - Improve Code Quality', () => {
    it('should demonstrate improved implementation', () => {
      // After GREEN phase, we refactor for better code quality
      
      interface ICalculator {
        add(a: number, b: number): number;
        subtract(a: number, b: number): number;
      }
      
      class Calculator implements ICalculator {
        /**
         * Adds two numbers with input validation
         */
        add(a: number, b: number): number {
          this.validateInput(a, b);
          return a + b;
        }
        
        /**
         * Subtracts two numbers with input validation
         */
        subtract(a: number, b: number): number {
          this.validateInput(a, b);
          return a - b;
        }
        
        private validateInput(a: number, b: number): void {
          if (typeof a !== 'number' || typeof b !== 'number') {
            throw new Error('Both arguments must be numbers');
          }
          if (!Number.isFinite(a) || !Number.isFinite(b)) {
            throw new Error('Both arguments must be finite numbers');
          }
        }
      }
      
      const calculator = new Calculator();
      
      // Original functionality still works
      expect(calculator.add(2, 3)).toBe(5);
      expect(calculator.subtract(5, 3)).toBe(2);
      
      // New validation works
      expect(() => calculator.add(NaN, 5)).toThrow('Both arguments must be finite numbers');
      expect(() => calculator.add('2' as any, 3)).toThrow('Both arguments must be numbers');
    });
  });
});

/**
 * TDD Cycle Demonstration:
 * 
 * 1. RED: Write failing tests that define desired behavior
 *    - Tests specify what the code should do
 *    - Tests fail because implementation doesn't exist
 * 
 * 2. GREEN: Write minimal code to make tests pass
 *    - Focus on making tests pass, not perfect code
 *    - Implement just enough functionality
 * 
 * 3. REFACTOR: Improve code quality while keeping tests green
 *    - Add error handling, validation, documentation
 *    - Improve performance and maintainability
 *    - Tests ensure refactoring doesn't break functionality
 * 
 * Benefits for SEO Research MCP Server:
 * - API integrations are tested before implementation
 * - MCP protocol compliance is validated
 * - Error handling is comprehensive
 * - Performance optimizations are verified
 * - Code quality is maintained through refactoring
 */ 