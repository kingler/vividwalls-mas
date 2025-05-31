/**
 * VividWalls CopilotKit WordPress Integration
 * Handles the React component rendering and n8n workflow communication
 */

(function() {
    'use strict';

    // Wait for DOM and React to be ready
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof React === 'undefined' || typeof ReactDOM === 'undefined') {
            console.error('React is not loaded. CopilotKit cannot initialize.');
            return;
        }

        // Initialize CopilotKit components
        initializeCopilotKit();
    });

    function initializeCopilotKit() {
        const { useState, useEffect, useCallback } = React;

        // VividWalls AI Assistant Component
        const VividWallsAssistant = () => {
            const [isOpen, setIsOpen] = useState(false);
            const [messages, setMessages] = useState([]);
            const [isLoading, setIsLoading] = useState(false);
            const [sessionId] = useState(() => 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9));

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

            // Send message to n8n workflow via WordPress AJAX
            const sendMessage = useCallback(async (message, imageData = null) => {
                setIsLoading(true);
                
                try {
                    const formData = new FormData();
                    formData.append('action', 'copilot_proxy');
                    formData.append('nonce', vividwalls_ajax.nonce);
                    formData.append('chatInput', message);
                    formData.append('sessionId', sessionId);
                    formData.append('page_url', window.location.href);
                    
                    if (imageData) {
                        formData.append('imageData', imageData);
                    }

                    const response = await fetch(vividwalls_ajax.ajax_url, {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        return result.data;
                    } else {
                        throw new Error(result.data || 'Failed to get response');
                    }
                } catch (error) {
                    console.error('Error sending message:', error);
                    return {
                        response: 'Sorry, I encountered an error. Please try again.',
                        error: true
                    };
                } finally {
                    setIsLoading(false);
                }
            }, [sessionId]);

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
                        text: response.response || response,
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
                            text: response.response || response,
                            sender: 'ai',
                            timestamp: new Date(),
                            recommendations: response.recommendations || null,
                            visualizations: response.visualizations || null
                        };

                        setMessages(prev => [...prev, aiMessage]);
                    }
                };

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
                            onClick: () => setIsOpen(false)
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
                            React.createElement('p', { key: 'text' }, 'Hi! I\'m your VividWalls AI assistant. I can help you:'),
                            React.createElement('ul', { key: 'list' }, [
                                React.createElement('li', { key: '1' }, '🎨 Find perfect artwork for your space'),
                                React.createElement('li', { key: '2' }, '📸 Analyze room photos for art recommendations'),
                                React.createElement('li', { key: '3' }, '💡 Answer questions about our collections'),
                                React.createElement('li', { key: '4' }, '📏 Help with sizing and customization')
                            ]),
                            React.createElement('p', { key: 'prompt' }, 'Try asking: "What artwork would work in a modern living room?" or drag & drop a photo of your space!')
                        ]),

                        // Message list
                        ...messages.map(message => 
                            React.createElement('div', {
                                key: message.id,
                                className: `message ${message.sender}`
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
                                            alt: rec.title
                                        }),
                                        React.createElement('h4', { key: 'title' }, rec.title),
                                        React.createElement('p', { key: 'desc' }, rec.description),
                                        React.createElement('a', {
                                            key: 'link',
                                            href: rec.url,
                                            className: 'view-artwork-btn',
                                            target: '_blank'
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
                            className: `input-container ${dragOver ? 'drag-over' : ''}`
                        }, [
                            React.createElement('input', {
                                key: 'input',
                                type: 'text',
                                value: inputValue,
                                onChange: (e) => setInputValue(e.target.value),
                                placeholder: 'Ask about artwork or drag & drop a room photo...',
                                disabled: isLoading
                            }),
                            React.createElement('button', {
                                key: 'submit',
                                type: 'submit',
                                disabled: !inputValue.trim() || isLoading
                            }, '→')
                        ])
                    ])
                ]);
            };

            return React.createElement('div', {
                className: `vividwalls-copilot ${isOpen ? 'open' : ''}`
            }, [
                // Floating Action Button
                !isOpen && React.createElement('button', {
                    key: 'fab',
                    className: 'copilot-fab',
                    onClick: () => setIsOpen(true)
                }, [
                    React.createElement('span', { key: 'icon' }, '🎨'),
                    React.createElement('span', { key: 'text' }, 'Get Art Recommendations')
                ]),

                // Chat Interface
                isOpen && React.createElement(ChatInterface, { key: 'chat' })
            ]);
        };

        // Render the main component
        const container = document.getElementById('vividwalls-copilot-container');
        if (container) {
            ReactDOM.render(React.createElement(VividWallsAssistant), container);
        }

        // Handle shortcode embeds
        const embeds = document.querySelectorAll('.vividwalls-copilot-embed');
        embeds.forEach(embed => {
            const mode = embed.dataset.mode || 'chat';
            const triggerText = embed.dataset.trigger || 'Ask about art recommendations';
            const position = embed.dataset.position || 'bottom-right';

            if (mode === 'popup') {
                ReactDOM.render(
                    React.createElement('button', {
                        className: 'vividwalls-trigger-btn',
                        onClick: () => {
                            const modal = document.createElement('div');
                            modal.className = 'vividwalls-modal';
                            modal.innerHTML = '<div class="modal-content"><div id="modal-copilot"></div></div>';
                            document.body.appendChild(modal);
                            
                            ReactDOM.render(React.createElement(VividWallsAssistant), modal.querySelector('#modal-copilot'));
                            
                            modal.addEventListener('click', (e) => {
                                if (e.target === modal) {
                                    document.body.removeChild(modal);
                                }
                            });
                        }
                    }, triggerText),
                    embed
                );
            } else {
                ReactDOM.render(React.createElement(VividWallsAssistant), embed);
            }
        });
    }

    // Utility function to generate session ID
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

})(); 