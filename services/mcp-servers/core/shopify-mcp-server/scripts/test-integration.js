#!/usr/bin/env node

/**
 * VividWalls CopilotKit Integration Test Script
 * Tests the Shopify theme integration and n8n webhook connectivity
 */

import { spawn } from 'child_process';
import fetch from 'node-fetch';

const SHOPIFY_MCP_SERVER = './build/index.js';
const N8N_WEBHOOK_URL = 'http://157.230.13.13:5678/webhook/vividwalls-chat';

// Colors for console output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

async function createMCPRequest(tool, args) {
    return new Promise((resolve, reject) => {
        const server = spawn('node', [SHOPIFY_MCP_SERVER], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let errorOutput = '';

        server.stdout.on('data', (data) => {
            output += data.toString();
        });

        server.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        server.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(output);
                    resolve(result);
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${e.message}`));
                }
            } else {
                reject(new Error(`MCP server failed with code ${code}: ${errorOutput}`));
            }
        });

        const request = {
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/call',
            params: {
                name: tool,
                arguments: args
            }
        };

        server.stdin.write(JSON.stringify(request) + '\n');
        server.stdin.end();
    });
}

async function testEnvironmentVariables() {
    log('\n🔧 Testing Environment Variables...', 'blue');
    
    const requiredEnvVars = ['SHOPIFY_ACCESS_TOKEN', 'MYSHOPIFY_DOMAIN'];
    let allPresent = true;

    for (const envVar of requiredEnvVars) {
        if (process.env[envVar]) {
            log(`  ✅ ${envVar}: Set`, 'green');
        } else {
            log(`  ❌ ${envVar}: Missing`, 'red');
            allPresent = false;
        }
    }

    if (!allPresent) {
        throw new Error('Required environment variables are missing');
    }
}

async function testShopifyConnection() {
    log('\n🏪 Testing Shopify Connection...', 'blue');
    
    try {
        const shopResponse = await createMCPRequest('get-shop', {});
        const shop = JSON.parse(shopResponse.content[0].text);
        
        log(`  ✅ Connected to shop: ${shop.shop.name}`, 'green');
        log(`  📧 Email: ${shop.shop.email}`, 'reset');
        log(`  🌐 Domain: ${shop.shop.domain}`, 'reset');
        
        return shop;
    } catch (error) {
        log(`  ❌ Failed to connect to Shopify: ${error.message}`, 'red');
        throw error;
    }
}

async function testThemeAccess() {
    log('\n🎨 Testing Theme Access...', 'blue');
    
    try {
        const themesResponse = await createMCPRequest('get-themes', {});
        const themes = JSON.parse(themesResponse.content[0].text);
        
        log(`  ✅ Found ${themes.themes.length} themes`, 'green');
        
        const activeTheme = themes.themes.find(theme => theme.role === 'main');
        if (activeTheme) {
            log(`  🎯 Active theme: ${activeTheme.name} (ID: ${activeTheme.id})`, 'green');
            
            // Test theme asset access
            const assetsResponse = await createMCPRequest('get-theme-assets', {
                themeId: activeTheme.id.toString()
            });
            const assets = JSON.parse(assetsResponse.content[0].text);
            
            const themeLiquid = assets.assets.find(asset => asset.key === 'layout/theme.liquid');
            if (themeLiquid) {
                log(`  ✅ theme.liquid accessible`, 'green');
            } else {
                log(`  ❌ theme.liquid not found`, 'red');
                throw new Error('Cannot access theme.liquid');
            }
            
            return activeTheme;
        } else {
            log(`  ❌ No active theme found`, 'red');
            throw new Error('No active theme found');
        }
    } catch (error) {
        log(`  ❌ Failed to access themes: ${error.message}`, 'red');
        throw error;
    }
}

async function testWebhookConnectivity() {
    log('\n🔗 Testing n8n Webhook Connectivity...', 'blue');
    
    try {
        const testPayload = {
            chatInput: 'Test connection from integration script',
            sessionId: 'test_session_' + Date.now(),
            pageContext: {
                url: 'https://test.com',
                type: 'test',
                title: 'Integration Test'
            },
            timestamp: new Date().toISOString()
        };

        const response = await fetch(N8N_WEBHOOK_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testPayload),
            timeout: 10000
        });

        if (response.ok) {
            log(`  ✅ Webhook responded with status: ${response.status}`, 'green');
            
            try {
                const responseData = await response.json();
                log(`  📨 Response received: ${JSON.stringify(responseData).substring(0, 100)}...`, 'reset');
            } catch (e) {
                log(`  📨 Response received (non-JSON)`, 'reset');
            }
            
            return true;
        } else {
            log(`  ⚠️  Webhook responded with status: ${response.status}`, 'yellow');
            log(`  📝 This may be normal if n8n expects specific payload format`, 'yellow');
            return false;
        }
    } catch (error) {
        if (error.name === 'FetchError' && error.code === 'ECONNREFUSED') {
            log(`  ❌ Cannot connect to webhook: ${N8N_WEBHOOK_URL}`, 'red');
            log(`  💡 Make sure n8n is running and accessible`, 'yellow');
        } else {
            log(`  ❌ Webhook test failed: ${error.message}`, 'red');
        }
        return false;
    }
}

async function testIntegrationStatus(activeTheme) {
    log('\n🧪 Testing Integration Status...', 'blue');
    
    try {
        const themeContentResponse = await createMCPRequest('get-theme-asset', {
            themeId: activeTheme.id.toString(),
            assetKey: 'layout/theme.liquid'
        });
        const themeContent = JSON.parse(themeContentResponse.content[0].text);
        const content = themeContent.asset.value;

        // Check for VividWalls integration
        const hasVividWallsCSS = content.includes('VividWalls CopilotKit Styles');
        const hasVividWallsJS = content.includes('VividWalls CopilotKit Integration');
        const hasReactCDN = content.includes('unpkg.com/react');

        if (hasVividWallsCSS && hasVividWallsJS) {
            log(`  ✅ VividWalls integration is installed`, 'green');
            log(`  🎨 CSS integration: Found`, 'green');
            log(`  ⚙️  JavaScript integration: Found`, 'green');
            
            if (hasReactCDN) {
                log(`  ⚛️  React CDN loading: Found`, 'green');
            } else {
                log(`  ⚛️  React CDN loading: Not found (may load dynamically)`, 'yellow');
            }
            
            return true;
        } else {
            log(`  ❌ VividWalls integration not found in theme`, 'red');
            log(`  🎨 CSS integration: ${hasVividWallsCSS ? 'Found' : 'Missing'}`, hasVividWallsCSS ? 'green' : 'red');
            log(`  ⚙️  JavaScript integration: ${hasVividWallsJS ? 'Found' : 'Missing'}`, hasVividWallsJS ? 'green' : 'red');
            return false;
        }
    } catch (error) {
        log(`  ❌ Failed to check integration status: ${error.message}`, 'red');
        return false;
    }
}

async function testProductDataAccess() {
    log('\n📦 Testing Product Data Access...', 'blue');
    
    try {
        const productsResponse = await createMCPRequest('get-products', { limit: 3 });
        const content = productsResponse.content[0].text;
        
        if (content.includes('Product:')) {
            const productCount = (content.match(/Product:/g) || []).length;
            log(`  ✅ Can access product data (${productCount} products tested)`, 'green');
            return true;
        } else {
            log(`  ❌ No product data found`, 'red');
            return false;
        }
    } catch (error) {
        log(`  ❌ Failed to access product data: ${error.message}`, 'red');
        return false;
    }
}

async function generateTestReport(results) {
    log('\n📊 Test Report', 'bold');
    log('='.repeat(50), 'reset');
    
    const tests = [
        { name: 'Environment Variables', status: results.envVars },
        { name: 'Shopify Connection', status: results.shopifyConnection },
        { name: 'Theme Access', status: results.themeAccess },
        { name: 'Webhook Connectivity', status: results.webhookConnectivity },
        { name: 'Integration Status', status: results.integrationStatus },
        { name: 'Product Data Access', status: results.productDataAccess }
    ];

    let passedTests = 0;
    let totalTests = tests.length;

    tests.forEach(test => {
        const icon = test.status ? '✅' : '❌';
        const color = test.status ? 'green' : 'red';
        log(`${icon} ${test.name}`, color);
        if (test.status) passedTests++;
    });

    log('\n📈 Summary:', 'bold');
    log(`  Passed: ${passedTests}/${totalTests} tests`, passedTests === totalTests ? 'green' : 'yellow');
    
    if (passedTests === totalTests) {
        log('\n🎉 All tests passed! Your VividWalls integration is ready.', 'green');
        log('\n🚀 Next steps:', 'blue');
        log('  1. Visit your Shopify store', 'reset');
        log('  2. Look for the floating "Get Art Recommendations" button', 'reset');
        log('  3. Test the AI assistant with various questions', 'reset');
        log('  4. Try uploading a room photo for analysis', 'reset');
    } else {
        log('\n⚠️  Some tests failed. Please review the issues above.', 'yellow');
        
        if (!results.envVars) {
            log('\n🔧 Environment Setup:', 'blue');
            log('  export SHOPIFY_ACCESS_TOKEN="your_token_here"', 'reset');
            log('  export MYSHOPIFY_DOMAIN="your-store.myshopify.com"', 'reset');
        }
        
        if (!results.integrationStatus) {
            log('\n🔧 Install Integration:', 'blue');
            log('  npm run build', 'reset');
            log('  node scripts/create-vividwalls-copilot-integration.js', 'reset');
        }
        
        if (!results.webhookConnectivity) {
            log('\n🔧 Check n8n Setup:', 'blue');
            log('  • Ensure n8n is running at: http://157.230.13.13:5678', 'reset');
            log('  • Verify webhook endpoint is configured', 'reset');
            log('  • Check firewall and network connectivity', 'reset');
        }
    }
}

async function main() {
    log('🧪 VividWalls CopilotKit Integration Test Suite', 'bold');
    log('='.repeat(60), 'reset');
    
    const results = {
        envVars: false,
        shopifyConnection: false,
        themeAccess: false,
        webhookConnectivity: false,
        integrationStatus: false,
        productDataAccess: false
    };

    try {
        // Test environment variables
        await testEnvironmentVariables();
        results.envVars = true;

        // Test Shopify connection
        const shop = await testShopifyConnection();
        results.shopifyConnection = true;

        // Test theme access
        const activeTheme = await testThemeAccess();
        results.themeAccess = true;

        // Test webhook connectivity (non-blocking)
        results.webhookConnectivity = await testWebhookConnectivity();

        // Test integration status
        results.integrationStatus = await testIntegrationStatus(activeTheme);

        // Test product data access
        results.productDataAccess = await testProductDataAccess();

    } catch (error) {
        log(`\n💥 Test suite failed: ${error.message}`, 'red');
    }

    await generateTestReport(results);
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { main as testIntegration };