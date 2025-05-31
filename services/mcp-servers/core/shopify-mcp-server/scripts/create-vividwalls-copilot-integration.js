#!/usr/bin/env node

/**
 * VividWalls CopilotKit Shopify Integration Script
 * This script uses the Shopify MCP server to add CopilotKit functionality to the active theme
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';

const SHOPIFY_MCP_SERVER = './build/index.js';
const N8N_WEBHOOK_URL = 'http://157.230.13.13:5678/webhook/vividwalls-chat';

// Enhanced JavaScript for Shopify (adapted from WordPress version)
const SHOPIFY_COPILOT_JS = `/**
 * VividWalls CopilotKit Shopify Integration
 * Handles the React component rendering and n8n workflow communication
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        n8nWebhookUrl: '${N8N_WEBHOOK_URL}',
        sessionStorageKey: 'vividwalls_session_id',
        apiTimeout: 30000
    };

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        // Load React and ReactDOM from CDN if not available
        loadReactDependencies(() => {
            initializeCopilotKit();
        });
    });

    function loadReactDependencies(callback) {
        if (typeof React !== 'undefined' && typeof ReactDOM !== 'undefined') {
            callback();
            return;
        }

        let loadedCount = 0;
        const totalDeps = 2;

        function checkLoaded() {
            loadedCount++;
            if (loadedCount === totalDeps) {
                callback();
            }
        }

        // Load React
        const reactScript = document.createElement('script');
        reactScript.src = 'https://unpkg.com/react@18/umd/react.production.min.js';
        reactScript.onload = checkLoaded;
        document.head.appendChild(reactScript);

        // Load ReactDOM
        const reactDOMScript = document.createElement('script');
        reactDOMScript.src = 'https://unpkg.com/react-dom@18/umd/react-dom.production.min.js';
        reactDOMScript.onload = checkLoaded;
        document.head.appendChild(reactDOMScript);
    }

    function initializeCopilotKit() {
        const { useState, useEffect, useCallback } = React;

        // VividWalls AI Assistant Component
        const VividWallsAssistant = () => {
            const [isOpen, setIsOpen] = useState(false);
            const [messages, setMessages] = useState([]);
            const [isLoading, setIsLoading] = useState(false);
            const [sessionId] = useState(() => {
                let id = sessionStorage.getItem(CONFIG.sessionStorageKey);
                if (!id) {
                    id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    sessionStorage.setItem(CONFIG.sessionStorageKey, id);
                }
                return id;
            });

            // Get current page context
            const getPageContext = useCallback(() => {
                const context = {
                    url: window.location.href,
                    path: window.location.pathname,
                    title: document.title,
                    type: 'unknown'
                };

                // Detect page type
                if (context.path.includes('/products/')) {
                    context.type = 'product';
                    context.productHandle = context.path.split('/products/')[1]?.split('?')[0];
                } else if (context.path.includes('/collections/')) {
                    context.type = 'collection';
                    context.collectionHandle = context.path.split('/collections/')[1]?.split('?')[0];
                } else if (context.path === '/') {
                    context.type = 'home';
                } else if (context.path.includes('/cart')) {
                    context.type = 'cart';
                }

                // Get product data if on product page
                if (context.type === 'product' && window.ShopifyAnalytics?.meta) {
                    context.productData = {
                        id: window.ShopifyAnalytics.meta.product.id,
                        title: window.ShopifyAnalytics.meta.product.title,
                        type: window.ShopifyAnalytics.meta.product.type,
                        vendor: window.ShopifyAnalytics.meta.product.vendor,
                        price: window.ShopifyAnalytics.meta.product.price
                    };
                }

                return context;
            }, []);

            // Handle image upload and analysis
            const handleImageUpload = useCallback(async (file) => {
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        resolve(e.target.result);
                    };
                    reader.readAsDataURL(file);
                });
            }, []);

            // Send message to n8n webhook
            const sendMessage = useCallback(async (message, imageData = null) => {
                setIsLoading(true);
                
                try {
                    const pageContext = getPageContext();
                    
                    const payload = {
                        chatInput: message,
                        sessionId: sessionId,
                        pageContext: pageContext,
                        timestamp: new Date().toISOString(),
                        imageData: imageData
                    };

                    const response = await fetch(CONFIG.n8nWebhookUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payload),
                        signal: AbortSignal.timeout(CONFIG.apiTimeout)
                    });

                    if (!response.ok) {
                        throw new Error(\`HTTP error! status: \${response.status}\`);
                    }

                    const result = await response.json();
                    return result;
                    
                } catch (error) {
                    console.error('Error sending message:', error);
                    return {
                        response: 'Sorry, I encountered an error connecting to our AI assistant. Please try again.',
                        error: true
                    };
                } finally {
                    setIsLoading(false);
                }
            }, [sessionId, getPageContext]);

            // Chat Interface Component
            const ChatInterface = () => {
                const [inputValue, setInputValue] = useState('');
                const [dragOver, setDragOver] = useState(false);

                const handleSubmit = async (e) => {
                    e.preventDefault();
                    if (!inputValue.trim() || isLoading) return;

                    const userMessage = {
                        id: Date.now(),
                        text: inputValue,
                        sender: 'user',
                        timestamp: new Date()
                    };

                    setMessages(prev => [...prev, userMessage]);
                    setInputValue('');

                    const response = await sendMessage(inputValue);
                    
                    const aiMessage = {
                        id: Date.now() + 1,
                        text: response.response || response.message || response,
                        sender: 'ai',
                        timestamp: new Date(),
                        recommendations: response.recommendations || null,
                        visualizations: response.visualizations || null
                    };

                    setMessages(prev => [...prev, aiMessage]);
                };

                const handleImageDrop = async (e) => {
                    e.preventDefault();
                    setDragOver(false);
                    
                    const files = Array.from(e.dataTransfer.files);
                    const imageFile = files.find(file => file.type.startsWith('image/'));
                    
                    if (imageFile) {
                        const imageData = await handleImageUpload(imageFile);
                        const userMessage = {
                            id: Date.now(),
                            text: 'Uploaded an image of my space',
                            sender: 'user',
                            timestamp: new Date(),
                            image: imageData
                        };

                        setMessages(prev => [...prev, userMessage]);

                        const response = await sendMessage('Please analyze this room image and recommend suitable VividWalls artwork', imageData);
                        
                        const aiMessage = {
                            id: Date.now() + 1,
                            text: response.response || response.message || response,
                            sender: 'ai',
                            timestamp: new Date(),
                            recommendations: response.recommendations || null,
                            visualizations: response.visualizations || null
                        };

                        setMessages(prev => [...prev, aiMessage]);
                    }
                };

                // Generate contextual welcome message
                const getWelcomeMessage = () => {
                    const context = getPageContext();
                    
                    if (context.type === 'product') {
                        return {
                            title: 'Hi! I\\'m your VividWalls art advisor.',
                            subtitle: 'I can help you with this artwork and find perfect pieces for your space.',
                            suggestions: [
                                '🎨 Get details about this artwork',
                                '📏 Help with sizing and framing',
                                '🏠 Find complementary pieces',
                                '📸 Analyze your room for placement'
                            ]
                        };
                    } else if (context.type === 'collection') {
                        return {
                            title: 'Welcome to VividWalls!',
                            subtitle: 'I can help you discover the perfect artwork from this collection.',
                            suggestions: [
                                '🎯 Find art that matches your style',
                                '📸 Upload a room photo for recommendations',
                                '💡 Learn about limited editions',
                                '📐 Get sizing advice'
                            ]
                        };
                    } else {
                        return {
                            title: 'Hi! I\\'m your VividWalls AI assistant.',
                            subtitle: 'I can help you discover perfect artwork for your space.',
                            suggestions: [
                                '🎨 Find artwork by style or theme',
                                '📸 Analyze room photos for recommendations',
                                '💡 Learn about our collections',
                                '📏 Get sizing and framing help'
                            ]
                        };
                    }
                };

                const welcomeMsg = getWelcomeMessage();

                return React.createElement('div', {
                    className: 'vividwalls-chat-interface',
                    onDrop: handleImageDrop,
                    onDragOver: (e) => { e.preventDefault(); setDragOver(true); },
                    onDragLeave: () => setDragOver(false)
                }, [
                    // Chat Header
                    React.createElement('div', {
                        key: 'header',
                        className: 'chat-header'
                    }, [
                        React.createElement('h3', { key: 'title' }, 'VividWalls AI Assistant'),
                        React.createElement('button', {
                            key: 'close',
                            className: 'close-btn',
                            onClick: () => setIsOpen(false),
                            'aria-label': 'Close chat'
                        }, '×')
                    ]),

                    // Messages Container
                    React.createElement('div', {
                        key: 'messages',
                        className: 'messages-container'
                    }, [
                        // Welcome message
                        messages.length === 0 && React.createElement('div', {
                            key: 'welcome',
                            className: 'welcome-message'
                        }, [
                            React.createElement('h4', { key: 'title' }, welcomeMsg.title),
                            React.createElement('p', { key: 'subtitle' }, welcomeMsg.subtitle),
                            React.createElement('ul', { key: 'list' }, 
                                welcomeMsg.suggestions.map((suggestion, index) =>
                                    React.createElement('li', { key: index }, suggestion)
                                )
                            ),
                            React.createElement('p', { key: 'prompt', className: 'welcome-prompt' }, 
                                'Try asking: "What artwork would work in a modern living room?" or drag & drop a photo!'
                            )
                        ]),

                        // Message list
                        ...messages.map(message => 
                            React.createElement('div', {
                                key: message.id,
                                className: \`message \${message.sender}\`
                            }, [
                                message.image && React.createElement('img', {
                                    key: 'image',
                                    src: message.image,
                                    alt: 'Uploaded room image',
                                    className: 'message-image'
                                }),
                                React.createElement('div', {
                                    key: 'text',
                                    className: 'message-text'
                                }, message.text),
                                
                                // Render art recommendations if available
                                message.recommendations && React.createElement('div', {
                                    key: 'recommendations',
                                    className: 'art-recommendations'
                                }, message.recommendations.map((rec, index) =>
                                    React.createElement('div', {
                                        key: index,
                                        className: 'recommendation-card'
                                    }, [
                                        React.createElement('img', {
                                            key: 'img',
                                            src: rec.image,
                                            alt: rec.title,
                                            loading: 'lazy'
                                        }),
                                        React.createElement('h4', { key: 'title' }, rec.title),
                                        React.createElement('p', { key: 'desc' }, rec.description),
                                        React.createElement('a', {
                                            key: 'link',
                                            href: rec.url,
                                            className: 'view-artwork-btn',
                                            target: '_blank',
                                            rel: 'noopener noreferrer'
                                        }, 'View Artwork')
                                    ])
                                ))
                            ])
                        ),

                        // Loading indicator
                        isLoading && React.createElement('div', {
                            key: 'loading',
                            className: 'message ai loading'
                        }, React.createElement('div', { className: 'typing-indicator' }, [
                            React.createElement('span', { key: '1' }),
                            React.createElement('span', { key: '2' }),
                            React.createElement('span', { key: '3' })
                        ]))
                    ]),

                    // Input Form
                    React.createElement('form', {
                        key: 'form',
                        className: 'chat-input-form',
                        onSubmit: handleSubmit
                    }, [
                        React.createElement('div', {
                            key: 'input-container',
                            className: \`input-container \${dragOver ? 'drag-over' : ''}\`
                        }, [
                            React.createElement('input', {
                                key: 'input',
                                type: 'text',
                                value: inputValue,
                                onChange: (e) => setInputValue(e.target.value),
                                placeholder: 'Ask about artwork or drag & drop a room photo...',
                                disabled: isLoading,
                                'aria-label': 'Chat message input'
                            }),
                            React.createElement('button', {
                                key: 'submit',
                                type: 'submit',
                                disabled: !inputValue.trim() || isLoading,
                                'aria-label': 'Send message'
                            }, '→')
                        ])
                    ])
                ]);
            };

            return React.createElement('div', {
                className: \`vividwalls-copilot \${isOpen ? 'open' : ''}\`,
                role: 'dialog',
                'aria-label': 'VividWalls AI Assistant'
            }, [
                // Floating Action Button
                !isOpen && React.createElement('button', {
                    key: 'fab',
                    className: 'copilot-fab',
                    onClick: () => setIsOpen(true),
                    'aria-label': 'Open VividWalls AI Assistant'
                }, [
                    React.createElement('span', { key: 'icon', 'aria-hidden': 'true' }, '🎨'),
                    React.createElement('span', { key: 'text' }, 'Get Art Recommendations')
                ]),

                // Chat Interface
                isOpen && React.createElement(ChatInterface, { key: 'chat' })
            ]);
        };

        // Create container and render
        function renderCopilot() {
            let container = document.getElementById('vividwalls-copilot-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'vividwalls-copilot-container';
                document.body.appendChild(container);
            }

            ReactDOM.render(React.createElement(VividWallsAssistant), container);
        }

        // Initialize on all pages
        renderCopilot();

        // Re-render on page changes (for SPA-like behavior)
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                setTimeout(renderCopilot, 100); // Small delay to ensure page has updated
            }
        }).observe(document, { subtree: true, childList: true });
    }

    // Utility function to generate session ID
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

})();`;

// Enhanced CSS for Shopify (adapted from WordPress version)
const SHOPIFY_COPILOT_CSS = `/**
 * VividWalls CopilotKit Shopify Integration Styles
 * Modern, responsive design for the AI assistant interface
 */

/* Main Container */
.vividwalls-copilot {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* Floating Action Button */
.copilot-fab {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
}

.copilot-fab:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.copilot-fab span:first-child {
    font-size: 18px;
}

@keyframes pulse {
    0% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
    50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.8); }
    100% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
}

/* Chat Interface */
.vividwalls-chat-interface {
    width: 380px;
    height: 600px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #e1e5e9;
}

/* Chat Header */
.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
}

.close-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

/* Messages Container */
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

/* Welcome Message */
.welcome-message {
    background: #f8f9ff;
    border: 1px solid #e1e5e9;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.welcome-message h4 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 16px;
    font-weight: 600;
}

.welcome-message p {
    margin: 0 0 12px 0;
    color: #4a5568;
    font-size: 14px;
}

.welcome-message .welcome-prompt {
    font-size: 12px;
    color: #666;
    font-style: italic;
}

.welcome-message ul {
    list-style: none;
    padding: 0;
    margin: 12px 0;
    text-align: left;
}

.welcome-message li {
    padding: 4px 0;
    font-size: 13px;
    color: #666;
}

/* Messages */
.message {
    max-width: 85%;
    margin-bottom: 12px;
}

.message.user {
    align-self: flex-end;
    margin-left: auto;
}

.message.ai {
    align-self: flex-start;
}

.message-text {
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 14px;
    line-height: 1.4;
    word-wrap: break-word;
}

.message.user .message-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
}

.message.ai .message-text {
    background: #f1f3f4;
    color: #333;
    border-bottom-left-radius: 4px;
}

.message-image {
    max-width: 200px;
    border-radius: 12px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Art Recommendations */
.art-recommendations {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin-top: 12px;
}

.recommendation-card {
    background: white;
    border: 1px solid #e1e5e9;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.recommendation-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-card img {
    width: 100%;
    height: 100px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 8px;
}

.recommendation-card h4 {
    margin: 0 0 4px 0;
    font-size: 12px;
    font-weight: 600;
    color: #333;
}

.recommendation-card p {
    margin: 0 0 8px 0;
    font-size: 11px;
    color: #666;
    line-height: 1.3;
}

.view-artwork-btn {
    display: inline-block;
    background: #667eea;
    color: white;
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    transition: background-color 0.2s;
}

.view-artwork-btn:hover {
    background: #5a6fd8;
    color: white;
    text-decoration: none;
}

/* Loading Indicator */
.message.loading .message-text {
    background: #f1f3f4;
    padding: 16px;
}

.typing-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #999;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* Input Form */
.chat-input-form {
    padding: 16px 20px;
    border-top: 1px solid #e1e5e9;
    background: #fafbfc;
}

.input-container {
    display: flex;
    gap: 8px;
    align-items: center;
    background: white;
    border: 2px solid #e1e5e9;
    border-radius: 24px;
    padding: 4px;
    transition: border-color 0.2s;
}

.input-container:focus-within {
    border-color: #667eea;
}

.input-container.drag-over {
    border-color: #667eea;
    background: #f8f9ff;
}

.input-container input {
    flex: 1;
    border: none;
    outline: none;
    padding: 12px 16px;
    font-size: 14px;
    background: transparent;
}

.input-container input::placeholder {
    color: #999;
}

.input-container button {
    background: #667eea;
    color: white;
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.2s;
}

.input-container button:hover:not(:disabled) {
    background: #5a6fd8;
}

.input-container button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
    .vividwalls-copilot {
        bottom: 10px;
        right: 10px;
        left: 10px;
    }
    
    .vividwalls-chat-interface {
        width: 100%;
        height: 70vh;
        max-height: 600px;
    }
    
    .copilot-fab {
        width: 100%;
        justify-content: center;
        border-radius: 12px;
    }
    
    .art-recommendations {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .vividwalls-chat-interface {
        height: 80vh;
    }
    
    .messages-container {
        padding: 16px;
    }
    
    .chat-input-form {
        padding: 12px 16px;
    }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .copilot-fab {
        animation: none;
    }
    
    .typing-indicator span {
        animation: none;
    }
    
    * {
        transition: none !important;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .vividwalls-chat-interface {
        border: 2px solid #000;
    }
    
    .message.ai .message-text {
        background: #fff;
        border: 1px solid #000;
    }
    
    .input-container {
        border-color: #000;
    }
}

/* Shopify theme compatibility */
.vividwalls-copilot * {
    box-sizing: border-box;
}

/* Ensure it doesn't interfere with Shopify's existing styles */
.vividwalls-copilot {
    all: initial;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
}`;

async function createMCPRequest(tool, args) {
    return new Promise((resolve, reject) => {
        const server = spawn('node', [SHOPIFY_MCP_SERVER], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let errorOutput = '';

        server.stdout.on('data', (data) => {
            output += data.toString();
        });

        server.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        server.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(output);
                    resolve(result);
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${e.message}`));
                }
            } else {
                reject(new Error(`MCP server failed with code ${code}: ${errorOutput}`));
            }
        });

        const request = {
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/call',
            params: {
                name: tool,
                arguments: args
            }
        };

        server.stdin.write(JSON.stringify(request) + '\n');
        server.stdin.end();
    });
}

async function main() {
    try {
        console.log('🚀 Starting VividWalls CopilotKit integration for Shopify...');

        // Get all themes
        console.log('📋 Getting Shopify themes...');
        const themesResponse = await createMCPRequest('get-themes', {});
        const themes = JSON.parse(themesResponse.content[0].text);
        
        console.log(`Found ${themes.themes.length} themes:`);
        themes.themes.forEach(theme => {
            console.log(`  - ${theme.name} (ID: ${theme.id}) ${theme.role === 'main' ? '[ACTIVE]' : ''}`);
        });

        // Find the active theme
        const activeTheme = themes.themes.find(theme => theme.role === 'main');
        if (!activeTheme) {
            throw new Error('No active theme found');
        }

        console.log(`\n🎨 Working with active theme: ${activeTheme.name} (ID: ${activeTheme.id})`);

        // Get theme assets to understand the structure
        console.log('📁 Getting theme assets...');
        const assetsResponse = await createMCPRequest('get-theme-assets', {
            themeId: activeTheme.id.toString()
        });
        const assets = JSON.parse(assetsResponse.content[0].text);

        // Find theme.liquid
        const themeLiquidAsset = assets.assets.find(asset => asset.key === 'layout/theme.liquid');
        if (!themeLiquidAsset) {
            throw new Error('theme.liquid not found in active theme');
        }

        console.log('📄 Found theme.liquid, getting current content...');

        // Get current theme.liquid content
        const themeContentResponse = await createMCPRequest('get-theme-asset', {
            themeId: activeTheme.id.toString(),
            assetKey: 'layout/theme.liquid'
        });
        const themeContent = JSON.parse(themeContentResponse.content[0].text);
        let currentContent = themeContent.asset.value;

        console.log('✏️  Modifying theme.liquid to include CopilotKit...');

        // Check if already integrated
        if (currentContent.includes('vividwalls-copilot')) {
            console.log('⚠️  VividWalls CopilotKit already appears to be integrated. Updating...');
        }

        // Add CSS to head (before closing </head>)
        const cssInjectPoint = currentContent.indexOf('</head>');
        if (cssInjectPoint === -1) {
            throw new Error('Could not find </head> tag in theme.liquid');
        }

        const cssTag = `
  <!-- VividWalls CopilotKit Styles -->
  <style>
${SHOPIFY_COPILOT_CSS}
  </style>`;

        // Add JavaScript before closing </body>
        const jsInjectPoint = currentContent.indexOf('</body>');
        if (jsInjectPoint === -1) {
            throw new Error('Could not find </body> tag in theme.liquid');
        }

        const jsTag = `
  <!-- VividWalls CopilotKit Integration -->
  <script>
${SHOPIFY_COPILOT_JS}
  </script>`;

        // Remove existing VividWalls integration if present
        currentContent = currentContent.replace(/<!-- VividWalls CopilotKit[\s\S]*?<\/script>/g, '');
        currentContent = currentContent.replace(/<!-- VividWalls CopilotKit[\s\S]*?<\/style>/g, '');

        // Insert new integration
        let updatedContent = currentContent.slice(0, cssInjectPoint) + cssTag + currentContent.slice(cssInjectPoint);
        const newJsInjectPoint = updatedContent.indexOf('</body>');
        updatedContent = updatedContent.slice(0, newJsInjectPoint) + jsTag + updatedContent.slice(newJsInjectPoint);

        // Update theme.liquid
        console.log('💾 Updating theme.liquid with CopilotKit integration...');
        await createMCPRequest('update-theme-asset', {
            themeId: activeTheme.id.toString(),
            assetKey: 'layout/theme.liquid',
            value: updatedContent
        });

        console.log('\n✅ VividWalls CopilotKit integration completed successfully!');
        console.log('\n📋 Integration Summary:');
        console.log(`   🎨 Theme: ${activeTheme.name}`);
        console.log(`   🔗 n8n Webhook: ${N8N_WEBHOOK_URL}`);
        console.log('   📱 Features:');
        console.log('     • Product page AI recommendations');
        console.log('     • Collection browsing assistance');
        console.log('     • Room photo analysis');
        console.log('     • Contextual art suggestions');
        console.log('     • Customer support integration');

        console.log('\n🌐 The VividWalls AI assistant is now live on your Shopify store!');
        console.log('   Customers will see a floating "Get Art Recommendations" button on all pages.');

    } catch (error) {
        console.error('\n❌ Error during integration:', error.message);
        console.error('\n🔧 Troubleshooting:');
        console.error('   • Ensure SHOPIFY_ACCESS_TOKEN and MYSHOPIFY_DOMAIN are set in .env');
        console.error('   • Verify the Shopify app has theme modification permissions');
        console.error('   • Check that the n8n webhook endpoint is accessible');
        process.exit(1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { main as createVividWallsCopilotIntegration };