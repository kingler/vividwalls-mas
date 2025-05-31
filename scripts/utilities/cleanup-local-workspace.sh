#!/bin/bash

# VividWalls Local Workspace Cleanup Script
# This script organizes backup files and removes temporary files

echo "🧹 Starting VividWalls workspace cleanup..."

# Create backup archive directory if it doesn't exist
mkdir -p archive/backups

echo "📁 Archiving backup files..."

# Move backup files to archive directory
find . -maxdepth 1 -name "*.backup*" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "*.bak*" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "Caddyfile.*" ! -name "Caddyfile" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "docker-compose.*.yml" ! -name "docker-compose.yml" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "wordpress-*" -exec mv {} archive/backups/ \; 2>/dev/null

# Move environment backup files
find . -maxdepth 1 -name ".env.backup*" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "env.*" ! -name "env.example" -exec mv {} archive/backups/ \; 2>/dev/null
find . -maxdepth 1 -name "supabase-env-fix.env" -exec mv {} archive/backups/ \; 2>/dev/null

echo "🗑️  Removing temporary files..."

# Remove definitely temporary files
rm -f chatbot.html 2>/dev/null
rm -f deploy-*.sh 2>/dev/null
rm -f start_services.py 2>/dev/null
rm -f .DS_Store 2>/dev/null

echo "📋 Organizing documentation..."

# Create docs directory if it doesn't exist  
mkdir -p docs

# Move documentation files to docs directory (except core ones)
find . -maxdepth 1 -name "*GUIDE*.md" -exec mv {} docs/ \; 2>/dev/null
find . -maxdepth 1 -name "*SETUP*.md" -exec mv {} docs/ \; 2>/dev/null
find . -maxdepth 1 -name "*DEPLOYMENT*.md" -exec mv {} docs/ \; 2>/dev/null
find . -maxdepth 1 -name "*OPTIMIZATION*.md" -exec mv {} docs/ \; 2>/dev/null

# Keep core project documentation in root
# README.md, LICENSE, CLAUDE.md, PROJECT_STATUS_SUMMARY.md etc.

echo "🔄 Updating .gitignore..."

# Add archive directory to .gitignore if not already there
if ! grep -q "archive/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Archived backup files" >> .gitignore
    echo "archive/backups/" >> .gitignore
fi

# Add common backup patterns
if ! grep -q "*.backup" .gitignore 2>/dev/null; then
    echo "*.backup*" >> .gitignore
    echo "*.bak*" >> .gitignore
    echo ".env.backup*" >> .gitignore
    echo "Caddyfile.*" >> .gitignore
    echo "!Caddyfile" >> .gitignore
    echo "docker-compose.*.yml" >> .gitignore
    echo "!docker-compose.yml" >> .gitignore
fi

echo "✅ Cleanup completed!"
echo ""
echo "📊 Summary:"
echo "  📁 Backup files moved to: archive/backups/"
echo "  📚 Documentation organized in: docs/"
echo "  🗑️  Temporary files removed"
echo "  🔒 .gitignore updated"
echo ""
echo "🎯 Current workspace structure:"
echo "├── docs/              # Documentation files"
echo "├── archive/backups/   # Archived backup files"
echo "├── n8n/workflows/     # VividWalls workflows"
echo "├── scripts/           # Deployment scripts"
echo "├── assets/            # Frontend resources"
echo "├── tasks/             # Task management"
echo "└── [core files]       # README, package.json, etc."
echo ""
echo "🚀 Workspace is now organized and ready for development!" 