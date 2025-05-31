# Pictorem Site Mapping Guide 🎯

## 🎯 **Objective**

Map the complete end-to-end Pictorem order flow to capture all pages, selectors, form fields, and navigation patterns needed for **production-ready browser automation**. This will replace the placeholder selectors in our MCP server with actual, working selectors from the live Pictorem site.

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd scripts
npm install
npx playwright install chromium
```

### **2. Run the Site Mapper**
```bash
npm run map-pictorem
```

The mapper will:
- ✅ Open Pictorem.com in a visible browser
- ✅ Systematically navigate through all order flow pages
- ✅ Capture selectors for every form field, button, and element
- ✅ Map all product configuration options
- ✅ Document payment methods and checkout flow
- ✅ Generate TypeScript interfaces for type safety

## 📋 **What Gets Mapped**

### **🔐 Authentication Flow**
- Login page URL and navigation
- Email/username input selectors
- Password input selectors
- Submit button selectors
- Post-login navigation patterns

### **📤 Upload Flow**
- Upload page discovery (`/upload`, `/create`, `/customize`)
- File input selectors (`input[type="file"]`)
- Drag & drop zone selectors
- Upload progress indicators
- Upload completion triggers

### **🎨 Product Configuration**
- **Product Types**: Canvas, Framed, Canvas Roll, etc.
- **Size Configuration**: Width/height inputs or preset selectors
- **Canvas Options**: Stretched vs Roll canvas types
- **Frame Options**: Frame type selectors and pricing
- **Quantity Controls**: Quantity input fields
- **Available Options**: All dropdown/radio options captured

### **💰 Pricing Elements**
- Price display selectors (real-time pricing updates)
- Add to cart button selectors
- Price calculation triggers
- Discount application areas

### **🛒 Checkout Flow**
- Cart navigation and access
- Customer information fields:
  - Email address inputs
  - Name fields (first, last, full)
  - Shipping address forms
  - State/province/country selectors
- Shipping options and pricing

### **💳 Payment Methods**
- Payment method selection (radio buttons/dropdowns)
- Credit card form fields:
  - Card number inputs
  - Expiration date fields
  - CVV/Security code inputs
  - Cardholder name fields
- Alternative payment methods (PayPal, etc.)
- Place order button selectors

### **📧 Order Confirmation**
- Order confirmation page patterns
- Order ID extraction selectors
- Success message patterns
- Email confirmation triggers

### **🧭 Navigation Patterns**
- Header navigation elements
- Footer links and patterns
- Breadcrumb navigation
- Account/profile access
- Order history navigation

### **⚠️ Error Patterns**
- Error message containers
- Validation error displays
- Network error patterns
- Form validation feedback

## 🔧 **Output Files**

The mapping tool generates several files in `/mcp/pictorem-mcp-server/mapping/`:

### **1. `pictorem-site-mapping.json`**
Complete mapping data in JSON format:

```json
{
  "metadata": {
    "mapped_date": "2025-01-29T...",
    "site_url": "https://www.pictorem.com",
    "mapper_version": "1.0.0"
  },
  "authentication": {
    "login_trigger": "a[href*='login']",
    "login_url": "https://www.pictorem.com/login",
    "form_fields": {
      "email": "input[name='email']",
      "password": "input[name='password']"
    },
    "submit_button": "button[type='submit']"
  },
  "upload_flow": {
    "upload_url": "https://www.pictorem.com/upload",
    "file_input": "input[type='file']",
    "dropzone": ".dropzone"
  },
  // ... complete mapping data
}
```

### **2. `pictorem-mapping.types.ts`**
TypeScript interfaces for type safety:

```typescript
export interface PictoremSiteMapping {
  metadata: {
    mapped_date: string;
    site_url: string;
    mapper_version: string;
  };
  authentication: {
    login_trigger?: string;
    login_url?: string;
    form_fields?: FormFields;
    submit_button?: string;
  };
  // ... complete interface definitions
}
```

## 🎯 **Mapping Strategy**

### **Step-by-Step Process**
1. **Home Page Analysis**: Start at `pictorem.com` and identify navigation
2. **Authentication Discovery**: Find and map login/signup flows
3. **Upload Flow Mapping**: Locate upload pages and file input methods
4. **Product Configuration**: Map all product customization options
5. **Pricing Integration**: Capture dynamic pricing elements
6. **Checkout Process**: Map customer info and payment flows
7. **Order Completion**: Document confirmation and success patterns
8. **Error Handling**: Identify error message patterns

### **Selector Priority**
1. **Stable IDs**: `#element-id` (highest priority)
2. **Semantic Names**: `input[name="email"]` (preferred)
3. **Data Attributes**: `[data-testid="login"]` (good)
4. **Class Names**: `.login-button` (less stable)
5. **Text Content**: `button:has-text("Login")` (fallback)

## 🔄 **Integration with MCP Server**

After mapping is complete, the results need to be integrated into the Pictorem MCP server:

### **1. Update Browser Manager**
Replace placeholder selectors in `src/index.ts`:

```typescript
// BEFORE (placeholder)
await page.fill('input[name="email"], input[type="email"]', this.username);

// AFTER (mapped)
const mapping = await loadSiteMapping();
await page.fill(mapping.authentication.form_fields.email, this.username);
```

### **2. Configuration Loading**
Add mapping loader to MCP server:

```typescript
import siteMapping from './mapping/pictorem-site-mapping.json';

class PictoremBrowserManager {
  private mapping: PictoremSiteMapping;
  
  constructor() {
    this.mapping = siteMapping;
  }
  
  async authenticateTraditional() {
    await page.fill(this.mapping.authentication.form_fields.email, this.username);
    await page.fill(this.mapping.authentication.form_fields.password, this.password);
    await page.click(this.mapping.authentication.submit_button);
  }
}
```

### **3. Dynamic Selector Updates**
Implement fallback logic for robust automation:

```typescript
async fillField(page: Page, fieldType: string, value: string) {
  const selectors = [
    this.mapping.checkout_flow.customer_fields[fieldType],
    this.mapping.checkout_flow.shipping_fields[fieldType],
    // Fallback selectors
    `input[name*="${fieldType}"]`,
    `input[id*="${fieldType}"]`
  ].filter(Boolean);
  
  for (const selector of selectors) {
    try {
      const element = page.locator(selector).first();
      if (await element.isVisible()) {
        await element.fill(value);
        return true;
      }
    } catch (e) {
      continue;
    }
  }
  
  throw new Error(`Could not find field for ${fieldType}`);
}
```

## 🧪 **Testing the Mapping**

### **1. Validation Script**
Create a validation script to test the mapped selectors:

```bash
npm run validate-mapping
```

### **2. Test Order Flow**
Run a complete test order with the mapped selectors:

```bash
npm run test-automation
```

### **3. Manual Verification**
1. Review the generated `pictorem-site-mapping.json`
2. Verify selectors are specific and stable
3. Check that all required fields are captured
4. Confirm payment and checkout flows are complete

## 📊 **Expected Results**

After successful mapping, you should have:

- ✅ **Complete authentication flow** with working login selectors
- ✅ **Upload process** with file input and drag-drop zones
- ✅ **Product configuration** with all customization options
- ✅ **Pricing elements** for real-time price updates
- ✅ **Checkout flow** with customer and shipping forms  
- ✅ **Payment processing** with credit card and payment method selectors
- ✅ **Order confirmation** with success pattern detection
- ✅ **Error handling** with comprehensive error message selectors

## 🔧 **Next Steps After Mapping**

### **1. Update MCP Server**
- Import the generated mapping data
- Replace all placeholder selectors
- Add mapping validation logic
- Implement fallback selector strategies

### **2. Test Integration**
- Run the updated MCP server
- Test each browser automation tool
- Validate recursive validation works
- Confirm order processing end-to-end

### **3. Production Deployment**
- Deploy updated MCP server to droplet
- Test with live Pictorem orders
- Monitor for selector changes
- Set up mapping refresh schedule

## 🎯 **Key Benefits**

### **Production Reliability**
- **Real selectors** instead of placeholders
- **Tested automation** with actual site structure
- **Comprehensive coverage** of all order scenarios
- **Error handling** for edge cases

### **Maintenance Efficiency**  
- **Systematic mapping** makes updates easier
- **Type-safe interfaces** prevent errors
- **Fallback strategies** handle site changes
- **Automated validation** catches issues early

### **Business Value**
- **Reliable order processing** without manual intervention
- **Reduced errors** from incorrect automation
- **Faster implementation** with mapped selectors
- **Scalable automation** that adapts to site changes

---

## 🚀 **Ready to Map Pictorem!**

Run the site mapper to capture the complete Pictorem order flow and make your browser automation production-ready:

```bash
cd scripts
npm install
npm run map-pictorem
```

**The mapping tool will systematically capture every selector, form field, and navigation pattern needed for bulletproof browser automation!** 🎯✨ 