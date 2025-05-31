#!/bin/bash

# Fix WordPress wp-config.php SSL configuration

ssh -i ~/.ssh/digitalocean root@157.230.13.13 << 'EOF'
cd /home/vivid/vivid_mas

# Create a temporary SSL configuration file
docker exec wordpress-multisite bash -c 'cat > /tmp/ssl-config.php << "PHPEOF"

/* SSL and HTTPS Configuration */
if (isset($_SERVER["HTTP_X_FORWARDED_PROTO"]) && $_SERVER["HTTP_X_FORWARDED_PROTO"] === "https") {
    $_SERVER["HTTPS"] = "on";
}
define("FORCE_SSL_ADMIN", true);

PHPEOF'

# Insert the SSL configuration before wp-settings.php
docker exec wordpress-multisite bash -c '
# Create a new wp-config.php with SSL configuration
cp /var/www/html/wp-config.php /var/www/html/wp-config.php.temp
sed "/require_once ABSPATH.*wp-settings.php/r /tmp/ssl-config.php" /var/www/html/wp-config.php.temp > /var/www/html/wp-config.php.new
mv /var/www/html/wp-config.php.new /var/www/html/wp-config.php
rm /tmp/ssl-config.php
'

echo "✅ WordPress SSL configuration added"

# Restart WordPress container
docker-compose -f wordpress-compose.yml restart wordpress

echo "✅ WordPress restarted"
EOF 