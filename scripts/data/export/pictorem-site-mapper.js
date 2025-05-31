#!/usr/bin/env node

/**
 * Pictorem Site Mapping Tool
 * 
 * This tool systematically maps the complete Pictorem order flow
 * to capture all pages, selectors, form fields, and navigation patterns
 * needed for accurate browser automation.
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

class PictoremSiteMapper {
    constructor(credentials = {}) {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.username = credentials.username || null;
        this.password = credentials.password || null;
        this.isAuthenticated = false;
        this.mapping = {
            metadata: {
                mapped_date: new Date().toISOString(),
                site_url: 'https://www.pictorem.com',
                mapper_version: '1.0.0',
                authenticated: false
            },
            authentication: {},
            upload_flow: {},
            product_configuration: {},
            pricing: {},
            checkout_flow: {},
            payment_methods: {},
            order_confirmation: {},
            navigation: {},
            error_patterns: {}
        };
    }

    async promptForCredentials() {
        if (this.username && this.password) {
            console.log('✅ Using provided credentials');
            return;
        }

        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        console.log('\n🔐 Pictorem Login Required');
        console.log('To map the complete order flow, we need to authenticate with your Pictorem account.');
        
        if (!this.username) {
            this.username = await new Promise(resolve => {
                rl.question('📧 Enter your Pictorem email: ', resolve);
            });
        }

        if (!this.password) {
            this.password = await new Promise(resolve => {
                rl.question('🔑 Enter your Pictorem password: ', (answer) => {
                    console.log('🔒 Password entered (hidden for security)');
                    resolve(answer);
                });
            });
        }

        rl.close();
        console.log('✅ Credentials collected\n');
    }

    async initialize() {
        console.log('🎭 Initializing Pictorem Site Mapper...');
        
        this.browser = await chromium.launch({ 
            headless: false, // Keep visible for mapping and debugging
            slowMo: 500 // Slow down for observation
        });
        
        this.context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        });
        
        this.page = await this.context.newPage();
        
        // Set longer timeout for slow loading
        this.page.setDefaultTimeout(60000);
        
        // Enable request/response logging for debugging
        this.page.on('request', request => {
            if (request.url().includes('pictorem.com') && !request.url().includes('.jpg') && !request.url().includes('.png') && !request.url().includes('.gif')) {
                console.log(`📤 ${request.method()} ${request.url().substring(0, 100)}...`);
            }
        });
        
        this.page.on('response', response => {
            if (response.url().includes('pictorem.com') && response.status() >= 400) {
                console.log(`📥 ${response.status()} ${response.url()}`);
            }
        });
    }

    async performAuthentication() {
        console.log('\n🔐 Performing Authentication...');
        
        try {
            // Navigate to correct login page
            await this.page.goto('https://www.pictorem.com/myaccount.html', { 
                waitUntil: 'domcontentloaded',
                timeout: 60000 
            });
            
            // Wait for page to stabilize
            await this.page.waitForTimeout(3000);
            
            console.log('📍 Current URL:', this.page.url());
            
            // Look for email field with multiple possible selectors
            const emailSelectors = [
                'input[name="email"]',
                'input[name="login[username]"]',
                'input[name="username"]',
                'input[type="email"]',
                '#email',
                '#username',
                '.email-input',
                'input[placeholder*="email" i]'
            ];
            
            let emailField = null;
            for (const selector of emailSelectors) {
                try {
                    emailField = this.page.locator(selector).first();
                    if (await emailField.isVisible({ timeout: 5000 })) {
                        console.log(`✅ Email field found: ${selector}`);
                        this.mapping.authentication.email_field = selector;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!emailField) {
                throw new Error('Could not find email input field');
            }
            
            // Look for password field with expanded selectors
            const passwordSelectors = [
                'input[name="password"]',
                'input[name="login[password]"]',
                'input[type="password"]',
                '#password',
                '.password-input',
                'input[placeholder*="password" i]',
                'input[class*="password"]',
                'input[id*="password"]'
            ];
            
            let passwordField = null;
            for (const selector of passwordSelectors) {
                try {
                    passwordField = this.page.locator(selector).first();
                    if (await passwordField.isVisible({ timeout: 5000 })) {
                        console.log(`✅ Password field found: ${selector}`);
                        this.mapping.authentication.password_field = selector;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!passwordField) {
                // Debug: Let's see what password inputs exist
                console.log('🔍 Debugging password field...');
                const allPasswords = await this.page.locator('input[type="password"]').all();
                console.log(`Found ${allPasswords.length} password fields`);
                
                if (allPasswords.length > 0) {
                    passwordField = allPasswords[0];
                    this.mapping.authentication.password_field = 'input[type="password"]';
                    console.log('✅ Using first password field found');
                } else {
                    throw new Error('Could not find password input field');
                }
            }
            
            // Fill in credentials
            await emailField.fill(this.username);
            console.log('✅ Email entered');
            
            await passwordField.fill(this.password);
            console.log('✅ Password entered');
            
            // Look for submit button with expanded selectors
            const submitSelectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Log In")',
                'button:has-text("Sign In")',
                'button:has-text("Submit")',
                '.login-button',
                '#login-button',
                '.btn-login',
                'input[value*="Login" i]',
                'input[value*="Sign In" i]',
                'form button',
                'form input[type="submit"]'
            ];
            
            let submitButton = null;
            for (const selector of submitSelectors) {
                try {
                    submitButton = this.page.locator(selector).first();
                    if (await submitButton.isVisible({ timeout: 5000 })) {
                        console.log(`✅ Submit button found: ${selector}`);
                        this.mapping.authentication.submit_button = selector;
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (!submitButton) {
                console.log('🔍 Debugging submit button...');
                const allButtons = await this.page.locator('button, input[type="submit"]').all();
                console.log(`Found ${allButtons.length} buttons/submit inputs`);
                
                if (allButtons.length > 0) {
                    // Try to find the most likely submit button
                    for (const button of allButtons) {
                        const text = await button.textContent();
                        const value = await button.getAttribute('value');
                        console.log(`Button text: "${text}", value: "${value}"`);
                        
                        if (text?.toLowerCase().includes('login') || 
                            text?.toLowerCase().includes('sign in') ||
                            value?.toLowerCase().includes('login') ||
                            value?.toLowerCase().includes('sign in')) {
                            submitButton = button;
                            this.mapping.authentication.submit_button = 'button:has-text("' + text + '")';
                            console.log(`✅ Using button with text: "${text}"`);
                            break;
                        }
                    }
                    
                    if (!submitButton) {
                        submitButton = allButtons[0];
                        this.mapping.authentication.submit_button = 'button, input[type="submit"]';
                        console.log('✅ Using first button found');
                    }
                } else {
                    throw new Error('Could not find submit button');
                }
            }
            
            // Submit the form
            await submitButton.click();
            console.log('🚀 Login form submitted');
            
            // Wait for navigation and check for successful login
            await this.page.waitForLoadState('domcontentloaded');
            await this.page.waitForTimeout(5000);
            
            const currentUrl = this.page.url();
            console.log('📍 Post-login URL:', currentUrl);
            
            // Check for successful authentication with expanded indicators
            const authIndicators = [
                'a:has-text("My Account")',
                'a:has-text("Logout")',
                'a:has-text("Log Out")',
                'a:has-text("Sign Out")',
                '.account-menu',
                '.user-menu',
                'a:has-text("Dashboard")',
                'a:has-text("Profile")',
                '.welcome-message',
                '.user-info'
            ];
            
            for (const selector of authIndicators) {
                try {
                    const element = this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 10000 })) {
                        console.log('✅ Authentication successful!');
                        this.isAuthenticated = true;
                        this.mapping.metadata.authenticated = true;
                        this.mapping.authentication.login_url = 'https://www.pictorem.com/myaccount.html';
                        this.mapping.authentication.success_indicator = selector;
                        return;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            // Check if we're still on a login-related page or redirected to account page
            if (currentUrl.includes('account') || currentUrl.includes('dashboard') || currentUrl.includes('profile')) {
                console.log('✅ Authentication appears successful (redirected to account area)');
                this.isAuthenticated = true;
                this.mapping.metadata.authenticated = true;
                this.mapping.authentication.login_url = 'https://www.pictorem.com/myaccount.html';
                this.mapping.authentication.success_indicator = 'url_redirect';
                return;
            }
            
            // If we get here, check for error messages
            const errorSelectors = [
                '.error-msg',
                '.alert-error',
                '.validation-advice',
                '.error-message',
                '.alert',
                '.notification',
                '.message',
                '[class*="error"]',
                '[class*="alert"]'
            ];
            
            for (const selector of errorSelectors) {
                try {
                    const element = this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 5000 })) {
                        const errorText = await element.textContent();
                        throw new Error(`Login failed: ${errorText}`);
                    }
                } catch (e) {
                    // Continue checking other selectors
                }
            }
            
            // If no error found but not authenticated, throw generic error
            throw new Error('Authentication status unclear - please verify credentials and check the browser window');
            
        } catch (error) {
            console.error('❌ Authentication failed:', error.message);
            throw error;
        }
    }

    async mapAuthenticationFlow() {
        console.log('\n🔐 Authentication Flow Already Mapped During Login');
        // Authentication mapping was done during performAuthentication()
        console.log('✅ Authentication flow mapped');
    }

    async mapUploadFlow() {
        console.log('\n📤 Mapping Upload Flow...');
        
        // Navigate to upload page using actual Pictorem URLs
        const uploadPaths = [
            '/order.html?hash=new&create=1&prod=canvas',
            '/order.html',
            '/upload/',
            '/customer/upload/',
            '/create/',
            '/new-order/',
            '/customize/'
        ];
        
        for (const path of uploadPaths) {
            try {
                await this.page.goto(`https://www.pictorem.com${path}`, { 
                    waitUntil: 'domcontentloaded',
                    timeout: 30000 
                });
                await this.page.waitForTimeout(3000);
                
                if (!this.page.url().includes('404') && !this.page.url().includes('error')) {
                    this.mapping.upload_flow.upload_url = this.page.url();
                    console.log(`✅ Upload page found: ${this.page.url()}`);
                    break;
                }
            } catch (e) {
                console.log(`⚠️ Could not access ${path}: ${e.message}`);
                continue;
            }
        }
        
        // Map file upload elements with more specific selectors
        const fileInputSelectors = [
            'input[type="file"]',
            'input[name="file"]',
            'input[name="upload"]',
            'input[name="image"]',
            '[data-testid="file-upload"]',
            '.file-upload',
            '#file-upload',
            '#upload',
            '.dropzone',
            '#dropzone',
            '.upload-area'
        ];
        
        for (const selector of fileInputSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.upload_flow.file_input = selector;
                    console.log(`✅ File input found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Map drag & drop zones
        const dropzoneSelectors = [
            '.dropzone',
            '[data-dropzone]',
            '.drag-drop',
            '#drop-area',
            '.file-drop-zone',
            '.upload-dropzone',
            '[data-upload]'
        ];
        
        for (const selector of dropzoneSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.upload_flow.dropzone = selector;
                    console.log(`✅ Dropzone found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Look for "Start Order" or "Create Order" buttons from the canvas page
        const orderStartSelectors = [
            'a:has-text("Start Order")',
            'button:has-text("Start Order")',
            'a:has-text("Create Order")',
            'button:has-text("Create Order")',
            'a[href*="order.html"]',
            '.start-order',
            '.create-order',
            '#start-order'
        ];
        
        for (const selector of orderStartSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.upload_flow.start_order_button = selector;
                    console.log(`✅ Start order button found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        console.log('✅ Upload flow mapped');
    }

    async mapProductConfiguration() {
        console.log('\n🎨 Mapping Product Configuration...');
        
        // Navigate to the order page to map product configuration
        try {
            await this.page.goto('https://www.pictorem.com/order.html?hash=new&create=1&prod=canvas&width=24&height=16', { 
                waitUntil: 'domcontentloaded',
                timeout: 30000 
            });
            await this.page.waitForTimeout(3000);
            console.log(`✅ Product configuration page accessed: ${this.page.url()}`);
        } catch (e) {
            console.log(`⚠️ Could not access product configuration page: ${e.message}`);
        }
        
        // Map product type selection (canvas, metal, acrylic, etc.)
        const productTypeSelectors = [
            'select[name*="product"]',
            'select[name*="type"]',
            'select[name*="prod"]',
            '.product-type',
            '#product-type',
            '#prod',
            '[data-testid="product-type"]',
            'input[name="product_type"]',
            'input[name="prod"]'
        ];
        
        for (const selector of productTypeSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.product_configuration.product_type_selector = selector;
                    
                    // Get available options if it's a select
                    if (selector.includes('select')) {
                        const options = await element.locator('option').allTextContents();
                        this.mapping.product_configuration.product_types = options.filter(opt => opt.trim());
                    }
                    console.log(`✅ Product type selector found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Map size inputs (width and height)
        const sizeSelectors = {
            width: [
                'input[name="width"]',
                'input[name*="width"]', 
                '#width', 
                '.width-input', 
                'input[id*="width"]',
                'select[name="width"]'
            ],
            height: [
                'input[name="height"]',
                'input[name*="height"]', 
                '#height', 
                '.height-input', 
                'input[id*="height"]',
                'select[name="height"]'
            ],
            size: [
                'select[name*="size"]', 
                '#size-select', 
                '.size-selector',
                'input[name="size"]'
            ]
        };
        
        for (const [type, selectors] of Object.entries(sizeSelectors)) {
            for (const selector of selectors) {
                try {
                    const element = await this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 5000 })) {
                        this.mapping.product_configuration[`${type}_selector`] = selector;
                        console.log(`✅ ${type} selector found: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
        }
        
        // Map canvas type options (from the canvas page info)
        const canvasTypeSelectors = [
            'select[name*="canvas"]',
            'select[name*="finish"]',
            'select[name*="varnish"]',
            '.canvas-type',
            '#canvas-type',
            'input[name*="canvas"][type="radio"]',
            'select[name*="material"]',
            '.finish-option',
            '.varnish-option'
        ];
        
        for (const selector of canvasTypeSelectors) {
            try {
                const elements = await this.page.locator(selector).all();
                if (elements.length > 0) {
                    this.mapping.product_configuration.canvas_type_selector = selector;
                    
                    // If it's a select, get options
                    if (selector.includes('select')) {
                        const options = await this.page.locator(`${selector} option`).allTextContents();
                        this.mapping.product_configuration.canvas_types = options.filter(opt => opt.trim());
                    }
                    console.log(`✅ Canvas type selector found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Map frame options (floating frames mentioned on canvas page)
        const frameSelectors = [
            'select[name*="frame"]',
            'select[name*="floating"]',
            '.frame-option',
            '#frame-type',
            'input[name*="frame"][type="radio"]',
            'select[name*="framing"]',
            '.floating-frame'
        ];
        
        for (const selector of frameSelectors) {
            try {
                const elements = await this.page.locator(selector).all();
                if (elements.length > 0) {
                    this.mapping.product_configuration.frame_selector = selector;
                    console.log(`✅ Frame selector found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Map quantity input
        const quantitySelectors = [
            'input[name="quantity"]',
            'input[name*="quantity"]',
            'input[name="qty"]',
            '#quantity',
            '.quantity-input',
            'select[name*="qty"]',
            'input[name="qty"]'
        ];
        
        for (const selector of quantitySelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.product_configuration.quantity_selector = selector;
                    console.log(`✅ Quantity selector found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        console.log('✅ Product configuration mapped');
    }

    async mapPricingElements() {
        console.log('\n💰 Mapping Pricing Elements...');
        
        const pricingSelectors = [
            '.price',
            '#price',
            '.total',
            '#total',
            '.cost',
            '.amount',
            '[data-testid="price"]',
            '.price-display',
            '.price-value',
            '.product-price'
        ];
        
        for (const selector of pricingSelectors) {
            try {
                const elements = await this.page.locator(selector).all();
                for (let i = 0; i < elements.length; i++) {
                    const element = elements[i];
                    if (await element.isVisible({ timeout: 5000 })) {
                        const text = await element.textContent();
                        if (text && (text.includes('$') || text.includes('USD') || text.match(/\d+\.\d{2}/))) {
                            this.mapping.pricing.price_display = selector;
                            console.log(`✅ Price element found: ${selector} - "${text.trim()}"`);
                            break;
                        }
                    }
                }
                if (this.mapping.pricing.price_display) break;
            } catch (e) {
                continue;
            }
        }
        
        // Map add to cart button
        const cartSelectors = [
            'button:has-text("Add to Cart")',
            'button:has-text("Add to Basket")',
            '.add-to-cart',
            '#add-to-cart',
            '[data-testid="add-to-cart"]',
            'input[value*="Add to Cart"]'
        ];
        
        for (const selector of cartSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.pricing.add_to_cart_button = selector;
                    console.log(`✅ Add to cart button found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        console.log('✅ Pricing elements mapped');
    }

    async mapCheckoutFlow() {
        console.log('\n🛒 Mapping Checkout Flow...');
        
        // Map cart/checkout navigation
        const checkoutSelectors = [
            'a[href*="cart"]',
            'a[href*="checkout"]',
            'button:has-text("Checkout")',
            '.cart-icon',
            '#cart',
            '.checkout-btn',
            '.mini-cart'
        ];
        
        for (const selector of checkoutSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.checkout_flow.checkout_trigger = selector;
                    console.log(`✅ Checkout trigger found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // If we found a checkout trigger, explore the checkout flow
        if (this.mapping.checkout_flow.checkout_trigger) {
            try {
                await this.page.click(this.mapping.checkout_flow.checkout_trigger);
                await this.page.waitForLoadState('domcontentloaded');
                await this.page.waitForTimeout(3000);
                
                this.mapping.checkout_flow.checkout_url = this.page.url();
                console.log(`✅ Checkout page accessed: ${this.page.url()}`);
                
                // Map customer information fields
                const customerFields = await this.mapFormFields([
                    'email', 'customer_email', 'contact_email', 'billing[email]'
                ], [
                    'password'
                ], [
                    'name', 'customer_name', 'full_name', 'first_name', 'last_name', 'billing[firstname]', 'billing[lastname]'
                ]);
                
                this.mapping.checkout_flow.customer_fields = customerFields;
                
                // Map shipping address fields
                const shippingFields = await this.mapFormFields([
                    'email'
                ], [], [
                    'name', 'firstname', 'lastname'
                ], [
                    'address', 'address1', 'street', 'shipping_address', 'billing[street][]'
                ], [
                    'city', 'shipping_city', 'billing[city]'
                ], [
                    'state', 'province', 'region', 'shipping_state', 'billing[region]'
                ], [
                    'country', 'shipping_country', 'billing[country_id]'
                ], [
                    'zip', 'postal_code', 'zipcode', 'postcode', 'billing[postcode]'
                ]);
                
                this.mapping.checkout_flow.shipping_fields = shippingFields;
                
            } catch (e) {
                console.log(`⚠️ Could not explore checkout flow: ${e.message}`);
            }
        }
        
        console.log('✅ Checkout flow mapped');
    }

    async mapPaymentMethods() {
        console.log('\n💳 Mapping Payment Methods...');
        
        // Look for payment method selectors
        const paymentSelectors = [
            'input[name*="payment"]',
            '.payment-method',
            '#payment-method',
            'input[type="radio"][name*="pay"]',
            '.payment-option',
            'select[name*="payment"]'
        ];
        
        for (const selector of paymentSelectors) {
            try {
                const elements = await this.page.locator(selector).all();
                if (elements.length > 0) {
                    this.mapping.payment_methods.payment_selector = selector;
                    
                    // Get payment method values/labels
                    const methods = [];
                    for (const element of elements) {
                        const value = await element.getAttribute('value');
                        const label = await element.locator('+ label, ~ label').textContent();
                        methods.push({ value, label: label?.trim() });
                    }
                    this.mapping.payment_methods.available_methods = methods;
                    console.log(`✅ Payment methods found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        // Map credit card fields
        const cardFields = await this.mapFormFields([
            'email'
        ], [], [], [], [], [], [], [
            'card_number', 'cardnumber', 'cc_number', 'credit_card'
        ], [
            'expiry', 'exp_date', 'expiration', 'exp_month', 'exp_year'
        ], [
            'cvv', 'cvc', 'security_code', 'card_code'
        ], [
            'cardholder', 'card_name', 'cc_name'
        ]);
        
        this.mapping.payment_methods.card_fields = cardFields;
        
        // Map place order button
        const orderButtonSelectors = [
            'button:has-text("Place Order")',
            'button:has-text("Complete Order")',
            'button:has-text("Submit Order")',
            '.place-order',
            '#place-order',
            '[data-testid="place-order"]',
            'input[value*="Place Order"]'
        ];
        
        for (const selector of orderButtonSelectors) {
            try {
                const element = await this.page.locator(selector).first();
                if (await element.isVisible({ timeout: 5000 })) {
                    this.mapping.payment_methods.place_order_button = selector;
                    console.log(`✅ Place order button found: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        console.log('✅ Payment methods mapped');
    }

    async mapFormFields(emailFields = [], passwordFields = [], nameFields = [], addressFields = [], cityFields = [], stateFields = [], countryFields = [], zipFields = [], cardFields = [], expiryFields = [], cvvFields = [], cardNameFields = []) {
        const fields = {};
        const allFields = [
            { type: 'email', selectors: emailFields },
            { type: 'password', selectors: passwordFields },
            { type: 'name', selectors: nameFields },
            { type: 'address', selectors: addressFields },
            { type: 'city', selectors: cityFields },
            { type: 'state', selectors: stateFields },
            { type: 'country', selectors: countryFields },
            { type: 'zip', selectors: zipFields },
            { type: 'card_number', selectors: cardFields },
            { type: 'expiry', selectors: expiryFields },
            { type: 'cvv', selectors: cvvFields },
            { type: 'card_name', selectors: cardNameFields }
        ].filter(field => field.selectors.length > 0);
        
        for (const { type, selectors } of allFields) {
            for (const fieldName of selectors) {
                const fieldSelectors = [
                    `input[name="${fieldName}"]`,
                    `input[name*="${fieldName}"]`,
                    `input[id="${fieldName}"]`,
                    `input[id*="${fieldName}"]`,
                    `select[name="${fieldName}"]`,
                    `select[name*="${fieldName}"]`,
                    `textarea[name="${fieldName}"]`
                ];
                
                for (const selector of fieldSelectors) {
                    try {
                        const element = await this.page.locator(selector).first();
                        if (await element.isVisible({ timeout: 5000 })) {
                            fields[type] = selector;
                            console.log(`✅ ${type} field found: ${selector}`);
                            break;
                        }
                    } catch (e) {
                        continue;
                    }
                }
                if (fields[type]) break;
            }
        }
        
        return fields;
    }

    async mapNavigationPatterns() {
        console.log('\n🧭 Mapping Navigation Patterns...');
        
        // Navigate back to main page to map navigation
        await this.page.goto('https://www.pictorem.com', { 
            waitUntil: 'domcontentloaded',
            timeout: 30000 
        });
        await this.page.waitForTimeout(3000);
        
        // Map common navigation elements based on the actual site structure
        const navElements = {
            home: [
                'a[href="/"]', 
                'a[href="https://www.pictorem.com"]',
                '.home-link', 
                '.logo', 
                'a[href*="pictorem.com"]'
            ],
            upload: [
                'a[href*="upload"]', 
                'a[href*="order.html"]',
                'a[href*="create"]', 
                '.upload-link',
                'a:has-text("UPLOAD FILES")',
                'a:has-text("Start Order")'
            ],
            gallery: [
                'a[href*="gallery"]', 
                'a[href*="products"]', 
                '.gallery-link',
                'a:has-text("ART GALLERY")'
            ],
            account: [
                'a[href*="account"]', 
                'a[href*="profile"]', 
                'a[href*="myaccount"]',
                '.account-link', 
                'a:has-text("My Account")',
                'a:has-text("MY ACCOUNT")'
            ],
            cart: [
                'a[href*="cart"]', 
                '.cart-link', 
                '.cart-icon', 
                '.mini-cart',
                'a:has-text("MY CART")',
                '#cart'
            ],
            orders: [
                'a[href*="orders"]', 
                'a[href*="order-history"]', 
                '.orders-link',
                'a:has-text("TRACK MY ORDER")'
            ],
            canvas: [
                'a[href*="canvas"]',
                'a[href*="canvas-print"]',
                'a:has-text("CANVAS")'
            ],
            formats: [
                'a:has-text("FORMATS & PRICES")',
                'a[href*="format"]'
            ]
        };
        
        for (const [name, selectors] of Object.entries(navElements)) {
            for (const selector of selectors) {
                try {
                    const element = await this.page.locator(selector).first();
                    if (await element.isVisible({ timeout: 5000 })) {
                        this.mapping.navigation[name] = selector;
                        console.log(`✅ ${name} navigation found: ${selector}`);
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
        }
        
        console.log('✅ Navigation patterns mapped');
    }

    async mapErrorPatterns() {
        console.log('\n⚠️ Mapping Error Patterns...');
        
        const errorSelectors = [
            '.error',
            '.alert',
            '.notification',
            '.message',
            '#error-message',
            '.error-text',
            '.validation-error',
            '.field-error',
            '.error-msg',
            '.alert-error',
            '.validation-advice'
        ];
        
        for (const selector of errorSelectors) {
            try {
                const elements = await this.page.locator(selector).all();
                if (elements.length > 0) {
                    // Check if any are visible or commonly used
                    this.mapping.error_patterns[selector] = {
                        selector: selector,
                        count: elements.length,
                        likely_error_container: true
                    };
                    console.log(`✅ Error pattern found: ${selector} (${elements.length} elements)`);
                }
            } catch (e) {
                continue;
            }
        }
        
        console.log('✅ Error patterns mapped');
    }

    async saveMapping() {
        const outputDir = path.join(process.cwd(), '..', 'mcp', 'pictorem-mcp-server', 'mapping');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const outputFile = path.join(outputDir, 'pictorem-site-mapping.json');
        fs.writeFileSync(outputFile, JSON.stringify(this.mapping, null, 2));
        
        console.log(`\n💾 Site mapping saved to: ${outputFile}`);
        
        // Also create a TypeScript interface file
        await this.generateTypeScriptInterfaces(outputDir);
    }

    async generateTypeScriptInterfaces(outputDir) {
        const interfaceContent = `/**
 * Pictorem Site Mapping Interfaces
 * Auto-generated from site mapping on ${this.mapping.metadata.mapped_date}
 * Authenticated mapping: ${this.mapping.metadata.authenticated}
 */

export interface PictoremSiteMapping {
  metadata: {
    mapped_date: string;
    site_url: string;
    mapper_version: string;
    authenticated: boolean;
  };
  authentication: {
    login_url?: string;
    email_field?: string;
    password_field?: string;
    submit_button?: string;
    success_indicator?: string;
  };
  upload_flow: {
    upload_url?: string;
    file_input?: string;
    dropzone?: string;
  };
  product_configuration: {
    product_type_selector?: string;
    product_types?: string[];
    width_selector?: string;
    height_selector?: string;
    size_selector?: string;
    canvas_type_selector?: string;
    canvas_types?: string[];
    frame_selector?: string;
    quantity_selector?: string;
  };
  pricing: {
    price_display?: string;
    add_to_cart_button?: string;
  };
  checkout_flow: {
    checkout_trigger?: string;
    checkout_url?: string;
    customer_fields?: FormFields;
    shipping_fields?: FormFields;
  };
  payment_methods: {
    payment_selector?: string;
    available_methods?: PaymentMethod[];
    card_fields?: FormFields;
    place_order_button?: string;
  };
  navigation: {
    [key: string]: string;
  };
  error_patterns: {
    [selector: string]: {
      selector: string;
      count: number;
      likely_error_container: boolean;
    };
  };
}

export interface FormFields {
  email?: string;
  password?: string;
  name?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  zip?: string;
  card_number?: string;
  expiry?: string;
  cvv?: string;
  card_name?: string;
}

export interface PaymentMethod {
  value?: string;
  label?: string;
}
`;
        
        const interfaceFile = path.join(outputDir, 'pictorem-mapping.types.ts');
        fs.writeFileSync(interfaceFile, interfaceContent);
        
        console.log(`📝 TypeScript interfaces saved to: ${interfaceFile}`);
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async runFullMapping() {
        try {
            await this.promptForCredentials();
            await this.initialize();
            
            console.log('🚀 Starting Authenticated Pictorem Site Mapping...');
            console.log('📋 This will systematically map the entire order flow with authentication\n');
            
            // First authenticate
            await this.performAuthentication();
            
            if (!this.isAuthenticated) {
                throw new Error('Authentication required to continue mapping');
            }
            
            // Now map all the flows
            await this.mapAuthenticationFlow();
            await this.mapUploadFlow();
            await this.mapProductConfiguration();
            await this.mapPricingElements();
            await this.mapCheckoutFlow();
            await this.mapPaymentMethods();
            await this.mapNavigationPatterns();
            await this.mapErrorPatterns();
            
            await this.saveMapping();
            
            console.log('\n🎉 Pictorem site mapping completed successfully!');
            console.log('\n📊 Mapping Summary:');
            console.log(`- Authentication: ${Object.keys(this.mapping.authentication).length} elements`);
            console.log(`- Upload Flow: ${Object.keys(this.mapping.upload_flow).length} elements`);
            console.log(`- Product Config: ${Object.keys(this.mapping.product_configuration).length} elements`);
            console.log(`- Pricing: ${Object.keys(this.mapping.pricing).length} elements`);
            console.log(`- Checkout: ${Object.keys(this.mapping.checkout_flow).length} elements`);
            console.log(`- Payment: ${Object.keys(this.mapping.payment_methods).length} elements`);
            console.log(`- Navigation: ${Object.keys(this.mapping.navigation).length} elements`);
            console.log(`- Error Patterns: ${Object.keys(this.mapping.error_patterns).length} patterns`);
            
            if (this.isAuthenticated) {
                console.log('\n✅ Authenticated mapping complete - all order flow features captured!');
            }
            
        } catch (error) {
            console.error('❌ Mapping failed:', error.message);
            if (error.message.includes('credentials') || error.message.includes('authentication')) {
                console.log('\n💡 Tip: Ensure your Pictorem credentials are correct and your account is active.');
            }
        } finally {
            await this.cleanup();
        }
    }
}

// Run the mapping tool
if (import.meta.url === `file://${process.argv[1]}`) {
    // Check for command line credentials
    const args = process.argv.slice(2);
    const credentials = {};
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--username' || args[i] === '-u') {
            credentials.username = args[i + 1];
        }
        if (args[i] === '--password' || args[i] === '-p') {
            credentials.password = args[i + 1];
        }
    }
    
    const mapper = new PictoremSiteMapper(credentials);
    mapper.runFullMapping();
}

export default PictoremSiteMapper; 