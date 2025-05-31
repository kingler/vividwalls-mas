#!/bin/bash

# Fix WordPress URLs in Database
# This script updates the WordPress database to use the correct HTTPS URLs

set -e

SERVER_IP="157.230.13.13"

echo "🔧 Fixing WordPress URLs in database..."

# Function to run commands on remote server
run_remote() {
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "$1"
}

echo "📝 Creating WordPress URL fix script..."

# Create a PHP script to fix WordPress URLs
cat > /tmp/fix_wp_urls.php << 'EOF'
<?php
// WordPress URL Fix Script
define('DB_NAME', 'wordpress');
define('DB_USER', 'wordpress');
define('DB_PASSWORD', 'wp_secure_pass_518f579bc2f50d8d');
define('DB_HOST', 'wordpress-mysql');

$mysqli = new mysqli(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME);

if ($mysqli->connect_error) {
    die('Connection failed: ' . $mysqli->connect_error);
}

echo "Connected to database successfully\n";

// Update home URL
$home_url = 'https://vividwalls.blog';
$site_url = 'https://vividwalls.blog';

$stmt1 = $mysqli->prepare("UPDATE wp_options SET option_value = ? WHERE option_name = 'home'");
$stmt1->bind_param("s", $home_url);
$result1 = $stmt1->execute();

$stmt2 = $mysqli->prepare("UPDATE wp_options SET option_value = ? WHERE option_name = 'siteurl'");
$stmt2->bind_param("s", $site_url);
$result2 = $stmt2->execute();

if ($result1 && $result2) {
    echo "✅ WordPress URLs updated successfully!\n";
    echo "Home URL: $home_url\n";
    echo "Site URL: $site_url\n";
} else {
    echo "❌ Error updating URLs\n";
}

// Verify the changes
$result = $mysqli->query("SELECT option_name, option_value FROM wp_options WHERE option_name IN ('home', 'siteurl')");
echo "\nCurrent URLs in database:\n";
while ($row = $result->fetch_assoc()) {
    echo $row['option_name'] . ": " . $row['option_value'] . "\n";
}

$mysqli->close();
?>
EOF

echo "📤 Uploading PHP script to WordPress container..."
run_remote "docker cp /dev/stdin wordpress-multisite:/tmp/fix_wp_urls.php" < /tmp/fix_wp_urls.php

echo "🔄 Running URL fix script..."
run_remote "docker exec wordpress-multisite php /tmp/fix_wp_urls.php"

echo "🧹 Cleaning up..."
run_remote "docker exec wordpress-multisite rm /tmp/fix_wp_urls.php"

echo "🔄 Restarting WordPress to apply changes..."
run_remote "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml restart wordpress"

echo "⏳ Waiting for WordPress to restart..."
sleep 10

echo "✅ Testing WordPress site..."
WP_STATUS=$(run_remote "curl -s -o /dev/null -w '%{http_code}' https://vividwalls.blog")
echo "WordPress HTTPS status: $WP_STATUS"

if [ "$WP_STATUS" = "200" ]; then
    echo "🎉 WordPress is now working correctly!"
    echo "🌐 Site: https://vividwalls.blog"
    echo "🔧 Admin: https://vividwalls.blog/wp-admin"
else
    echo "❌ Still having issues. Let's check what's happening..."
    run_remote "curl -I https://vividwalls.blog"
fi

echo "🏁 WordPress URL fix completed" 