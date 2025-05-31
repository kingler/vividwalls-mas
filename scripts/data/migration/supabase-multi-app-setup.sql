-- Multi-Application Schema Setup for Supabase
-- This script demonstrates how to create separate schemas for different applications

-- ============================================================================
-- SCHEMA-BASED MULTI-APP SETUP (RECOMMENDED APPROACH)
-- ============================================================================

-- Create schemas for different applications
CREATE SCHEMA IF NOT EXISTS app_ecommerce;
CREATE SCHEMA IF NOT EXISTS app_blog;
CREATE SCHEMA IF NOT EXISTS app_crm;
CREATE SCHEMA IF NOT EXISTS app_analytics;

-- Set up Row Level Security (RLS) for each schema
-- Note: RLS policies need to be created per table, not per schema

-- ============================================================================
-- EXAMPLE: E-COMMERCE APPLICATION SCHEMA
-- ============================================================================

-- Create tables in the ecommerce schema
CREATE TABLE app_ecommerce.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE app_ecommerce.products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE app_ecommerce.orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES app_ecommerce.users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EXAMPLE: BLOG APPLICATION SCHEMA
-- ============================================================================

CREATE TABLE app_blog.authors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE app_blog.posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id UUID REFERENCES app_blog.authors(id),
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE app_blog.comments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id UUID REFERENCES app_blog.posts(id),
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EXAMPLE: CRM APPLICATION SCHEMA
-- ============================================================================

CREATE TABLE app_crm.companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE app_crm.contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID REFERENCES app_crm.companies(id),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    position TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- ============================================================================

-- Enable RLS on all tables (example for ecommerce)
ALTER TABLE app_ecommerce.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_ecommerce.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_ecommerce.orders ENABLE ROW LEVEL SECURITY;

-- Create policies (example for user access)
CREATE POLICY "Users can view their own data" ON app_ecommerce.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON app_ecommerce.users
    FOR UPDATE USING (auth.uid() = id);

-- Public read access for products
CREATE POLICY "Anyone can view products" ON app_ecommerce.products
    FOR SELECT USING (true);

-- Users can only see their own orders
CREATE POLICY "Users can view their own orders" ON app_ecommerce.orders
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- API ACCESS CONFIGURATION
-- ============================================================================

-- Grant usage on schemas to anon and authenticated roles
GRANT USAGE ON SCHEMA app_ecommerce TO anon, authenticated;
GRANT USAGE ON SCHEMA app_blog TO anon, authenticated;
GRANT USAGE ON SCHEMA app_crm TO anon, authenticated;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_ecommerce TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA app_blog TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_blog TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_crm TO authenticated;

-- Grant sequence permissions for auto-incrementing IDs
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_ecommerce TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_blog TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_crm TO authenticated;

-- ============================================================================
-- REALTIME SUBSCRIPTIONS (Optional)
-- ============================================================================

-- Enable realtime for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE app_ecommerce.orders;
ALTER PUBLICATION supabase_realtime ADD TABLE app_blog.posts;
ALTER PUBLICATION supabase_realtime ADD TABLE app_crm.contacts;

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

/*
-- From your application, you can now access tables using schema prefixes:

-- JavaScript/TypeScript with Supabase client:
const { data: products } = await supabase
  .from('app_ecommerce.products')
  .select('*');

const { data: posts } = await supabase
  .from('app_blog.posts')
  .select('*');

-- Direct SQL queries:
SELECT * FROM app_ecommerce.products WHERE price < 100;
SELECT * FROM app_blog.posts WHERE published = true;
SELECT * FROM app_crm.contacts WHERE company_id = 'some-uuid';

-- n8n workflow database nodes can connect to specific schemas:
-- Connection string: postgresql://postgres:password@host:5432/postgres?schema=app_ecommerce
*/ 