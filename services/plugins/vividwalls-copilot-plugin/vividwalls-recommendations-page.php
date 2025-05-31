<?php
/**
 * VividWalls AI Recommendations Page Template
 * Standalone page for art recommendations with masonry grid layout
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class VividWallsRecommendationsPage {
    
    public function __construct() {
        add_action('init', array($this, 'add_rewrite_rules'));
        add_action('template_redirect', array($this, 'handle_recommendations_page'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_recommendation_assets'));
        add_action('wp_ajax_get_ai_recommendations', array($this, 'get_ai_recommendations'));
        add_action('wp_ajax_nopriv_get_ai_recommendations', array($this, 'get_ai_recommendations'));
        add_action('wp_ajax_save_user_preferences', array($this, 'save_user_preferences'));
        add_action('wp_ajax_nopriv_save_user_preferences', array($this, 'save_user_preferences'));
    }
    
    public function add_rewrite_rules() {
        add_rewrite_rule(
            '^art-recommendations/?$',
            'index.php?vividwalls_recommendations=1',
            'top'
        );
        add_rewrite_tag('%vividwalls_recommendations%', '1');
    }
    
    public function handle_recommendations_page() {
        global $wp_query;
        
        if (get_query_var('vividwalls_recommendations')) {
            $this->render_recommendations_page();
            exit;
        }
    }
    
    public function enqueue_recommendation_assets() {
        if (get_query_var('vividwalls_recommendations')) {
            wp_enqueue_style(
                'vividwalls-recommendations',
                VIVIDWALLS_COPILOT_PLUGIN_URL . 'assets/vividwalls-recommendations.css',
                array(),
                VIVIDWALLS_COPILOT_VERSION
            );
            
            wp_enqueue_script(
                'vividwalls-recommendations-js',
                VIVIDWALLS_COPILOT_PLUGIN_URL . 'assets/vividwalls-recommendations.js',
                array('jquery', 'masonry'),
                VIVIDWALLS_COPILOT_VERSION,
                true
            );
            
            wp_localize_script('vividwalls-recommendations-js', 'vividwalls_recs', array(
                'ajax_url' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('vividwalls_recommendations_nonce'),
                'n8n_webhook' => get_option('vividwalls_n8n_webhook', 'http://157.230.13.13:5678/webhook/vividwalls-chat'),
                'collection_api' => 'https://api.vividwalls.co/collections',
                'user_id' => get_current_user_id(),
                'session_id' => session_id()
            ));
        }
    }
    
    public function render_recommendations_page() {
        get_header();
        ?>
        <div id="vividwalls-recommendations-app">
            <!-- Page Header -->
            <section class="recommendations-hero">
                <div class="hero-content">
                    <h1 class="hero-title">
                        <span class="gradient-text">Discover Your Perfect Art</span>
                    </h1>
                    <p class="hero-subtitle">
                        Let our AI help you find the perfect pieces for your space using advanced color psychology and style analysis
                    </p>
                </div>
                <div class="hero-visual">
                    <div class="floating-artwork-preview">
                        <img src="<?php echo VIVIDWALLS_COPILOT_PLUGIN_URL; ?>assets/images/hero-art-preview.jpg" alt="Art Preview" />
                    </div>
                </div>
            </section>

            <!-- AI Recommendation Interface -->
            <section class="ai-interface-section">
                <div class="container">
                    <div class="ai-interface-card">
                        <div class="interface-header">
                            <div class="ai-avatar">
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2L15.09 8.26L22 9L17 14L18.18 21L12 17.77L5.82 21L7 14L2 9L8.91 8.26L12 2Z" fill="currentColor"/>
                                </svg>
                            </div>
                            <div class="interface-title">
                                <h2>VividWalls AI Art Curator</h2>
                                <p>Upload a room photo or describe your style preferences</p>
                            </div>
                        </div>

                        <!-- Image Upload Section -->
                        <div class="upload-section" id="upload-section">
                            <div class="upload-area" id="upload-area">
                                <div class="upload-content">
                                    <div class="upload-icon">
                                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="currentColor"/>
                                        </svg>
                                    </div>
                                    <h3>Upload Your Room Photo</h3>
                                    <p>Drag and drop or click to upload a photo of your space</p>
                                    <button class="upload-btn" id="upload-btn">Choose Photo</button>
                                    <input type="file" id="room-image-input" accept="image/*" style="display: none;">
                                </div>
                            </div>
                            
                            <!-- Image Preview -->
                            <div class="image-preview-container" id="image-preview" style="display: none;">
                                <div class="preview-image-wrapper">
                                    <img id="preview-image" src="" alt="Room preview">
                                    <div class="analysis-overlay" id="analysis-overlay">
                                        <div class="color-analysis" id="color-analysis"></div>
                                        <div class="style-tags" id="style-tags"></div>
                                    </div>
                                </div>
                                <div class="preview-actions">
                                    <button class="btn btn-secondary" id="change-image">Change Image</button>
                                    <button class="btn btn-primary" id="analyze-image">Analyze & Get Recommendations</button>
                                </div>
                            </div>
                        </div>

                        <!-- Text Input Alternative -->
                        <div class="divider">
                            <span>OR</span>
                        </div>

                        <div class="text-input-section">
                            <div class="input-group">
                                <label for="style-description">Describe Your Style Preferences</label>
                                <textarea 
                                    id="style-description" 
                                    placeholder="Tell us about your style preferences, room type, color preferences, or any specific requirements..."
                                    rows="4"
                                ></textarea>
                            </div>
                            
                            <!-- Quick Style Filters -->
                            <div class="style-filters">
                                <h4>Quick Style Filters</h4>
                                <div class="filter-grid">
                                    <button class="filter-tag" data-style="modern">Modern</button>
                                    <button class="filter-tag" data-style="contemporary">Contemporary</button>
                                    <button class="filter-tag" data-style="minimalist">Minimalist</button>
                                    <button class="filter-tag" data-style="abstract">Abstract</button>
                                    <button class="filter-tag" data-style="landscape">Landscape</button>
                                    <button class="filter-tag" data-style="portrait">Portrait</button>
                                    <button class="filter-tag" data-style="colorful">Colorful</button>
                                    <button class="filter-tag" data-style="monochrome">Black & White</button>
                                </div>
                            </div>

                            <button class="btn btn-primary btn-large" id="get-recommendations">
                                Get AI Recommendations
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Recommendations Display -->
            <section class="recommendations-section" id="recommendations-section" style="display: none;">
                <div class="container">
                    <div class="section-header">
                        <h2>Perfect Matches for Your Space</h2>
                        <p>Our AI has curated these artworks specifically for you</p>
                    </div>

                    <!-- Filter and Sort Controls -->
                    <div class="recommendations-controls">
                        <div class="filter-controls">
                            <select id="price-filter">
                                <option value="">All Prices</option>
                                <option value="0-500">Under $500</option>
                                <option value="500-1000">$500 - $1,000</option>
                                <option value="1000-2000">$1,000 - $2,000</option>
                                <option value="2000+">$2,000+</option>
                            </select>
                            
                            <select id="size-filter">
                                <option value="">All Sizes</option>
                                <option value="small">Small (under 16")</option>
                                <option value="medium">Medium (16" - 24")</option>
                                <option value="large">Large (24" - 36")</option>
                                <option value="xl">Extra Large (36"+)</option>
                            </select>
                            
                            <select id="style-filter">
                                <option value="">All Styles</option>
                                <option value="abstract">Abstract</option>
                                <option value="landscape">Landscape</option>
                                <option value="portrait">Portrait</option>
                                <option value="modern">Modern</option>
                                <option value="contemporary">Contemporary</option>
                            </select>
                        </div>
                        
                        <div class="sort-controls">
                            <select id="sort-options">
                                <option value="relevance">Best Match</option>
                                <option value="price-low">Price: Low to High</option>
                                <option value="price-high">Price: High to Low</option>
                                <option value="size">Size</option>
                                <option value="newest">Newest First</option>
                            </select>
                        </div>
                    </div>

                    <!-- Masonry Grid for Recommendations -->
                    <div class="recommendations-grid" id="recommendations-grid">
                        <!-- Dynamic content loaded here -->
                    </div>

                    <!-- Load More Button -->
                    <div class="load-more-section">
                        <button class="btn btn-outline btn-large" id="load-more-btn">
                            Load More Recommendations
                        </button>
                    </div>
                </div>
            </section>

            <!-- AI Analysis Explanation -->
            <section class="analysis-explanation" id="analysis-explanation" style="display: none;">
                <div class="container">
                    <div class="explanation-content">
                        <h3>How Our AI Made These Recommendations</h3>
                        <div class="analysis-breakdown" id="analysis-breakdown">
                            <!-- Dynamic analysis content -->
                        </div>
                    </div>
                </div>
            </section>

            <!-- Loading States -->
            <div class="loading-overlay" id="loading-overlay" style="display: none;">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <h3>Analyzing Your Space...</h3>
                    <p id="loading-message">Our AI is examining your room and finding perfect art matches</p>
                    <div class="loading-progress">
                        <div class="progress-bar" id="progress-bar"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recommendation Card Template -->
        <script type="text/template" id="recommendation-card-template">
            <div class="recommendation-card" data-artwork-id="{{id}}" data-price="{{price}}" data-size="{{size}}" data-style="{{style}}">
                <div class="card-image-wrapper">
                    <img src="{{image_url}}" alt="{{title}}" loading="lazy">
                    <div class="image-overlay">
                        <button class="quick-view-btn" data-artwork-id="{{id}}">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                            </svg>
                        </button>
                        <button class="like-btn" data-artwork-id="{{id}}">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="compatibility-score">
                        <span class="score">{{compatibility_score}}%</span>
                        <span class="label">Match</span>
                    </div>
                </div>
                
                <div class="card-content">
                    <h3 class="artwork-title">{{title}}</h3>
                    <p class="artist-name">by {{artist}}</p>
                    <p class="artwork-description">{{description}}</p>
                    
                    <div class="artwork-details">
                        <span class="size">{{dimensions}}</span>
                        <span class="medium">{{medium}}</span>
                    </div>
                    
                    <div class="recommendation-reason">
                        <h4>Why this works for you:</h4>
                        <p>{{recommendation_reason}}</p>
                    </div>
                    
                    <div class="color-harmony" style="display: {{show_colors}};">
                        <h4>Color Harmony:</h4>
                        <div class="color-swatches">
                            {{#colors}}
                            <div class="color-swatch" style="background-color: {{color}}" title="{{name}}"></div>
                            {{/colors}}
                        </div>
                    </div>
                    
                    <div class="card-footer">
                        <div class="price-info">
                            {{#on_sale}}
                            <span class="original-price">${{original_price}}</span>
                            {{/on_sale}}
                            <span class="current-price">${{price}}</span>
                            {{#payment_plan}}
                            <span class="payment-plan">or {{payment_plan}}/month</span>
                            {{/payment_plan}}
                        </div>
                        
                        <div class="card-actions">
                            <button class="btn btn-outline btn-small share-btn" data-artwork-id="{{id}}">
                                Share
                            </button>
                            <a href="{{product_url}}" class="btn btn-primary btn-small" target="_blank">
                                View Details
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </script>

        <?php
        get_footer();
    }
    
    public function get_ai_recommendations() {
        // Verify nonce
        if (!wp_verify_nonce($_POST['nonce'], 'vividwalls_recommendations_nonce')) {
            wp_die('Security check failed');
        }
        
        $request_type = sanitize_text_field($_POST['request_type']);
        $user_input = sanitize_textarea_field($_POST['user_input']);
        $image_data = isset($_POST['image_data']) ? $_POST['image_data'] : null;
        $filters = isset($_POST['filters']) ? $_POST['filters'] : array();
        
        // Prepare payload for n8n Sales Agent
        $payload = array(
            'message' => $user_input,
            'customer_id' => get_current_user_id() ?: 'anonymous_' . time(),
            'session_id' => session_id() ?: 'session_' . time(),
            'request_type' => 'ai_recommendations',
            'source' => 'wordpress_recommendations_page',
            'filters' => $filters,
            'timestamp' => current_time('mysql')
        );
        
        if ($image_data) {
            $payload['image_analysis'] = $this->analyze_room_image($image_data);
        }
        
        $n8n_webhook = get_option('vividwalls_n8n_webhook', '');
        
        if (!empty($n8n_webhook)) {
            $response = wp_remote_post($n8n_webhook, array(
                'method' => 'POST',
                'body' => json_encode($payload),
                'headers' => array(
                    'Content-Type' => 'application/json',
                ),
                'timeout' => 60
            ));
            
            if (is_wp_error($response)) {
                wp_send_json_error('Failed to connect to AI recommendation service');
            } else {
                $body = wp_remote_retrieve_body($response);
                $data = json_decode($body, true);
                
                // Process and format recommendations
                $formatted_recommendations = $this->format_recommendations($data);
                
                wp_send_json_success($formatted_recommendations);
            }
        } else {
            wp_send_json_error('AI recommendation service not configured');
        }
    }
    
    private function analyze_room_image($image_data) {
        // This would integrate with your image analysis n8n workflow
        // For now, return mock analysis structure
        return array(
            'dominant_colors' => array(
                array('color' => '#8B4513', 'name' => 'Brown', 'percentage' => 35),
                array('color' => '#F5F5DC', 'name' => 'Beige', 'percentage' => 25),
                array('color' => '#228B22', 'name' => 'Green', 'percentage' => 20)
            ),
            'style_detected' => 'Contemporary',
            'room_type' => 'Living Room',
            'mood_classification' => 'Warm and Inviting',
            'lighting_analysis' => 'Natural light from windows',
            'wall_color' => '#F5F5DC',
            'furniture_style' => 'Modern'
        );
    }
    
    private function format_recommendations($ai_response) {
        // Format the AI response into structured recommendation data
        $recommendations = array(
            'items' => array(),
            'analysis_explanation' => $ai_response['explanation'] ?? '',
            'total_found' => 0,
            'confidence_score' => $ai_response['confidence'] ?? 95
        );
        
        if (isset($ai_response['recommendations']) && is_array($ai_response['recommendations'])) {
            foreach ($ai_response['recommendations'] as $item) {
                $recommendations['items'][] = array(
                    'id' => $item['id'] ?? uniqid('art_'),
                    'title' => $item['title'] ?? 'Beautiful Artwork',
                    'artist' => $item['artist'] ?? 'Featured Artist',
                    'description' => $item['description'] ?? '',
                    'image_url' => $item['image_url'] ?? '',
                    'product_url' => $item['product_url'] ?? '#',
                    'price' => $item['price'] ?? 299,
                    'original_price' => $item['original_price'] ?? null,
                    'dimensions' => $item['dimensions'] ?? '24" x 36"',
                    'medium' => $item['medium'] ?? 'Canvas Print',
                    'style' => $item['style'] ?? 'Contemporary',
                    'colors' => $item['colors'] ?? array(),
                    'compatibility_score' => $item['compatibility_score'] ?? rand(85, 98),
                    'recommendation_reason' => $item['reason'] ?? 'Perfect color harmony with your space',
                    'on_sale' => $item['on_sale'] ?? false,
                    'payment_plan' => $item['payment_plan'] ?? null
                );
            }
            $recommendations['total_found'] = count($recommendations['items']);
        }
        
        return $recommendations;
    }
    
    public function save_user_preferences() {
        if (!wp_verify_nonce($_POST['nonce'], 'vividwalls_recommendations_nonce')) {
            wp_die('Security check failed');
        }
        
        $user_id = get_current_user_id();
        $preferences = array(
            'liked_artworks' => sanitize_text_field($_POST['liked_artworks']),
            'style_preferences' => sanitize_text_field($_POST['style_preferences']),
            'color_preferences' => sanitize_text_field($_POST['color_preferences']),
            'budget_range' => sanitize_text_field($_POST['budget_range']),
            'room_types' => sanitize_text_field($_POST['room_types'])
        );
        
        if ($user_id > 0) {
            update_user_meta($user_id, 'vividwalls_art_preferences', $preferences);
        } else {
            // Store in session for non-logged-in users
            if (!session_id()) {
                session_start();
            }
            $_SESSION['vividwalls_preferences'] = $preferences;
        }
        
        wp_send_json_success(array('message' => 'Preferences saved successfully'));
    }
}

// Initialize the recommendations page
new VividWallsRecommendationsPage();
?>