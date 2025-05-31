#!/usr/bin/env node

/**
 * Shopify MCP Connection Test Script
 * This script tests the connection to your Shopify store using MCP
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  storeUrl: process.env.SHOPIFY_STORE_URL || '',
  accessToken: process.env.SHOPIFY_ACCESS_TOKEN || '',
  apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01'
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

// Validate configuration
function validateConfig() {
  log('\n🔍 Validating Shopify Configuration...', colors.cyan);
  
  if (!config.storeUrl) {
    logError('SHOPIFY_STORE_URL is not set');
    return false;
  }
  
  if (!config.accessToken) {
    logError('SHOPIFY_ACCESS_TOKEN is not set');
    return false;
  }
  
  if (!config.storeUrl.includes('.myshopify.com')) {
    logWarning('Store URL should include .myshopify.com domain');
  }
  
  if (!config.accessToken.startsWith('shpat_')) {
    logWarning('Access token should start with shpat_');
  }
  
  logSuccess('Configuration validation passed');
  return true;
}

// Make Shopify API request
function makeShopifyRequest(endpoint, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const url = `https://${config.storeUrl}/admin/api/${config.apiVersion}/${endpoint}`;
    const urlObj = new URL(url);
    
    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'X-Shopify-Access-Token': config.accessToken,
        'Content-Type': 'application/json',
        'User-Agent': 'VividMAS-Shopify-MCP-Test/1.0'
      }
    };
    
    if (data && method !== 'GET') {
      const jsonData = JSON.stringify(data);
      options.headers['Content-Length'] = Buffer.byteLength(jsonData);
    }
    
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonResponse = JSON.parse(responseData);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(jsonResponse);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${jsonResponse.errors || responseData}`));
          }
        } catch (error) {
          reject(new Error(`Invalid JSON response: ${responseData}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    if (data && method !== 'GET') {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// Test basic connection
async function testConnection() {
  log('\n🔌 Testing Shopify Connection...', colors.cyan);
  
  try {
    const response = await makeShopifyRequest('shop.json');
    logSuccess('Successfully connected to Shopify!');
    logInfo(`Store: ${response.shop.name}`);
    logInfo(`Domain: ${response.shop.domain}`);
    logInfo(`Currency: ${response.shop.currency}`);
    return true;
  } catch (error) {
    logError(`Connection failed: ${error.message}`);
    return false;
  }
}

// Test products API
async function testProducts() {
  log('\n📦 Testing Products API...', colors.cyan);
  
  try {
    const response = await makeShopifyRequest('products.json?limit=5');
    logSuccess(`Found ${response.products.length} products`);
    
    if (response.products.length > 0) {
      const product = response.products[0];
      logInfo(`Sample product: ${product.title}`);
      logInfo(`Product ID: ${product.id}`);
      logInfo(`Variants: ${product.variants.length}`);
    }
    
    return true;
  } catch (error) {
    logError(`Products API test failed: ${error.message}`);
    return false;
  }
}

// Test orders API
async function testOrders() {
  log('\n📋 Testing Orders API...', colors.cyan);
  
  try {
    const response = await makeShopifyRequest('orders.json?limit=5&status=any');
    logSuccess(`Found ${response.orders.length} orders`);
    
    if (response.orders.length > 0) {
      const order = response.orders[0];
      logInfo(`Sample order: #${order.order_number}`);
      logInfo(`Total: ${order.total_price} ${order.currency}`);
      logInfo(`Status: ${order.financial_status}`);
    }
    
    return true;
  } catch (error) {
    logError(`Orders API test failed: ${error.message}`);
    return false;
  }
}

// Test customers API
async function testCustomers() {
  log('\n👥 Testing Customers API...', colors.cyan);
  
  try {
    const response = await makeShopifyRequest('customers.json?limit=5');
    logSuccess(`Found ${response.customers.length} customers`);
    
    if (response.customers.length > 0) {
      const customer = response.customers[0];
      logInfo(`Sample customer: ${customer.first_name} ${customer.last_name}`);
      logInfo(`Email: ${customer.email}`);
      logInfo(`Orders count: ${customer.orders_count}`);
    }
    
    return true;
  } catch (error) {
    logError(`Customers API test failed: ${error.message}`);
    return false;
  }
}

// Check VividWalls specific products
async function checkVividWallsProducts() {
  log('\n🎨 Checking VividWalls Art Products...', colors.cyan);
  
  try {
    const response = await makeShopifyRequest('products.json?limit=250');
    const artProducts = response.products.filter(product => {
      const title = product.title.toLowerCase();
      const hasTags = product.tags && typeof product.tags === 'string' 
        ? product.tags.toLowerCase().includes('artwork')
        : Array.isArray(product.tags) 
          ? product.tags.some(tag => tag.toLowerCase().includes('artwork'))
          : false;
      
      return title.includes('chromatic echoes') || 
             title.includes('deep echoes') || 
             title.includes('art') ||
             hasTags;
    });
    
    logSuccess(`Found ${artProducts.length} art products`);
    
    if (artProducts.length > 0) {
      logInfo('Art collections found:');
      const collections = [...new Set(artProducts.map(p => p.product_type))];
      collections.forEach(collection => {
        logInfo(`  - ${collection}`);
      });
      
      // Check frame variants
      const frameVariants = artProducts.reduce((acc, product) => {
        product.variants.forEach(variant => {
          if (variant.title.toLowerCase().includes('frame')) {
            acc.add(variant.title);
          }
        });
        return acc;
      }, new Set());
      
      if (frameVariants.size > 0) {
        logInfo('Frame options available:');
        frameVariants.forEach(frame => {
          logInfo(`  - ${frame}`);
        });
      }
    }
    
    return true;
  } catch (error) {
    logError(`VividWalls products check failed: ${error.message}`);
    return false;
  }
}

// Generate test report
function generateReport(results) {
  log('\n📊 Test Results Summary', colors.cyan);
  log('=' * 50);
  
  const tests = [
    { name: 'Configuration', passed: results.config },
    { name: 'Connection', passed: results.connection },
    { name: 'Products API', passed: results.products },
    { name: 'Orders API', passed: results.orders },
    { name: 'Customers API', passed: results.customers },
    { name: 'VividWalls Products', passed: results.vividwalls }
  ];
  
  tests.forEach(test => {
    if (test.passed) {
      logSuccess(`${test.name}: PASSED`);
    } else {
      logError(`${test.name}: FAILED`);
    }
  });
  
  const totalPassed = tests.filter(t => t.passed).length;
  const totalTests = tests.length;
  
  log(`\nOverall: ${totalPassed}/${totalTests} tests passed`, 
      totalPassed === totalTests ? colors.green : colors.yellow);
  
  if (totalPassed === totalTests) {
    logSuccess('\n🎉 All tests passed! Your Shopify MCP integration is ready!');
  } else {
    logWarning('\n⚠️  Some tests failed. Please check your configuration and try again.');
  }
}

// Main test function
async function runTests() {
  log('🚀 VividMAS Shopify MCP Connection Test', colors.cyan);
  log('=' * 50);
  
  const results = {
    config: false,
    connection: false,
    products: false,
    orders: false,
    customers: false,
    vividwalls: false
  };
  
  try {
    // Test configuration
    results.config = validateConfig();
    if (!results.config) {
      log('\n❌ Configuration validation failed. Please check your environment variables.');
      log('\nRequired environment variables:');
      log('- SHOPIFY_STORE_URL (e.g., your-store.myshopify.com)');
      log('- SHOPIFY_ACCESS_TOKEN (starts with shpat_)');
      log('- SHOPIFY_API_VERSION (optional, defaults to 2024-01)');
      process.exit(1);
    }
    
    // Test connection
    results.connection = await testConnection();
    if (!results.connection) {
      process.exit(1);
    }
    
    // Test APIs
    results.products = await testProducts();
    results.orders = await testOrders();
    results.customers = await testCustomers();
    results.vividwalls = await checkVividWallsProducts();
    
  } catch (error) {
    logError(`Unexpected error: ${error.message}`);
    process.exit(1);
  }
  
  // Generate report
  generateReport(results);
}

// Run the tests
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests,
  makeShopifyRequest,
  validateConfig
};
