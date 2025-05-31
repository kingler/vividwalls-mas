/**
 * VividWalls Enhanced CopilotKit Integration
 * Advanced image analysis and room visualization with AI recommendations
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        n8nEndpoint: window.vividwallsConfig?.n8nEndpoint || 'https://n8n.vividwalls.blog/webhook/vividwalls-copilot',
        artAnalysisEndpoint: 'https://n8n.vividwalls.blog/webhook/vividwalls-art-analysis',
        batchAnalysisEndpoint: 'https://n8n.vividwalls.blog/webhook/vividwalls-batch-analysis',
        maxImageSize: 5 * 1024 * 1024, // 5MB
        supportedFormats: ['image/jpeg', 'image/png', 'image/webp'],
        analysisTimeout: 120000 // 2 minutes
    };

    // Wait for DOM and React to be ready
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof React === 'undefined' || typeof ReactDOM === 'undefined') {
            console.error('React is not loaded. Enhanced CopilotKit cannot initialize.');
            return;
        }

        initializeEnhancedCopilotKit();
    });

    function initializeEnhancedCopilotKit() {
        const { useState, useEffect, useCallback, useRef } = React;

        // Enhanced VividWalls AI Assistant with Image Analysis
        const EnhancedVividWallsAssistant = () => {
            const [isOpen, setIsOpen] = useState(false);
            const [isAnalyzing, setIsAnalyzing] = useState(false);
            const [uploadedImage, setUploadedImage] = useState(null);
            const [analysisResult, setAnalysisResult] = useState(null);
            const [roomDescription, setRoomDescription] = useState('');
            const [recommendations, setRecommendations] = useState([]);
            const [chatHistory, setChatHistory] = useState([]);
            const [isLoading, setIsLoading] = useState(false);
            const fileInputRef = useRef(null);
            const canvasRef = useRef(null);

            // Image upload and analysis
            const handleImageUpload = useCallback(async (event) => {
                const file = event.target.files[0];
                if (!file) return;

                // Validate file
                if (!CONFIG.supportedFormats.includes(file.type)) {
                    alert('Please upload a JPEG, PNG, or WebP image.');
                    return;
                }

                if (file.size > CONFIG.maxImageSize) {
                    alert('Image size must be less than 5MB.');
                    return;
                }

                setIsAnalyzing(true);
                setAnalysisResult(null);

                try {
                    // Convert to base64
                    const base64 = await fileToBase64(file);
                    setUploadedImage(base64);

                    // Analyze the image
                    const analysis = await analyzeRoomImage(base64);
                    setAnalysisResult(analysis);

                    // Add to chat history
                    const analysisMessage = {
                        type: 'analysis',
                        timestamp: new Date().toISOString(),
                        content: `I've analyzed your room image! Here's what I found:
                        
**Room Analysis:**
- **Style**: ${analysis.subjectMatter?.style || 'Contemporary'}
- **Dominant Colors**: ${analysis.colorAnalysis?.dominantColors?.map(c => c.name).join(', ') || 'Neutral tones'}
- **Mood**: ${analysis.colorAnalysis?.moodClassification?.primary || 'Balanced'}
- **Recommended Rooms**: ${analysis.recommendations?.idealRooms?.join(', ') || 'Living areas'}

**Color Psychology:**
${analysis.colorAnalysis?.emotionalResponse || 'This space has a balanced and welcoming feel.'}

Let me find some perfect art pieces that would complement your space!`,
                        analysis: analysis
                    };

                    setChatHistory(prev => [...prev, analysisMessage]);

                    // Get art recommendations based on analysis
                    await getArtRecommendations(analysis);

                } catch (error) {
                    console.error('Image analysis failed:', error);
                    alert('Failed to analyze image. Please try again.');
                } finally {
                    setIsAnalyzing(false);
                }
            }, []);

            // Convert file to base64
            const fileToBase64 = (file) => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = error => reject(error);
                });
            };

            // Analyze room image using n8n workflow
            const analyzeRoomImage = async (imageData) => {
                const response = await fetch(CONFIG.artAnalysisEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        imageData: imageData,
                        analysisType: 'comprehensive',
                        source: 'room_analysis',
                        sessionId: `room_${Date.now()}`
                    })
                });

                if (!response.ok) {
                    throw new Error(`Analysis failed: ${response.statusText}`);
                }

                return await response.json();
            };

            // Get art recommendations based on room analysis
            const getArtRecommendations = async (roomAnalysis) => {
                setIsLoading(true);

                try {
                    const response = await fetch(CONFIG.n8nEndpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            chatInput: `Based on this room analysis, recommend 3-5 VividWalls art pieces that would complement this space:
                            
Room Style: ${roomAnalysis.subjectMatter?.style}
Dominant Colors: ${roomAnalysis.colorAnalysis?.dominantColors?.map(c => c.name).join(', ')}
Mood: ${roomAnalysis.colorAnalysis?.moodClassification?.primary}
Room Type: ${roomAnalysis.recommendations?.idealRooms?.[0] || 'living space'}
Color Harmony: ${roomAnalysis.colorAnalysis?.colorHarmony}

Please provide specific product recommendations with explanations of why each piece would work well in this space.`,
                            sessionId: `recommendations_${Date.now()}`,
                            roomAnalysis: roomAnalysis,
                            requestType: 'art_recommendations'
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        setRecommendations(result.recommendations || []);
                        
                        // Add recommendations to chat
                        const recMessage = {
                            type: 'recommendations',
                            timestamp: new Date().toISOString(),
                            content: result.response || 'Here are my art recommendations for your space!',
                            recommendations: result.recommendations
                        };
                        
                        setChatHistory(prev => [...prev, recMessage]);
                    }
                } catch (error) {
                    console.error('Failed to get recommendations:', error);
                } finally {
                    setIsLoading(false);
                }
            };

            // Handle text-based room description
            const handleRoomDescription = useCallback(async () => {
                if (!roomDescription.trim()) return;

                setIsLoading(true);
                const userMessage = {
                    type: 'user',
                    timestamp: new Date().toISOString(),
                    content: roomDescription
                };

                setChatHistory(prev => [...prev, userMessage]);

                try {
                    const response = await fetch(CONFIG.n8nEndpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            chatInput: roomDescription,
                            sessionId: `description_${Date.now()}`,
                            requestType: 'room_description_analysis'
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        const aiMessage = {
                            type: 'ai',
                            timestamp: new Date().toISOString(),
                            content: result.response,
                            recommendations: result.recommendations
                        };
                        
                        setChatHistory(prev => [...prev, aiMessage]);
                        if (result.recommendations) {
                            setRecommendations(result.recommendations);
                        }
                    }
                } catch (error) {
                    console.error('Failed to process room description:', error);
                } finally {
                    setIsLoading(false);
                    setRoomDescription('');
                }
            }, [roomDescription]);

            // Render image preview with analysis overlay
            const renderImagePreview = () => {
                if (!uploadedImage) return null;

                return React.createElement('div', {
                    className: 'image-preview-container'
                }, [
                    React.createElement('img', {
                        key: 'preview',
                        src: uploadedImage,
                        alt: 'Room preview',
                        className: 'room-preview-image'
                    }),
                    analysisResult && React.createElement('div', {
                        key: 'overlay',
                        className: 'analysis-overlay'
                    }, [
                        React.createElement('div', {
                            key: 'colors',
                            className: 'color-palette'
                        }, analysisResult.colorAnalysis?.dominantColors?.map((color, index) => 
                            React.createElement('div', {
                                key: index,
                                className: 'color-swatch',
                                style: { backgroundColor: color.color },
                                title: `${color.name} (${color.percentage}%)`
                            })
                        )),
                        React.createElement('div', {
                            key: 'mood',
                            className: 'mood-indicator'
                        }, `Mood: ${analysisResult.colorAnalysis?.moodClassification?.primary}`)
                    ])
                ]);
            };

            // Render chat message
            const renderChatMessage = (message, index) => {
                return React.createElement('div', {
                    key: index,
                    className: `chat-message ${message.type}`
                }, [
                    React.createElement('div', {
                        key: 'content',
                        className: 'message-content'
                    }, message.content),
                    message.recommendations && React.createElement('div', {
                        key: 'recs',
                        className: 'recommendations-grid'
                    }, message.recommendations.map((rec, recIndex) => 
                        React.createElement('div', {
                            key: recIndex,
                            className: 'recommendation-card',
                            onClick: () => window.open(rec.url, '_blank')
                        }, [
                            rec.image && React.createElement('img', {
                                key: 'img',
                                src: rec.image,
                                alt: rec.title,
                                className: 'rec-image'
                            }),
                            React.createElement('div', {
                                key: 'info',
                                className: 'rec-info'
                            }, [
                                React.createElement('h4', { key: 'title' }, rec.title),
                                React.createElement('p', { key: 'desc' }, rec.description),
                                React.createElement('span', { key: 'price' }, rec.price)
                            ])
                        ])
                    ))
                ]);
            };

            // Main assistant interface
            return React.createElement('div', {
                className: 'vividwalls-enhanced-copilot'
            }, [
                // Floating Action Button
                React.createElement('button', {
                    key: 'fab',
                    className: 'copilot-fab enhanced',
                    onClick: () => setIsOpen(!isOpen)
                }, [
                    React.createElement('span', { key: 'icon' }, '🎨'),
                    React.createElement('span', { key: 'text' }, 'VividWalls AI')
                ]),

                // Main Chat Interface
                isOpen && React.createElement('div', {
                    key: 'interface',
                    className: 'copilot-interface enhanced'
                }, [
                    // Header
                    React.createElement('div', {
                        key: 'header',
                        className: 'copilot-header'
                    }, [
                        React.createElement('h3', { key: 'title' }, 'VividWalls AI Assistant'),
                        React.createElement('button', {
                            key: 'close',
                            className: 'close-btn',
                            onClick: () => setIsOpen(false)
                        }, '×')
                    ]),

                    // Image Upload Section
                    React.createElement('div', {
                        key: 'upload',
                        className: 'upload-section'
                    }, [
                        React.createElement('input', {
                            key: 'file-input',
                            ref: fileInputRef,
                            type: 'file',
                            accept: 'image/*',
                            onChange: handleImageUpload,
                            style: { display: 'none' }
                        }),
                        React.createElement('button', {
                            key: 'upload-btn',
                            className: 'upload-btn',
                            onClick: () => fileInputRef.current?.click(),
                            disabled: isAnalyzing
                        }, [
                            React.createElement('span', { key: 'icon' }, '📷'),
                            React.createElement('span', { key: 'text' }, 
                                isAnalyzing ? 'Analyzing...' : 'Upload Room Photo'
                            )
                        ])
                    ]),

                    // Image Preview
                    renderImagePreview(),

                    // Chat History
                    React.createElement('div', {
                        key: 'chat',
                        className: 'chat-history'
                    }, chatHistory.map(renderChatMessage)),

                    // Text Input
                    React.createElement('div', {
                        key: 'input',
                        className: 'input-section'
                    }, [
                        React.createElement('textarea', {
                            key: 'textarea',
                            value: roomDescription,
                            onChange: (e) => setRoomDescription(e.target.value),
                            placeholder: 'Describe your room or ask for art recommendations...',
                            className: 'room-description-input',
                            rows: 3
                        }),
                        React.createElement('button', {
                            key: 'send',
                            onClick: handleRoomDescription,
                            disabled: isLoading || !roomDescription.trim(),
                            className: 'send-btn'
                        }, isLoading ? 'Processing...' : 'Send')
                    ])
                ])
            ]);
        };

        // Render the enhanced assistant
        const container = document.createElement('div');
        container.id = 'vividwalls-enhanced-copilot-root';
        document.body.appendChild(container);

        ReactDOM.render(
            React.createElement(EnhancedVividWallsAssistant),
            container
        );
    }

    // Utility functions for image processing
    window.VividWallsImageUtils = {
        // Resize image for analysis
        resizeImage: (file, maxWidth = 1024, maxHeight = 1024, quality = 0.8) => {
            return new Promise((resolve) => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const img = new Image();

                img.onload = () => {
                    // Calculate new dimensions
                    let { width, height } = img;
                    
                    if (width > height) {
                        if (width > maxWidth) {
                            height = (height * maxWidth) / width;
                            width = maxWidth;
                        }
                    } else {
                        if (height > maxHeight) {
                            width = (width * maxHeight) / height;
                            height = maxHeight;
                        }
                    }

                    canvas.width = width;
                    canvas.height = height;

                    // Draw and compress
                    ctx.drawImage(img, 0, 0, width, height);
                    canvas.toBlob(resolve, 'image/jpeg', quality);
                };

                img.src = URL.createObjectURL(file);
            });
        },

        // Extract dominant colors from image
        extractColors: (imageElement, colorCount = 5) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = imageElement.width;
            canvas.height = imageElement.height;
            
            ctx.drawImage(imageElement, 0, 0);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            // Simple color extraction (could be enhanced with clustering)
            const colorMap = {};
            
            for (let i = 0; i < data.length; i += 16) { // Sample every 4th pixel
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                const alpha = data[i + 3];
                
                if (alpha > 128) { // Skip transparent pixels
                    const color = `rgb(${r},${g},${b})`;
                    colorMap[color] = (colorMap[color] || 0) + 1;
                }
            }
            
            // Return top colors
            return Object.entries(colorMap)
                .sort(([,a], [,b]) => b - a)
                .slice(0, colorCount)
                .map(([color, count]) => ({ color, count }));
        }
    };

    // Global API for external integration
    window.VividWallsAPI = {
        analyzeImage: async (imageData, options = {}) => {
            const response = await fetch(CONFIG.artAnalysisEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    imageData,
                    analysisType: options.analysisType || 'comprehensive',
                    source: options.source || 'external_api',
                    sessionId: options.sessionId || `external_${Date.now()}`
                })
            });
            
            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }
            
            return await response.json();
        },

        batchAnalyze: async (imageUrls, options = {}) => {
            const response = await fetch(CONFIG.batchAnalysisEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    imageUrls,
                    analysisType: options.analysisType || 'comprehensive',
                    batchId: options.batchId || `batch_${Date.now()}`,
                    source: options.source || 'external_batch'
                })
            });
            
            if (!response.ok) {
                throw new Error(`Batch analysis failed: ${response.statusText}`);
            }
            
            return await response.json();
        },

        getRecommendations: async (roomDescription, options = {}) => {
            const response = await fetch(CONFIG.n8nEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chatInput: roomDescription,
                    sessionId: options.sessionId || `rec_${Date.now()}`,
                    requestType: 'recommendations'
                })
            });
            
            if (!response.ok) {
                throw new Error(`Recommendations failed: ${response.statusText}`);
            }
            
            return await response.json();
        }
    };

    console.log('VividWalls Enhanced CopilotKit initialized successfully!');
})(); 