-- Multi-Database Setup for Supabase
-- This script demonstrates how to create separate databases for different applications

-- ============================================================================
-- SEPARATE DATABASE APPROACH
-- ============================================================================

-- Create separate databases for different applications
-- Note: You need superuser privileges to create databases

CREATE DATABASE ecommerce_app 
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

CREATE DATABASE blog_app 
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

CREATE DATABASE crm_app 
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- ============================================================================
-- SETUP SUPABASE EXTENSIONS IN EACH DATABASE
-- ============================================================================

-- Connect to ecommerce_app database and set up Supabase
\c ecommerce_app;

-- Create necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgjwt";

-- Create auth schema and basic setup
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- Repeat for blog_app
\c blog_app;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgjwt";
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- Repeat for crm_app
\c crm_app;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgjwt";
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- ============================================================================
-- CONNECTION EXAMPLES
-- ============================================================================

/*
Different applications can connect to their specific databases:

E-commerce App:
postgresql://postgres:password@157.230.13.13:5432/ecommerce_app

Blog App:
postgresql://postgres:password@157.230.13.13:5432/blog_app

CRM App:
postgresql://postgres:password@157.230.13.13:5432/crm_app

Supabase Client Configuration:
const supabaseEcommerce = createClient(
  'https://supabase.vividwalls.blog',
  'your-anon-key',
  {
    db: { schema: 'public' },
    global: { headers: { 'X-Database': 'ecommerce_app' } }
  }
);

n8n Database Connections:
- Ecommerce: postgresql://postgres:password@supabase-db:5432/ecommerce_app
- Blog: postgresql://postgres:password@supabase-db:5432/blog_app
- CRM: postgresql://postgres:password@supabase-db:5432/crm_app
*/ 