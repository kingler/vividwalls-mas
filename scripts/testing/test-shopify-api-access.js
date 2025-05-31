#!/usr/bin/env node

/**
 * Shopify Storefront API Test Script
 * Tests connection to the Shopify Storefront API
 */

const https = require('https');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

// Configuration from environment variables
const config = {
  storeUrl: process.env.SHOPIFY_STORE_URL || '',
  accessToken: process.env.SHOPIFY_ACCESS_TOKEN || '',
  storefrontToken: process.env.SHOPIFY_STOREFRONT_TOKEN || '',
  apiVersion: process.env.SHOPIFY_API_VERSION || '2024-01'
};

// Log with colors
function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

// Test Admin API access
function testAdminAPI() {
  return new Promise((resolve, reject) => {
    log('\n🔌 Testing Admin API Connection...', colors.cyan);
    
    const url = `https://${config.storeUrl}/admin/api/${config.apiVersion}/shop.json`;
    const options = {
      headers: {
        'X-Shopify-Access-Token': config.accessToken,
        'Content-Type': 'application/json'
      }
    };

    https.get(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const shopInfo = JSON.parse(data);
            logSuccess('Admin API connection successful');
            logInfo(`Shop name: ${shopInfo.shop.name}`);
            resolve(true);
          } catch (e) {
            logError(`Error parsing response: ${e.message}`);
            reject(e);
          }
        } else {
          logError(`Failed to connect to Admin API: HTTP ${res.statusCode}`);
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      logError(`Connection error: ${err.message}`);
      reject(err);
    });
  });
}

// Test Orders API access
function testOrdersAPI() {
  return new Promise((resolve, reject) => {
    log('\n📋 Testing Orders API Access...', colors.cyan);
    
    const url = `https://${config.storeUrl}/admin/api/${config.apiVersion}/orders.json?limit=1&status=any`;
    const options = {
      headers: {
        'X-Shopify-Access-Token': config.accessToken,
        'Content-Type': 'application/json'
      }
    };

    https.get(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const ordersData = JSON.parse(data);
            const orderCount = ordersData.orders ? ordersData.orders.length : 0;
            logSuccess(`Orders API access successful`);
            logInfo(`Retrieved ${orderCount} orders`);
            resolve(true);
          } catch (e) {
            logError(`Error parsing response: ${e.message}`);
            reject(e);
          }
        } else {
          logError(`Failed to access Orders API: HTTP ${res.statusCode}`);
          try {
            const errorData = JSON.parse(data);
            logError(`Error details: ${JSON.stringify(errorData.errors || errorData)}`);
          } catch (e) {
            logError(`Response: ${data}`);
          }
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      logError(`Connection error: ${err.message}`);
      reject(err);
    });
  });
}

// Test Customers API access
function testCustomersAPI() {
  return new Promise((resolve, reject) => {
    log('\n👥 Testing Customers API Access...', colors.cyan);
    
    const url = `https://${config.storeUrl}/admin/api/${config.apiVersion}/customers.json?limit=1`;
    const options = {
      headers: {
        'X-Shopify-Access-Token': config.accessToken,
        'Content-Type': 'application/json'
      }
    };

    https.get(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const customersData = JSON.parse(data);
            const customerCount = customersData.customers ? customersData.customers.length : 0;
            logSuccess(`Customers API access successful`);
            logInfo(`Retrieved ${customerCount} customers`);
            resolve(true);
          } catch (e) {
            logError(`Error parsing response: ${e.message}`);
            reject(e);
          }
        } else {
          logError(`Failed to access Customers API: HTTP ${res.statusCode}`);
          try {
            const errorData = JSON.parse(data);
            logError(`Error details: ${JSON.stringify(errorData.errors || errorData)}`);
          } catch (e) {
            logError(`Response: ${data}`);
          }
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      logError(`Connection error: ${err.message}`);
      reject(err);
    });
  });
}

// Test Storefront API if a token is provided
function testStorefrontAPI() {
  return new Promise((resolve, reject) => {
    if (!config.storefrontToken) {
      log('\n🛒 Skipping Storefront API test (no token provided)', colors.yellow);
      resolve(false);
      return;
    }
    
    log('\n🛒 Testing Storefront API Access...', colors.cyan);
    
    const query = `
      {
        shop {
          name
          products(first: 5) {
            edges {
              node {
                id
                title
                handle
              }
            }
          }
        }
      }
    `;
    
    const url = `https://${config.storeUrl}/api/${config.apiVersion}/graphql.json`;
    const options = {
      method: 'POST',
      headers: {
        'X-Shopify-Storefront-Access-Token': config.storefrontToken,
        'Content-Type': 'application/json'
      }
    };
    
    const req = https.request(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const graphqlData = JSON.parse(data);
            if (graphqlData.errors) {
              logError(`GraphQL errors: ${JSON.stringify(graphqlData.errors)}`);
              reject(new Error(graphqlData.errors[0].message));
              return;
            }
            
            const shopName = graphqlData.data.shop.name;
            const products = graphqlData.data.shop.products.edges;
            logSuccess(`Storefront API access successful`);
            logInfo(`Shop name: ${shopName}`);
            logInfo(`Retrieved ${products.length} products`);
            resolve(true);
          } catch (e) {
            logError(`Error parsing response: ${e.message}`);
            reject(e);
          }
        } else {
          logError(`Failed to access Storefront API: HTTP ${res.statusCode}`);
          try {
            const errorData = JSON.parse(data);
            logError(`Error details: ${JSON.stringify(errorData.errors || errorData)}`);
          } catch (e) {
            logError(`Response: ${data}`);
          }
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });
    
    req.on('error', (err) => {
      logError(`Connection error: ${err.message}`);
      reject(err);
    });
    
    req.write(JSON.stringify({ query }));
    req.end();
  });
}

// Display summary of test results
function displaySummary(results) {
  log('\n📊 API Access Summary', colors.cyan);
  log('====================');
  
  Object.keys(results).forEach(key => {
    const passed = results[key];
    if (passed) {
      logSuccess(`${key}: ACCESS GRANTED`);
    } else {
      logError(`${key}: ACCESS DENIED`);
    }
  });
  
  const totalPassed = Object.values(results).filter(Boolean).length;
  const totalTests = Object.values(results).length;
  
  log(`\n${totalPassed}/${totalTests} APIs accessible`, 
      totalPassed === totalTests ? colors.green : colors.yellow);
}

// Display instructions for updating API scope
function displayUpdateInstructions() {
  log('\n🔧 How to Update API Permissions', colors.cyan);
  log('===========================');
  log('1. Go to your Shopify admin dashboard');
  log('2. Navigate to Settings → Apps and sales channels');
  log('3. Find your private app');
  log('4. Edit its permissions to add:');
  log('   - read_orders - View orders');
  log('   - read_customers - View customer information');
  log('5. Save changes and regenerate the API credentials');
  log('6. Update your configuration with the new access token\n');
}

// Main function to run all tests
async function runTests() {
  log('🔍 Shopify API Access Test', colors.cyan);
  log('======================');
  
  if (!config.storeUrl || !config.accessToken) {
    logError('Missing required environment variables:');
    if (!config.storeUrl) logError('- SHOPIFY_STORE_URL');
    if (!config.accessToken) logError('- SHOPIFY_ACCESS_TOKEN');
    process.exit(1);
  }
  
  logInfo(`Testing store: ${config.storeUrl}`);
  logInfo(`API version: ${config.apiVersion}`);
  
  const results = {
    'Admin API': false,
    'Orders API': false,
    'Customers API': false
  };
  
  if (config.storefrontToken) {
    results['Storefront API'] = false;
  }
  
  try {
    // Test Admin API (always run first)
    results['Admin API'] = await testAdminAPI();
    
    // Test other APIs
    try {
      results['Orders API'] = await testOrdersAPI();
    } catch (e) {
      // Already logged error in function
    }
    
    try {
      results['Customers API'] = await testCustomersAPI();
    } catch (e) {
      // Already logged error in function
    }
    
    if (config.storefrontToken) {
      try {
        results['Storefront API'] = await testStorefrontAPI();
      } catch (e) {
        // Already logged error in function
      }
    }
    
    // Display results summary
    displaySummary(results);
    
    // If any API access is denied, show instructions
    if (Object.values(results).some(result => result === false)) {
      displayUpdateInstructions();
    }
    
  } catch (e) {
    logError(`Test failed: ${e.message}`);
    process.exit(1);
  }
}

// Run tests
runTests();
