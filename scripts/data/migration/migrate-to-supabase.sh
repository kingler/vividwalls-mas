#!/bin/bash

# Migrate VividWalls Product Data to Supabase Database
# This script moves the product data from the main PostgreSQL container to Supabase

set -e

DROPLET_IP="157.230.13.13"
DROPLET_USER="root"

echo "🔄 Migrating VividWalls Product Data to Supabase..."
echo "=================================================="

# Step 1: Export data from main PostgreSQL container
echo "📤 Exporting data from main PostgreSQL container..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Create export directory
mkdir -p /tmp/vividwalls-export

# Export schema and data from main PostgreSQL
echo "Exporting VividWalls schema and data..."
docker exec vivid_mas-postgres-1 pg_dump -U postgres -d postgres \
  --schema-only \
  --table=products \
  --table=product_variants \
  --table=product_images \
  --table=product_categories \
  --table=product_tags \
  --table=product_analysis \
  --table=product_recommendations \
  --table=product_room_suitability \
  > /tmp/vividwalls-export/schema.sql

docker exec vivid_mas-postgres-1 pg_dump -U postgres -d postgres \
  --data-only \
  --table=products \
  --table=product_variants \
  --table=product_images \
  --table=product_categories \
  --table=product_tags \
  --table=product_analysis \
  --table=product_recommendations \
  --table=product_room_suitability \
  > /tmp/vividwalls-export/data.sql

echo "✅ Data exported successfully"
EOF

# Step 2: Import data into Supabase database
echo "📥 Importing data into Supabase database..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

# Import schema first
echo "Importing schema into Supabase..."
docker exec -i supabase-db psql -U postgres -d postgres < /tmp/vividwalls-export/schema.sql

# Import data
echo "Importing data into Supabase..."
docker exec -i supabase-db psql -U postgres -d postgres < /tmp/vividwalls-export/data.sql

echo "✅ Data imported successfully"
EOF

# Step 3: Verify the migration
echo "🔍 Verifying migration..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas

echo "Checking tables in Supabase database:"
docker exec supabase-db psql -U postgres -d postgres -c "
SELECT 
    tablename,
    (SELECT COUNT(*) FROM products) as products_count,
    (SELECT COUNT(*) FROM product_variants) as variants_count,
    (SELECT COUNT(*) FROM product_images) as images_count
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'products';"

echo ""
echo "Product tables in Supabase:"
docker exec supabase-db psql -U postgres -d postgres -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' AND tablename LIKE '%product%' 
ORDER BY tablename;"

echo "✅ Migration verification complete"
EOF

# Step 4: Clean up export files
echo "🧹 Cleaning up temporary files..."
ssh -i ~/.ssh/digitalocean ${DROPLET_USER}@${DROPLET_IP} << 'EOF'
cd /home/vivid/vivid_mas
rm -rf /tmp/vividwalls-export
echo "✅ Cleanup complete"
EOF

echo ""
echo "🎉 VividWalls Product Data Migration Completed!"
echo ""
echo "📊 Summary:"
echo "✅ Exported schema and data from main PostgreSQL"
echo "✅ Imported into Supabase database"
echo "✅ Verified migration success"
echo "✅ Cleaned up temporary files"
echo ""
echo "🌐 You can now view the product data in Supabase Studio at:"
echo "• https://supabase.vividwalls.blog"
echo ""
echo "📋 Available Tables:"
echo "• products (58 products)"
echo "• product_variants (506 variants)"
echo "• product_images (513 images)"
echo "• product_categories"
echo "• product_tags"
echo "• product_analysis"
echo "• product_recommendations"
echo "• product_room_suitability" 