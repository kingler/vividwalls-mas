/**
 * VividWalls AI Recommendations Page JavaScript
 * Handles image upload, AI analysis, and masonry grid display
 */

(function($) {
    'use strict';

    // Global state management
    window.VividWallsRecommendations = {
        state: {
            currentImage: null,
            analysisResult: null,
            recommendations: [],
            filters: {
                price: '',
                size: '',
                style: ''
            },
            sortBy: 'relevance',
            page: 1,
            loading: false,
            userPreferences: {}
        },
        
        // Configuration
        config: {
            maxImageSize: 5 * 1024 * 1024, // 5MB
            supportedFormats: ['image/jpeg', 'image/png', 'image/webp'],
            analysisTimeout: 120000, // 2 minutes
            itemsPerPage: 12,
            masonryOptions: {
                itemSelector: '.recommendation-card',
                columnWidth: '.recommendation-card',
                percentPosition: true,
                gutter: 30
            }
        }
    };

    const VWR = window.VividWallsRecommendations;

    // Initialize when document is ready
    $(document).ready(function() {
        VWR.init();
    });

    // Main initialization
    VWR.init = function() {
        this.bindEvents();
        this.initializeMasonry();
        this.loadUserPreferences();
        this.setupImageUpload();
        this.setupFilters();
        this.setupInfiniteScroll();
        
        console.log('VividWalls Recommendations initialized successfully');
    };

    // Event binding
    VWR.bindEvents = function() {
        // Image upload events
        $('#upload-btn').on('click', function() {
            $('#room-image-input').click();
        });
        
        $('#room-image-input').on('change', this.handleImageUpload.bind(this));
        
        // Drag and drop events
        this.setupDragAndDrop();
        
        // Analysis and recommendation events
        $('#analyze-image').on('click', this.analyzeImage.bind(this));
        $('#get-recommendations').on('click', this.getTextBasedRecommendations.bind(this));
        $('#change-image').on('click', this.resetImageUpload.bind(this));
        
        // Filter and sort events
        $('#price-filter, #size-filter, #style-filter').on('change', this.applyFilters.bind(this));
        $('#sort-options').on('change', this.applySorting.bind(this));
        
        // Style tag events
        $('.filter-tag').on('click', this.toggleStyleFilter.bind(this));
        
        // Load more
        $('#load-more-btn').on('click', this.loadMoreRecommendations.bind(this));
        
        // Card interaction events
        $(document).on('click', '.quick-view-btn', this.showQuickView.bind(this));
        $(document).on('click', '.like-btn', this.toggleLike.bind(this));
        $(document).on('click', '.share-btn', this.shareArtwork.bind(this));
    };

    // Setup drag and drop functionality
    VWR.setupDragAndDrop = function() {
        const $uploadArea = $('#upload-area');
        
        $uploadArea.on('dragover dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).addClass('drag-over');
        });
        
        $uploadArea.on('dragleave dragend drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).removeClass('drag-over');
        });
        
        $uploadArea.on('drop', function(e) {
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                VWR.processImageFile(files[0]);
            }
        });
    };

    // Handle image upload
    VWR.handleImageUpload = function(event) {
        const file = event.target.files[0];
        if (file) {
            this.processImageFile(file);
        }
    };

    // Process uploaded image file
    VWR.processImageFile = function(file) {
        // Validate file
        if (!this.config.supportedFormats.includes(file.type)) {
            this.showError('Please upload a JPEG, PNG, or WebP image.');
            return;
        }

        if (file.size > this.config.maxImageSize) {
            this.showError('Image size must be less than 5MB.');
            return;
        }

        // Show loading
        this.showLoading('Processing your image...');

        // Convert to base64 and preview
        this.fileToBase64(file)
            .then(base64 => {
                this.state.currentImage = base64;
                this.showImagePreview(base64);
                this.hideLoading();
            })
            .catch(error => {
                this.showError('Failed to process image. Please try again.');
                this.hideLoading();
                console.error('Image processing error:', error);
            });
    };

    // Convert file to base64
    VWR.fileToBase64 = function(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    // Show image preview
    VWR.showImagePreview = function(base64) {
        $('#preview-image').attr('src', base64);
        $('#upload-section').hide();
        $('#image-preview').show();
        
        // Scroll to preview
        $('html, body').animate({
            scrollTop: $('#image-preview').offset().top - 100
        }, 500);
    };

    // Reset image upload
    VWR.resetImageUpload = function() {
        this.state.currentImage = null;
        this.state.analysisResult = null;
        $('#room-image-input').val('');
        $('#image-preview').hide();
        $('#upload-section').show();
        $('#analysis-overlay').empty();
    };

    // Analyze uploaded image
    VWR.analyzeImage = function() {
        if (!this.state.currentImage) {
            this.showError('Please upload an image first.');
            return;
        }

        this.showLoading('Analyzing your room...', 'Our AI is examining colors, style, and composition to find perfect art matches');
        this.updateProgress(10);

        // Simulate progress updates
        const progressInterval = setInterval(() => {
            const currentProgress = parseInt($('#progress-bar').css('width')) || 0;
            if (currentProgress < 90) {
                this.updateProgress(currentProgress + 10);
            }
        }, 500);

        // Send to AI analysis endpoint
        $.ajax({
            url: vividwalls_recs.ajax_url,
            type: 'POST',
            data: {
                action: 'get_ai_recommendations',
                nonce: vividwalls_recs.nonce,
                request_type: 'image_analysis',
                image_data: this.state.currentImage,
                user_input: 'Analyze this room image and provide art recommendations',
                filters: this.state.filters
            },
            timeout: this.config.analysisTimeout,
            success: (response) => {
                clearInterval(progressInterval);
                this.updateProgress(100);
                
                setTimeout(() => {
                    this.hideLoading();
                    
                    if (response.success) {
                        this.handleAnalysisSuccess(response.data);
                    } else {
                        this.showError(response.data || 'Analysis failed. Please try again.');
                    }
                }, 1000);
            },
            error: (xhr, status, error) => {
                clearInterval(progressInterval);
                this.hideLoading();
                this.showError('Failed to analyze image. Please check your connection and try again.');
                console.error('Analysis error:', error);
            }
        });
    };

    // Handle successful analysis
    VWR.handleAnalysisSuccess = function(data) {
        this.state.analysisResult = data.analysis_explanation;
        this.state.recommendations = data.items || [];

        // Update analysis overlay
        this.updateAnalysisOverlay(data);

        // Show recommendations
        this.displayRecommendations(data.items);

        // Show analysis explanation
        this.showAnalysisExplanation(data.analysis_explanation);

        // Scroll to recommendations
        $('html, body').animate({
            scrollTop: $('#recommendations-section').offset().top - 80
        }, 800);
    };

    // Update analysis overlay on image
    VWR.updateAnalysisOverlay = function(data) {
        const $overlay = $('#analysis-overlay');
        const $colorAnalysis = $('#color-analysis');
        const $styleTags = $('#style-tags');

        // Clear existing content
        $colorAnalysis.empty();
        $styleTags.empty();

        // Add color swatches if available
        if (data.dominant_colors && data.dominant_colors.length > 0) {
            data.dominant_colors.forEach(color => {
                $colorAnalysis.append(`
                    <div class="color-swatch" 
                         style="background-color: ${color.color}" 
                         title="${color.name} (${color.percentage}%)">
                    </div>
                `);
            });
        }

        // Add style tags
        const styleTags = [
            data.style_detected || 'Contemporary',
            data.room_type || 'Living Space',
            data.mood_classification || 'Balanced'
        ];

        styleTags.forEach(tag => {
            $styleTags.append(`<span class="style-tag">${tag}</span>`);
        });
    };

    // Get text-based recommendations
    VWR.getTextBasedRecommendations = function() {
        const userInput = $('#style-description').val().trim();
        const selectedStyles = $('.filter-tag.active').map(function() {
            return $(this).data('style');
        }).get();

        if (!userInput && selectedStyles.length === 0) {
            this.showError('Please describe your preferences or select some style filters.');
            return;
        }

        let combinedInput = userInput;
        if (selectedStyles.length > 0) {
            combinedInput += ` Style preferences: ${selectedStyles.join(', ')}`;
        }

        this.showLoading('Finding perfect art for you...', 'Our AI is searching through thousands of artworks to find your ideal matches');
        this.updateProgress(20);

        // Simulate progress
        const progressInterval = setInterval(() => {
            const currentProgress = parseInt($('#progress-bar').css('width')) || 0;
            if (currentProgress < 90) {
                this.updateProgress(currentProgress + 15);
            }
        }, 800);

        $.ajax({
            url: vividwalls_recs.ajax_url,
            type: 'POST',
            data: {
                action: 'get_ai_recommendations',
                nonce: vividwalls_recs.nonce,
                request_type: 'text_analysis',
                user_input: combinedInput,
                filters: this.state.filters,
                style_preferences: selectedStyles
            },
            timeout: this.config.analysisTimeout,
            success: (response) => {
                clearInterval(progressInterval);
                this.updateProgress(100);
                
                setTimeout(() => {
                    this.hideLoading();
                    
                    if (response.success) {
                        this.handleRecommendationsSuccess(response.data);
                    } else {
                        this.showError(response.data || 'Failed to get recommendations. Please try again.');
                    }
                }, 1000);
            },
            error: (xhr, status, error) => {
                clearInterval(progressInterval);
                this.hideLoading();
                this.showError('Failed to get recommendations. Please check your connection and try again.');
                console.error('Recommendations error:', error);
            }
        });
    };

    // Handle successful recommendations
    VWR.handleRecommendationsSuccess = function(data) {
        this.state.recommendations = data.items || [];
        this.displayRecommendations(data.items);
        this.showAnalysisExplanation(data.analysis_explanation);

        // Scroll to recommendations
        $('html, body').animate({
            scrollTop: $('#recommendations-section').offset().top - 80
        }, 800);
    };

    // Display recommendations in masonry grid
    VWR.displayRecommendations = function(items) {
        if (!items || items.length === 0) {
            this.showNoRecommendations();
            return;
        }

        const $grid = $('#recommendations-grid');
        $grid.empty();

        // Show recommendations section
        $('#recommendations-section').show();

        // Add items to grid
        items.forEach(item => {
            const $card = this.createRecommendationCard(item);
            $grid.append($card);
        });

        // Trigger masonry layout
        setTimeout(() => {
            $grid.masonry('reloadItems');
            $grid.masonry('layout');
        }, 100);

        // Lazy load images
        this.initializeLazyLoading();
    };

    // Create recommendation card HTML
    VWR.createRecommendationCard = function(item) {
        const template = $('#recommendation-card-template').html();
        
        // Process colors for display
        const showColors = item.colors && item.colors.length > 0 ? 'block' : 'none';
        const colorsHtml = item.colors ? item.colors.map(color => 
            `<div class="color-swatch" style="background-color: ${color.color}" title="${color.name}"></div>`
        ).join('') : '';

        // Replace template variables
        let cardHtml = template
            .replace(/\{\{id\}\}/g, item.id)
            .replace(/\{\{title\}\}/g, item.title)
            .replace(/\{\{artist\}\}/g, item.artist)
            .replace(/\{\{description\}\}/g, item.description)
            .replace(/\{\{image_url\}\}/g, item.image_url)
            .replace(/\{\{product_url\}\}/g, item.product_url)
            .replace(/\{\{price\}\}/g, item.price.toLocaleString())
            .replace(/\{\{dimensions\}\}/g, item.dimensions)
            .replace(/\{\{medium\}\}/g, item.medium)
            .replace(/\{\{style\}\}/g, item.style)
            .replace(/\{\{size\}\}/g, this.categorizeSize(item.dimensions))
            .replace(/\{\{compatibility_score\}\}/g, item.compatibility_score)
            .replace(/\{\{recommendation_reason\}\}/g, item.recommendation_reason)
            .replace(/\{\{show_colors\}\}/g, showColors);

        // Handle conditional content
        if (item.on_sale && item.original_price) {
            cardHtml = cardHtml.replace(/\{\{#on_sale\}\}(.*?)\{\{\\/on_sale\}\}/gs, '$1');
            cardHtml = cardHtml.replace(/\{\{original_price\}\}/g, item.original_price.toLocaleString());
        } else {
            cardHtml = cardHtml.replace(/\{\{#on_sale\}\}(.*?)\{\{\\/on_sale\}\}/gs, '');
        }

        if (item.payment_plan) {
            cardHtml = cardHtml.replace(/\{\{#payment_plan\}\}(.*?)\{\{\\/payment_plan\}\}/gs, '$1');
            cardHtml = cardHtml.replace(/\{\{payment_plan\}\}/g, item.payment_plan);
        } else {
            cardHtml = cardHtml.replace(/\{\{#payment_plan\}\}(.*?)\{\{\\/payment_plan\}\}/gs, '');
        }

        // Add colors
        cardHtml = cardHtml.replace(/\{\{#colors\}\}(.*?)\{\{\\/colors\}\}/gs, colorsHtml);

        return $(cardHtml);
    };

    // Categorize artwork size
    VWR.categorizeSize = function(dimensions) {
        if (!dimensions) return 'medium';
        
        const numbers = dimensions.match(/\d+/g);
        if (!numbers || numbers.length < 2) return 'medium';
        
        const maxDimension = Math.max(parseInt(numbers[0]), parseInt(numbers[1]));
        
        if (maxDimension < 16) return 'small';
        if (maxDimension < 24) return 'medium';
        if (maxDimension < 36) return 'large';
        return 'xl';
    };

    // Show analysis explanation
    VWR.showAnalysisExplanation = function(explanation) {
        if (!explanation) return;

        const $section = $('#analysis-explanation');
        const $breakdown = $('#analysis-breakdown');

        // Create breakdown items
        const breakdownItems = [
            {
                icon: '🎨',
                title: 'Style Analysis',
                description: 'We analyzed your space\'s aesthetic and identified key style elements that guide our recommendations.'
            },
            {
                icon: '🌈',
                title: 'Color Harmony',
                description: 'Our AI examined color relationships to find artworks that create perfect visual balance in your room.'
            },
            {
                icon: '📐',
                title: 'Proportions & Scale',
                description: 'We considered your room\'s dimensions and furniture scale to recommend appropriately sized pieces.'
            },
            {
                icon: '💡',
                title: 'Personal Preferences',
                description: 'Your stated preferences and style choices were factored into every recommendation we made.'
            }
        ];

        $breakdown.empty();
        breakdownItems.forEach(item => {
            $breakdown.append(`
                <div class="breakdown-item">
                    <div class="icon">${item.icon}</div>
                    <h4>${item.title}</h4>
                    <p>${item.description}</p>
                </div>
            `);
        });

        $section.show();
    };

    // Show no recommendations message
    VWR.showNoRecommendations = function() {
        $('#recommendations-section').show();
        $('#recommendations-grid').html(`
            <div class="no-recommendations">
                <div class="no-rec-icon">🎨</div>
                <h3>No Perfect Matches Found</h3>
                <p>Try adjusting your preferences or uploading a different image for better results.</p>
                <button class="btn btn-primary" onclick="location.reload()">Start Over</button>
            </div>
        `);
    };

    // Initialize masonry grid
    VWR.initializeMasonry = function() {
        const $grid = $('#recommendations-grid');
        
        // Initialize masonry after images load
        $grid.imagesLoaded(function() {
            $grid.masonry(VWR.config.masonryOptions);
        });
    };

    // Setup filters
    VWR.setupFilters = function() {
        // Apply filters when changed
        $('#price-filter, #size-filter, #style-filter').on('change', function() {
            VWR.applyFilters();
        });
    };

    // Apply filters to recommendations
    VWR.applyFilters = function() {
        this.state.filters = {
            price: $('#price-filter').val(),
            size: $('#size-filter').val(),
            style: $('#style-filter').val()
        };

        this.filterRecommendations();
    };

    // Filter recommendations based on current filters
    VWR.filterRecommendations = function() {
        const $cards = $('.recommendation-card');
        
        $cards.each(function() {
            const $card = $(this);
            const price = parseFloat($card.data('price'));
            const size = $card.data('size');
            const style = $card.data('style');
            
            let visible = true;

            // Price filter
            if (VWR.state.filters.price) {
                const priceRange = VWR.state.filters.price;
                if (priceRange === '0-500' && price > 500) visible = false;
                if (priceRange === '500-1000' && (price < 500 || price > 1000)) visible = false;
                if (priceRange === '1000-2000' && (price < 1000 || price > 2000)) visible = false;
                if (priceRange === '2000+' && price < 2000) visible = false;
            }

            // Size filter
            if (VWR.state.filters.size && size !== VWR.state.filters.size) {
                visible = false;
            }

            // Style filter
            if (VWR.state.filters.style && style.toLowerCase() !== VWR.state.filters.style.toLowerCase()) {
                visible = false;
            }

            // Show/hide card
            if (visible) {
                $card.show();
            } else {
                $card.hide();
            }
        });

        // Refresh masonry layout
        setTimeout(() => {
            $('#recommendations-grid').masonry('layout');
        }, 100);
    };

    // Apply sorting
    VWR.applySorting = function() {
        const sortBy = $('#sort-options').val();
        this.state.sortBy = sortBy;

        const $grid = $('#recommendations-grid');
        const $cards = $grid.children('.recommendation-card').get();

        $cards.sort((a, b) => {
            const $a = $(a);
            const $b = $(b);

            switch (sortBy) {
                case 'price-low':
                    return parseFloat($a.data('price')) - parseFloat($b.data('price'));
                case 'price-high':
                    return parseFloat($b.data('price')) - parseFloat($a.data('price'));
                case 'size':
                    const sizeOrder = { small: 1, medium: 2, large: 3, xl: 4 };
                    return sizeOrder[$a.data('size')] - sizeOrder[$b.data('size')];
                case 'newest':
                    return Math.random() - 0.5; // Random for demo
                default: // relevance
                    return 0; // Keep original order
            }
        });

        $.each($cards, function(index, item) {
            $grid.append(item);
        });

        // Refresh masonry layout
        setTimeout(() => {
            $grid.masonry('layout');
        }, 100);
    };

    // Toggle style filter
    VWR.toggleStyleFilter = function(event) {
        const $tag = $(event.currentTarget);
        $tag.toggleClass('active');
        
        // Update style description with selected filters
        this.updateStyleDescription();
    };

    // Update style description with selected filters
    VWR.updateStyleDescription = function() {
        const selectedStyles = $('.filter-tag.active').map(function() {
            return $(this).text();
        }).get();

        if (selectedStyles.length > 0) {
            const currentText = $('#style-description').val();
            if (!currentText.includes('Style preferences:')) {
                const newText = currentText + (currentText ? '\n\n' : '') + 
                               `Style preferences: ${selectedStyles.join(', ')}`;
                $('#style-description').val(newText);
            }
        }
    };

    // Quick view functionality
    VWR.showQuickView = function(event) {
        const artworkId = $(event.currentTarget).data('artwork-id');
        // Implementation for quick view modal
        console.log('Quick view for artwork:', artworkId);
        
        // For now, just scroll to the card
        const $card = $(`.recommendation-card[data-artwork-id="${artworkId}"]`);
        $('html, body').animate({
            scrollTop: $card.offset().top - 100
        }, 500);
    };

    // Toggle like functionality
    VWR.toggleLike = function(event) {
        event.preventDefault();
        const $btn = $(event.currentTarget);
        const artworkId = $btn.data('artwork-id');
        
        $btn.toggleClass('liked');
        
        // Save to user preferences
        this.saveUserPreference('liked_artworks', artworkId);
        
        // Visual feedback
        if ($btn.hasClass('liked')) {
            $btn.css('color', '#e53e3e');
            this.showToast('Added to favorites ❤️');
        } else {
            $btn.css('color', '');
            this.showToast('Removed from favorites');
        }
    };

    // Share artwork
    VWR.shareArtwork = function(event) {
        const $card = $(event.currentTarget).closest('.recommendation-card');
        const title = $card.find('.artwork-title').text();
        const url = $card.find('.btn-primary').attr('href');
        
        if (navigator.share) {
            navigator.share({
                title: `Check out this artwork: ${title}`,
                url: url
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(url).then(() => {
                this.showToast('Link copied to clipboard!');
            });
        }
    };

    // Load more recommendations
    VWR.loadMoreRecommendations = function() {
        this.state.page++;
        // Implementation for loading more items
        this.showToast('Loading more recommendations...');
    };

    // Initialize lazy loading for images
    VWR.initializeLazyLoading = function() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    };

    // Setup infinite scroll
    VWR.setupInfiniteScroll = function() {
        $(window).on('scroll', function() {
            if ($(window).scrollTop() + $(window).height() > $(document).height() - 1000) {
                if (!VWR.state.loading && VWR.state.recommendations.length >= VWR.config.itemsPerPage) {
                    VWR.loadMoreRecommendations();
                }
            }
        });
    };

    // User preferences management
    VWR.loadUserPreferences = function() {
        const userId = vividwalls_recs.user_id;
        if (userId > 0) {
            // Load from user meta or AJAX call
            // For now, use localStorage
            const prefs = localStorage.getItem('vividwalls_preferences');
            if (prefs) {
                this.state.userPreferences = JSON.parse(prefs);
            }
        }
    };

    VWR.saveUserPreference = function(key, value) {
        this.state.userPreferences[key] = value;
        localStorage.setItem('vividwalls_preferences', JSON.stringify(this.state.userPreferences));
        
        // Also save to server if user is logged in
        if (vividwalls_recs.user_id > 0) {
            $.post(vividwalls_recs.ajax_url, {
                action: 'save_user_preferences',
                nonce: vividwalls_recs.nonce,
                [key]: value
            });
        }
    };

    // Utility functions
    VWR.showLoading = function(title, message) {
        $('#loading-overlay').show();
        $('#loading-overlay h3').text(title || 'Loading...');
        $('#loading-overlay p').text(message || 'Please wait while we process your request');
        $('#progress-bar').css('width', '0%');
        this.state.loading = true;
    };

    VWR.hideLoading = function() {
        $('#loading-overlay').hide();
        this.state.loading = false;
    };

    VWR.updateProgress = function(percentage) {
        $('#progress-bar').css('width', percentage + '%');
    };

    VWR.showError = function(message) {
        this.showToast(message, 'error');
    };

    VWR.showToast = function(message, type = 'success') {
        // Create toast notification
        const toast = $(`
            <div class="toast toast-${type}">
                <div class="toast-content">
                    <span class="toast-icon">${type === 'error' ? '❌' : '✅'}</span>
                    <span class="toast-message">${message}</span>
                </div>
            </div>
        `);

        // Add toast styles if not already present
        if (!$('#toast-styles').length) {
            $('head').append(`
                <style id="toast-styles">
                    .toast {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        border-left: 4px solid #48bb78;
                        padding: 16px 20px;
                        z-index: 10001;
                        animation: slideInRight 0.3s ease;
                        max-width: 400px;
                    }
                    .toast-error {
                        border-left-color: #e53e3e;
                    }
                    .toast-content {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                    }
                    .toast-message {
                        flex: 1;
                        font-size: 14px;
                        color: #2d3748;
                    }
                    @keyframes slideInRight {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                </style>
            `);
        }

        $('body').append(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.fadeOut(300, () => toast.remove());
        }, 3000);
    };

})(jQuery);