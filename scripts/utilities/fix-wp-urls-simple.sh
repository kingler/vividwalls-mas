#!/bin/bash

# Simple WordPress URL Fix
set -e

SERVER_IP="157.230.13.13"

echo "🔧 Fixing WordPress URLs with correct database host..."

ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cat > /tmp/fix_urls.php << 'EOF'
<?php
\$mysqli = new mysqli('wordpress-db', 'wordpress', 'wp_secure_pass_518f579bc2f50d8d', 'wordpress');
if (\$mysqli->connect_error) {
    die('Connection failed: ' . \$mysqli->connect_error);
}
echo \"Connected to database successfully\\n\";

\$home_url = 'https://vividwalls.blog';
\$site_url = 'https://vividwalls.blog';

\$stmt1 = \$mysqli->prepare('UPDATE wp_options SET option_value = ? WHERE option_name = ?');
\$home_option = 'home';
\$stmt1->bind_param('ss', \$home_url, \$home_option);
\$result1 = \$stmt1->execute();

\$stmt2 = \$mysqli->prepare('UPDATE wp_options SET option_value = ? WHERE option_name = ?');
\$siteurl_option = 'siteurl';
\$stmt2->bind_param('ss', \$site_url, \$siteurl_option);
\$result2 = \$stmt2->execute();

if (\$result1 && \$result2) {
    echo \"URLs updated successfully!\\n\";
} else {
    echo \"Error updating URLs\\n\";
}

\$result = \$mysqli->query('SELECT option_name, option_value FROM wp_options WHERE option_name IN (\\\"home\\\", \\\"siteurl\\\")');
echo \"Current URLs:\\n\";
while (\$row = \$result->fetch_assoc()) {
    echo \$row['option_name'] . ': ' . \$row['option_value'] . \"\\n\";
}
\$mysqli->close();
?>
EOF"

echo "🔄 Running URL fix script..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker cp /tmp/fix_urls.php wordpress-multisite:/tmp/fix_urls.php"
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker exec wordpress-multisite php /tmp/fix_urls.php"

echo "🧹 Cleaning up..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "rm /tmp/fix_urls.php"
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "docker exec wordpress-multisite rm /tmp/fix_urls.php"

echo "🔄 Restarting WordPress..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "cd /home/vivid/vivid_mas && docker-compose -f wordpress-compose.optimized.yml restart wordpress"

echo "⏳ Waiting for restart..."
sleep 10

echo "✅ Testing WordPress..."
ssh -i ~/.ssh/digitalocean root@${SERVER_IP} "curl -I https://vividwalls.blog"

echo "🏁 Done!" 