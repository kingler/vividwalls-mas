#!/bin/bash

# Final WordPress URL Fix using WordPress database connection
set -e

SERVER_IP="157.230.13.13"

echo "🔧 Creating WordPress URL fix script using WordPress DB connection..."

# Create the PHP script on the server
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} 'cat > /tmp/wp_fix_urls.php << '"'"'EOF'"'"'
<?php
// Load WordPress
require_once("/var/www/html/wp-config.php");
require_once("/var/www/html/wp-includes/wp-db.php");

// Create database connection using WordPress settings
$wpdb = new wpdb(DB_USER, DB_PASSWORD, DB_NAME, DB_HOST);

echo "Connected to WordPress database: " . DB_NAME . "\n";

// Update URLs
$home_url = "https://vividwalls.blog";
$site_url = "https://vividwalls.blog";

$result1 = $wpdb->update(
    $wpdb->options,
    array("option_value" => $home_url),
    array("option_name" => "home")
);

$result2 = $wpdb->update(
    $wpdb->options,
    array("option_value" => $site_url),
    array("option_name" => "siteurl")
);

if ($result1 !== false && $result2 !== false) {
    echo "✅ URLs updated successfully!\n";
} else {
    echo "❌ Error updating URLs\n";
}

// Verify changes
$results = $wpdb->get_results("SELECT option_name, option_value FROM $wpdb->options WHERE option_name IN ('"'"'home'"'"', '"'"'siteurl'"'"')");
echo "\nCurrent URLs in database:\n";
foreach ($results as $row) {
    echo $row->option_name . ": " . $row->option_value . "\n";
}
?>
EOF'

echo "📤 Copying script to WordPress container..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker cp /tmp/wp_fix_urls.php wordpress-multisite:/tmp/wp_fix_urls.php"

echo "🔄 Running WordPress URL fix..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker exec wordpress-multisite php /tmp/wp_fix_urls.php"

echo "🧹 Cleaning up..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "rm /tmp/wp_fix_urls.php"
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker exec wordpress-multisite rm /tmp/wp_fix_urls.php"

echo "🔄 Restarting WordPress..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml restart wordpress"

echo "⏳ Waiting for restart..."
sleep 15

echo "✅ Testing WordPress site..."
RESULT=$(ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "curl -s -o /dev/null -w '%{http_code}' https://vividwalls.blog")
echo "WordPress status: $RESULT"

if [ "$RESULT" = "200" ]; then
    echo "🎉 SUCCESS! WordPress is now working!"
    echo "🌐 Site: https://vividwalls.blog"
    echo "🔧 Admin: https://vividwalls.blog/wp-admin"
else
    echo "❌ Still redirecting. Let's check the response:"
    ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "curl -I https://vividwalls.blog"
fi

echo "🏁 WordPress URL fix completed!" 