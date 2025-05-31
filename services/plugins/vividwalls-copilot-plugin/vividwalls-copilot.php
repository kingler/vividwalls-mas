<?php
/**
 * Plugin Name: VividWalls AI Sales Agent
 * Plugin URI: https://vividwalls.co
 * Description: AI-powered sales agent with image analysis and art recommendations for VividWalls
 * Version: 1.0.0
 * Author: VividWalls
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('VIVIDWALLS_COPILOT_VERSION', '1.0.0');
define('VIVIDWALLS_COPILOT_PLUGIN_URL', plugin_dir_url(__FILE__));
define('VIVIDWALLS_COPILOT_PLUGIN_PATH', plugin_dir_path(__FILE__));

class VividWallsCopilot {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'render_copilot_interface'));
        add_action('wp_ajax_vividwalls_copilot', array($this, 'handle_ajax_request'));
        add_action('wp_ajax_nopriv_vividwalls_copilot', array($this, 'handle_ajax_request'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_shortcode('vividwalls_copilot', array($this, 'copilot_shortcode'));
        
        // Include recommendations page functionality
        require_once VIVIDWALLS_COPILOT_PLUGIN_PATH . 'vividwalls-recommendations-page.php';
    }
    
    public function init() {
        // Plugin initialization
    }
    
    public function enqueue_scripts() {
        // Only load on frontend
        if (!is_admin()) {
            wp_enqueue_script(
                'vividwalls-copilot-js',
                VIVIDWALLS_COPILOT_PLUGIN_URL . 'assets/vividwalls-copilot-enhanced.js',
                array('jquery'),
                VIVIDWALLS_COPILOT_VERSION,
                true
            );
            
            wp_enqueue_style(
                'vividwalls-copilot-css',
                VIVIDWALLS_COPILOT_PLUGIN_URL . 'assets/vividwalls-copilot.css',
                array(),
                VIVIDWALLS_COPILOT_VERSION
            );
            
            // Localize script with AJAX URL and nonce
            wp_localize_script('vividwalls-copilot-js', 'vividwalls_ajax', array(
                'ajax_url' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('vividwalls_copilot_nonce'),
                'n8n_webhook' => get_option('vividwalls_n8n_webhook', 'http://157.230.13.13:5678/webhook/vividwalls-chat'),
                'api_settings' => array(
                    'enabled' => get_option('vividwalls_copilot_enabled', '1'),
                    'position' => get_option('vividwalls_copilot_position', 'bottom-right'),
                    'theme' => get_option('vividwalls_copilot_theme', 'default'),
                    'auto_open' => get_option('vividwalls_copilot_auto_open', '0'),
                )
            ));
        }
    }
    
    public function render_copilot_interface() {
        if (get_option('vividwalls_copilot_enabled', '1') == '1') {
            $position = get_option('vividwalls_copilot_position', 'bottom-right');
            $theme = get_option('vividwalls_copilot_theme', 'default');
            
            echo '<div id="vividwalls-copilot-container" class="position-' . esc_attr($position) . ' theme-' . esc_attr($theme) . '">';
            echo '<div id="vividwalls-copilot-button">';
            echo '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">';
            echo '<path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9Z" fill="currentColor"/>';
            echo '</svg>';
            echo '</div>';
            echo '<div id="vividwalls-copilot-chat" style="display: none;">';
            echo '<div id="vividwalls-copilot-header">';
            echo '<h3>VividWalls Art Advisor</h3>';
            echo '<button id="vividwalls-copilot-close">×</button>';
            echo '</div>';
            echo '<div id="vividwalls-copilot-messages"></div>';
            echo '<div id="vividwalls-copilot-input-area">';
            echo '<input type="file" id="vividwalls-room-image" accept="image/*" style="display: none;">';
            echo '<button id="vividwalls-upload-button">📷 Upload Room</button>';
            echo '<input type="text" id="vividwalls-copilot-input" placeholder="Ask about art or upload a room photo...">';
            echo '<button id="vividwalls-copilot-send">Send</button>';
            echo '</div>';
            echo '</div>';
            echo '</div>';
        }
    }
    
    public function handle_ajax_request() {
        // Verify nonce
        if (!wp_verify_nonce($_POST['nonce'], 'vividwalls_copilot_nonce')) {
            wp_die('Security check failed');
        }
        
        $action_type = sanitize_text_field($_POST['action_type']);
        $message = sanitize_textarea_field($_POST['message']);
        
        switch ($action_type) {
            case 'chat_message':
                $this->process_chat_message($message);
                break;
            case 'image_analysis':
                $this->process_image_analysis();
                break;
            case 'product_recommendation':
                $this->get_product_recommendations($_POST['criteria']);
                break;
            default:
                wp_send_json_error('Invalid action type');
        }
    }
    
    private function process_chat_message($message) {
        // Integration with n8n webhook
        $n8n_webhook = get_option('vividwalls_n8n_webhook', '');
        
        if (!empty($n8n_webhook)) {
            $payload = array(
                'message' => $message,
                'user_id' => get_current_user_id(),
                'session_id' => session_id(),
                'page_url' => $_POST['page_url'],
                'timestamp' => current_time('mysql'),
                'source' => 'wordpress_copilot'
            );
            
            $response = wp_remote_post($n8n_webhook, array(
                'method' => 'POST',
                'body' => json_encode($payload),
                'headers' => array(
                    'Content-Type' => 'application/json',
                ),
                'timeout' => 45
            ));
            
            if (is_wp_error($response)) {
                wp_send_json_error('Failed to connect to AI service');
            } else {
                $body = wp_remote_retrieve_body($response);
                $data = json_decode($body, true);
                wp_send_json_success($data);
            }
        } else {
            wp_send_json_error('AI service not configured');
        }
    }
    
    private function process_image_analysis() {
        if (!isset($_FILES['room_image'])) {
            wp_send_json_error('No image uploaded');
        }
        
        // Handle file upload
        $uploaded_file = $_FILES['room_image'];
        $upload_dir = wp_upload_dir();
        
        // Validate image
        $allowed_types = array('image/jpeg', 'image/png', 'image/gif');
        if (!in_array($uploaded_file['type'], $allowed_types)) {
            wp_send_json_error('Invalid file type');
        }
        
        // Save image temporarily
        $filename = uniqid('room_') . '.' . pathinfo($uploaded_file['name'], PATHINFO_EXTENSION);
        $filepath = $upload_dir['path'] . '/' . $filename;
        
        if (move_uploaded_file($uploaded_file['tmp_name'], $filepath)) {
            // Send to n8n for image analysis
            $n8n_webhook = get_option('vividwalls_n8n_image_webhook', '');
            
            $payload = array(
                'image_url' => $upload_dir['url'] . '/' . $filename,
                'analysis_type' => 'room_analysis',
                'user_id' => get_current_user_id(),
                'timestamp' => current_time('mysql')
            );
            
            $response = wp_remote_post($n8n_webhook, array(
                'method' => 'POST',
                'body' => json_encode($payload),
                'headers' => array('Content-Type' => 'application/json'),
                'timeout' => 60
            ));
            
            if (!is_wp_error($response)) {
                $body = wp_remote_retrieve_body($response);
                $data = json_decode($body, true);
                
                // Clean up temporary file
                unlink($filepath);
                
                wp_send_json_success($data);
            } else {
                wp_send_json_error('Image analysis failed');
            }
        } else {
            wp_send_json_error('Failed to upload image');
        }
    }
    
    private function get_product_recommendations($criteria) {
        // Integration with Shopify MCP or WooCommerce
        $recommendations = array();
        
        // This would integrate with your Shopify MCP server
        // For now, returning mock data structure
        $recommendations = array(
            'products' => array(),
            'collections' => array(),
            'artists' => array()
        );
        
        wp_send_json_success($recommendations);
    }
    
    public function add_admin_menu() {
        add_options_page(
            'VividWalls Copilot Settings',
            'VividWalls AI',
            'manage_options',
            'vividwalls-copilot',
            array($this, 'admin_page')
        );
    }
    
    public function admin_page() {
        if (isset($_POST['save_settings'])) {
            update_option('vividwalls_copilot_enabled', sanitize_text_field($_POST['enabled']));
            update_option('vividwalls_copilot_position', sanitize_text_field($_POST['position']));
            update_option('vividwalls_copilot_theme', sanitize_text_field($_POST['theme']));
            update_option('vividwalls_n8n_webhook', sanitize_url($_POST['n8n_webhook']));
            update_option('vividwalls_n8n_image_webhook', sanitize_url($_POST['n8n_image_webhook']));
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        
        $enabled = get_option('vividwalls_copilot_enabled', '1');
        $position = get_option('vividwalls_copilot_position', 'bottom-right');
        $theme = get_option('vividwalls_copilot_theme', 'default');
        $n8n_webhook = get_option('vividwalls_n8n_webhook', '');
        $n8n_image_webhook = get_option('vividwalls_n8n_image_webhook', '');
        ?>
        <div class="wrap">
            <h1>VividWalls AI Sales Agent Settings</h1>
            <form method="post" action="">
                <table class="form-table">
                    <tr>
                        <th scope="row">Enable Copilot</th>
                        <td>
                            <input type="checkbox" name="enabled" value="1" <?php checked($enabled, '1'); ?>>
                            <label>Enable the AI sales agent on your site</label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Position</th>
                        <td>
                            <select name="position">
                                <option value="bottom-right" <?php selected($position, 'bottom-right'); ?>>Bottom Right</option>
                                <option value="bottom-left" <?php selected($position, 'bottom-left'); ?>>Bottom Left</option>
                                <option value="top-right" <?php selected($position, 'top-right'); ?>>Top Right</option>
                                <option value="top-left" <?php selected($position, 'top-left'); ?>>Top Left</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">Theme</th>
                        <td>
                            <select name="theme">
                                <option value="default" <?php selected($theme, 'default'); ?>>Default</option>
                                <option value="dark" <?php selected($theme, 'dark'); ?>>Dark</option>
                                <option value="minimal" <?php selected($theme, 'minimal'); ?>>Minimal</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">n8n Chat Webhook</th>
                        <td>
                            <input type="url" name="n8n_webhook" value="<?php echo esc_attr($n8n_webhook); ?>" class="regular-text">
                            <p class="description">URL for n8n chat processing webhook</p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">n8n Image Analysis Webhook</th>
                        <td>
                            <input type="url" name="n8n_image_webhook" value="<?php echo esc_attr($n8n_image_webhook); ?>" class="regular-text">
                            <p class="description">URL for n8n image analysis webhook</p>
                        </td>
                    </tr>
                </table>
                <?php submit_button('Save Settings', 'primary', 'save_settings'); ?>
            </form>
            
            <h2>Integration Status</h2>
            <table class="widefat">
                <tr>
                    <th>Component</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>JavaScript Files</td>
                    <td><?php echo file_exists(VIVIDWALLS_COPILOT_PLUGIN_PATH . 'assets/vividwalls-copilot-enhanced.js') ? '✅ Loaded' : '❌ Missing'; ?></td>
                </tr>
                <tr>
                    <td>CSS Styles</td>
                    <td><?php echo file_exists(VIVIDWALLS_COPILOT_PLUGIN_PATH . 'assets/vividwalls-copilot.css') ? '✅ Loaded' : '❌ Missing'; ?></td>
                </tr>
                <tr>
                    <td>n8n Connection</td>
                    <td><?php echo !empty($n8n_webhook) ? '✅ Configured' : '⚠️ Not configured'; ?></td>
                </tr>
            </table>
            
            <h2>Shortcode Usage</h2>
            <p>You can also embed the copilot on specific pages using the shortcode:</p>
            <code>[vividwalls_copilot position="inline" theme="minimal"]</code>
        </div>
        <?php
    }
    
    public function copilot_shortcode($atts) {
        $atts = shortcode_atts(array(
            'position' => 'inline',
            'theme' => 'default',
            'auto_open' => 'false'
        ), $atts);
        
        ob_start();
        echo '<div class="vividwalls-copilot-shortcode position-' . esc_attr($atts['position']) . ' theme-' . esc_attr($atts['theme']) . '">';
        echo '<div id="vividwalls-copilot-inline">';
        echo '<h3>Ask our AI Art Advisor</h3>';
        echo '<div id="vividwalls-copilot-messages-inline"></div>';
        echo '<div id="vividwalls-copilot-input-area-inline">';
        echo '<input type="file" id="vividwalls-room-image-inline" accept="image/*" style="display: none;">';
        echo '<button id="vividwalls-upload-button-inline">📷 Upload Room Photo</button>';
        echo '<input type="text" id="vividwalls-copilot-input-inline" placeholder="Describe your style or ask about our art...">';
        echo '<button id="vividwalls-copilot-send-inline">Get Recommendations</button>';
        echo '</div>';
        echo '</div>';
        echo '</div>';
        
        return ob_get_clean();
    }
}

// Initialize the plugin
new VividWallsCopilot();

// Activation hook
register_activation_hook(__FILE__, 'vividwalls_copilot_activate');
function vividwalls_copilot_activate() {
    // Set default options
    add_option('vividwalls_copilot_enabled', '1');
    add_option('vividwalls_copilot_position', 'bottom-right');
    add_option('vividwalls_copilot_theme', 'default');
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'vividwalls_copilot_deactivate');
function vividwalls_copilot_deactivate() {
    // Clean up if needed
}
?>