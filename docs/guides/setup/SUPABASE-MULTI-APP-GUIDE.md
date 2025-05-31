# Supabase Multi-Application Database Guide

Your Supabase instance at `https://supabase.vividwalls.blog` is a **full PostgreSQL database** that can absolutely support multiple applications with different database schemas and collections.

## 🏗️ Current Infrastructure

### Database Access Points
- **Supabase Studio**: https://supabase.vividwalls.blog (Web UI)
- **Direct PostgreSQL**: 157.230.13.13:5432
- **Internal Docker**: supabase-db:5432 (from other containers)

### Current Database Structure
```
postgres (main database)
├── public (default schema)
├── auth (Supabase authentication)
├── storage (file storage)
├── realtime (real-time subscriptions)
├── supabase_functions (edge functions)
├── vault (secrets management)
└── [your custom schemas]
```

## 🎯 Multi-Application Strategies

### Option 1: Schema-Based Separation (Recommended)

**Pros:**
- ✅ Single database connection
- ✅ Shared authentication system
- ✅ Easy cross-app queries
- ✅ Unified backup/restore
- ✅ Better resource utilization

**Implementation:**
```sql
-- Create schemas for different apps
CREATE SCHEMA app_ecommerce;
CREATE SCHEMA app_blog;
CREATE SCHEMA app_crm;

-- Access tables with schema prefix
SELECT * FROM app_ecommerce.products;
SELECT * FROM app_blog.posts;
```

### Option 2: Separate Databases

**Pros:**
- ✅ Complete isolation
- ✅ Independent scaling
- ✅ Separate backups
- ✅ Different access controls

**Cons:**
- ❌ Multiple connections needed
- ❌ No cross-app queries
- ❌ More complex management

## 🚀 Quick Setup Examples

### 1. E-commerce + Blog + CRM (Schema-based)

```sql
-- Run in Supabase Studio SQL Editor
CREATE SCHEMA IF NOT EXISTS app_ecommerce;
CREATE SCHEMA IF NOT EXISTS app_blog;
CREATE SCHEMA IF NOT EXISTS app_crm;

-- E-commerce tables
CREATE TABLE app_ecommerce.products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Blog tables
CREATE TABLE app_blog.posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CRM tables
CREATE TABLE app_crm.contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    company TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Application Access Patterns

#### JavaScript/TypeScript (Supabase Client)
```javascript
// Single client, multiple schemas
const supabase = createClient('https://supabase.vividwalls.blog', 'your-anon-key');

// Access different app data
const { data: products } = await supabase
  .from('app_ecommerce.products')
  .select('*');

const { data: posts } = await supabase
  .from('app_blog.posts')
  .select('*');

const { data: contacts } = await supabase
  .from('app_crm.contacts')
  .select('*');
```

#### n8n Workflows
```javascript
// Database node configuration
// Host: supabase-db (internal) or 157.230.13.13 (external)
// Port: 5432
// Database: postgres
// Schema: app_ecommerce (or app_blog, app_crm)

// Query examples:
SELECT * FROM app_ecommerce.products WHERE price < 100;
SELECT * FROM app_blog.posts WHERE published = true;
INSERT INTO app_crm.contacts (name, email) VALUES ('John Doe', 'john@example.com');
```

#### Direct SQL Access
```bash
# Connect to specific schema
psql postgresql://postgres:password@157.230.13.13:5432/postgres

# Set default schema
SET search_path TO app_ecommerce;
SELECT * FROM products;  -- Now queries app_ecommerce.products

# Or use full schema names
SELECT * FROM app_blog.posts;
SELECT * FROM app_crm.contacts;
```

## 🔐 Security & Access Control

### Row Level Security (RLS)
```sql
-- Enable RLS on tables
ALTER TABLE app_ecommerce.products ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Public can view products" ON app_ecommerce.products
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can manage their orders" ON app_ecommerce.orders
    FOR ALL USING (auth.uid() = user_id);
```

### Schema Permissions
```sql
-- Grant access to specific roles
GRANT USAGE ON SCHEMA app_ecommerce TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_ecommerce TO authenticated;

-- Read-only access for analytics
GRANT USAGE ON SCHEMA app_ecommerce TO analytics_role;
GRANT SELECT ON ALL TABLES IN SCHEMA app_ecommerce TO analytics_role;
```

## 📊 Real-time Subscriptions

```sql
-- Enable realtime for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE app_ecommerce.orders;
ALTER PUBLICATION supabase_realtime ADD TABLE app_blog.posts;
```

```javascript
// Subscribe to changes
const subscription = supabase
  .channel('ecommerce-orders')
  .on('postgres_changes', 
    { event: '*', schema: 'app_ecommerce', table: 'orders' },
    (payload) => console.log('Order changed:', payload)
  )
  .subscribe();
```

## 🔧 Management via Supabase Studio

Access your Supabase Studio at: **https://supabase.vividwalls.blog**

### Available Features:
1. **Table Editor**: Create/edit tables in any schema
2. **SQL Editor**: Run custom queries across all schemas
3. **Authentication**: Manage users across all apps
4. **Storage**: File storage for all applications
5. **Edge Functions**: Serverless functions
6. **Realtime**: Configure real-time subscriptions
7. **API Docs**: Auto-generated API documentation

### Creating Tables via Studio:
1. Go to Table Editor
2. Click "New Table"
3. Set schema to `app_ecommerce` (or your desired schema)
4. Define columns and constraints
5. Enable RLS if needed

## 🔄 Integration with n8n

Your n8n instance can connect to different schemas:

### Database Connection Settings:
- **Host**: `supabase-db` (internal) or `157.230.13.13` (external)
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `[your-postgres-password]`

### Schema-Specific Queries:
```sql
-- E-commerce workflow
SELECT * FROM app_ecommerce.orders WHERE status = 'pending';

-- Blog workflow  
INSERT INTO app_blog.posts (title, content, author_id) 
VALUES ('New Post', 'Content here', 'author-uuid');

-- CRM workflow
UPDATE app_crm.contacts 
SET last_contacted = NOW() 
WHERE email = 'customer@example.com';
```

## 📈 Scaling Considerations

### Current Resources:
- **Memory**: 4.6GB used / 7.8GB total
- **CPU**: 4 vCPU cores
- **Storage**: Sufficient for multiple applications

### Performance Tips:
1. **Indexing**: Create indexes on frequently queried columns
2. **Connection Pooling**: Use pgBouncer (already included)
3. **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
4. **Schema Organization**: Group related tables in same schema

### Monitoring:
```sql
-- Check schema sizes
SELECT schemaname, 
       pg_size_pretty(sum(pg_total_relation_size(schemaname||'.'||tablename))::bigint) as size
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
GROUP BY schemaname;

-- Active connections by database
SELECT datname, count(*) as connections
FROM pg_stat_activity 
GROUP BY datname;
```

## 🎯 Recommended Approach

For most use cases, **Schema-based separation** is recommended because:

1. **Unified Management**: Single Supabase Studio interface
2. **Shared Authentication**: One auth system for all apps
3. **Cross-App Analytics**: Easy to query across applications
4. **Resource Efficiency**: Better utilization of your 8GB RAM
5. **Simplified Backups**: One database to backup/restore

## 🚀 Getting Started

1. **Access Supabase Studio**: https://supabase.vividwalls.blog
2. **Create your first schema**: `CREATE SCHEMA app_yourname;`
3. **Create tables**: Use the Table Editor or SQL Editor
4. **Set up RLS**: Enable row-level security for data protection
5. **Connect from your app**: Use schema-prefixed table names
6. **Integrate with n8n**: Create workflows using schema-specific queries

Your Supabase instance is production-ready and can easily handle multiple applications with proper schema organization! 🎉 