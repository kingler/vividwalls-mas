# Pictorem MCP Server Test Suite

This directory contains comprehensive tests for the Pictorem MCP Server to validate all tools, functions, and interfaces used for Pictorem integration.

## Test Structure

### Test Files

- **`pricing.test.ts`** - Tests VividWalls pricing logic and calculations
- **`mcp-tools.test.ts`** - Tests MCP tool functionality and API interactions  
- **`schemas.test.ts`** - Tests Zod schema validation for all input parameters
- **`setup.ts`** - Test configuration and global setup

### Test Coverage

The test suite covers:

✅ **Pricing Logic Validation**
- Canvas stretched pricing calculations
- Canvas roll pricing with additional discounts
- Size category classification
- Edge cases and error conditions
- Business logic validation

✅ **MCP Tools Testing**
- `submit-order` tool functionality
- `calculate-pricing` tool accuracy
- `get-order-status` tool responses
- `upload-image` tool handling

✅ **Authentication Testing**
- Token-based authentication
- Token caching mechanisms
- Authentication failure handling

✅ **Schema Validation**
- Order configuration schema
- Pricing calculation schema
- Order status schema
- Image upload schema
- Error message validation

✅ **Error Handling**
- Network timeouts
- API rate limiting
- Server errors
- Validation errors

## Running Tests

### All Tests
```bash
npm test
```

### Specific Test Files
```bash
# Pricing tests only
npm test pricing.test.ts

# MCP tools tests only
npm test mcp-tools.test.ts

# Schema validation tests only
npm test schemas.test.ts
```

### Test Coverage Report
```bash
npm run test:coverage
```

### Watch Mode (Development)
```bash
npm run test:watch
```

## Test Scenarios

### 1. VividWalls Pricing Logic Tests

**Canvas Stretched Pricing:**
- 12x12" canvas @ $36.00 → $63.19 (15% discount + 106.5% markup)
- 24x16" canvas @ $57.00 → $100.05 
- 36x24" canvas @ $108.00 → $189.57

**Canvas Roll Pricing (Additional 25% Discount):**
- 24x16" canvas roll @ $57.00 → $70.62 (40% total discount + 106.5% markup)
- 48x32" canvas roll @ $200.00 → $247.80

**Size Categories:**
- Small: ≤144 square inches
- Medium: 145-576 square inches  
- Large: >576 square inches

### 2. MCP Tools Validation

**submit-order Tool:**
- Valid order submission with complete data
- Order validation and error handling
- Pricing calculation integration
- Response format validation

**calculate-pricing Tool:**
- Accurate pricing calculations
- Product type handling (canvas vs canvas_roll)
- Size validation and categorization
- Input parameter validation

**get-order-status Tool:**
- Order status retrieval
- Tracking information parsing
- Error handling for invalid orders

**upload-image Tool:**
- Image file upload handling
- File size and format validation
- Error responses for oversized files

### 3. Schema Validation Tests

**Order Configuration Schema:**
- Complete order data validation
- Required vs optional field handling
- Email format validation
- Product type enumeration
- Size constraint validation (1-120 inches)
- File size limits (100MB max)
- URL format validation

**Error Scenarios:**
- Invalid email formats
- Unsupported product types
- Size constraint violations
- Oversized files
- Missing required fields

## Mock Configuration

The test suite uses:
- **Axios Mock Adapter** for API call mocking
- **Vitest mocks** for MCP SDK components
- **Environment variable mocking** for credentials

### Mock Data

**Authentication:**
```javascript
const mockToken = 'test-auth-token-123';
```

**Order Response:**
```javascript
{
  order_id: 'PICT-ORD-2024-001',
  status: 'pending',
  estimated_delivery: '2024-02-15',
  tracking_url: 'https://pictorem.com/track/...'
}
```

## Test Environment

**Environment Variables:**
- `PICTOREM_USERNAME=test@vividwalls.com`
- `PICTOREM_PASSWORD=testpassword123`

**Node Version:** >=18.0.0
**Test Framework:** Vitest
**Coverage Tool:** @vitest/coverage-v8

## Coverage Requirements

The test suite maintains the following coverage thresholds:
- **Branches:** 80%
- **Functions:** 80% 
- **Lines:** 80%
- **Statements:** 80%

## Continuous Integration

Tests are designed to run in CI/CD environments with:
- Automated mocking of external APIs
- No network dependencies
- Deterministic test results
- Fast execution times

## Test-Driven Development

Following TDD practices:
1. **Tests written before implementation** ✅
2. **Tests verify actual functionality** ✅
3. **Error scenarios covered** ✅
4. **Business logic validated** ✅
5. **Integration points tested** ✅

## Debugging Tests

### View Detailed Test Output
```bash
npm test -- --reporter=verbose
```

### Debug Specific Test
```bash
npm test -- --reporter=verbose pricing.test.ts
```

### Coverage Analysis
```bash
npm run test:coverage
# Opens HTML coverage report in browser
```

## Business Logic Validation

The tests ensure:
- **Profitable Margins:** Final prices always exceed base costs
- **Accurate Discounts:** Pro (15%) and canvas roll (25%) discounts applied correctly
- **Consistent Markup:** 106.5% markup maintained across all products
- **Size Constraints:** Physical product limits enforced (1-120 inches)
- **File Limits:** Upload size restrictions validated (100MB max)

## Integration Testing

Tests validate integration with:
- **Pictorem API endpoints**
- **Authentication system**
- **File upload handling**
- **Error response parsing**
- **MCP protocol compliance**

This comprehensive test suite ensures the Pictorem MCP Server is production-ready and maintains data integrity for VividWalls e-commerce operations. 