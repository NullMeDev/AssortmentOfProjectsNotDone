# BH AutoHitter Project
## Automated Payment Testing Tool with Telegram Integration

⚠️ **EDUCATIONAL PURPOSE ONLY** - For personal security research and testing on authorized systems.

## 📁 Project Structure

```
BH_AutoHitter_Project/
├── chrome_extension/        # Chrome extension (BH AutoHitter)
│   ├── manifest.json       # Extension configuration
│   ├── settings.html       # Dashboard interface
│   ├── scripts/           # Core functionality scripts
│   ├── assets/           # Images, styles, sounds
│   └── models/          # ML models for detection
│
├── integration/           # External integrations
│   ├── telegram_bot.py   # Telegram bot for remote control
│   ├── web_api_integration.js  # Web API integration
│   ├── skybin_bh_api.rs  # Rust API for Skybin
│   ├── requirements.txt  # Python dependencies
│   └── venv/            # Python virtual environment
│
├── docs/                # Documentation
│   ├── SETUP_GUIDE.md   # Complete setup instructions
│   ├── API_DOCS.md      # API documentation
│   └── SECURITY.md      # Security guidelines
│
└── BH.zip              # Original extension archive
```

## 🚀 Quick Start

### Prerequisites
- Chrome/Chromium browser
- Python 3.8+
- Telegram account
- Node.js (optional, for web integration)
- Rust (optional, for Skybin integration)

### Installation

1. **Load Chrome Extension:**
   ```bash
   Chrome → chrome://extensions → Developer mode → Load unpacked → Select `chrome_extension` folder
   ```

2. **Setup Telegram Bot:**
   ```bash
   cd integration
   # Edit telegram_bot.py with your credentials
   ./venv/bin/python telegram_bot.py
   ```

## 🔑 Features

### Chrome Extension
- ✅ Automated form filling for payment testing
- ✅ BIN management system
- ✅ Proxy rotation support
- ✅ Hit logging and analytics
- ✅ Screenshot capabilities
- ✅ Real-time notifications

### Telegram Bot Integration
- 📊 Remote dashboard access
- 💳 BIN management via chat
- 🌐 Proxy configuration
- 📜 Hit history and exports
- 🔔 Real-time notifications
- ⚙️ Remote control capabilities

### Web Integration
- 🌐 REST API endpoints
- 🔄 WebSocket real-time updates
- 📝 Automatic paste creation
- 🔐 Encrypted data transmission
- 📊 Analytics dashboard

## 📖 Documentation

- [Complete Setup Guide](docs/SETUP_GUIDE.md)
- [API Documentation](docs/API_DOCS.md)
- [Security Guidelines](docs/SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## ⚠️ Legal Notice

This tool is for **educational and security research purposes only**. 

**Never use for:**
- Unauthorized payment testing
- Credit card fraud
- Violating terms of service
- Commercial purposes

**Only use:**
- On systems you own or have permission to test
- With test payment cards (e.g., Stripe test cards)
- In compliance with all applicable laws

## 🔒 Security

- All sensitive data is encrypted
- Telegram bot restricted to single user ID
- Local database storage
- No external data sharing
- VPN recommended during use

## 🛠️ Configuration

### Telegram Bot Setup
1. Get token from @BotFather
2. Get your ID from @userinfobot
3. Update `integration/telegram_bot.py`:
   ```python
   BOT_TOKEN = "your_token_here"
   YOUR_TELEGRAM_ID = your_id_here
   ```

### Chrome Extension Config
Access dashboard at: `chrome-extension://[EXTENSION_ID]/settings.html`

## 📦 Dependencies

### Python (Telegram Bot)
- python-telegram-bot>=20.0
- cryptography>=41.0.0
- aiosqlite
- aiohttp>=3.8.0

### JavaScript (Chrome Extension)
- Chrome Extensions API
- WebSocket API
- Crypto-JS for encryption

### Rust (Skybin API)
- actix-web
- sqlx
- tokio
- serde

## 🤝 Contributing

This is a personal research project. Not accepting external contributions.

## 📄 License

Personal use only. Not for distribution or commercial use.

## ⚡ Quick Commands

```bash
# Start Telegram bot
cd integration && ./venv/bin/python telegram_bot.py

# Run in background
nohup ./venv/bin/python telegram_bot.py > bot.log 2>&1 &

# View logs
tail -f integration/bot.log

# Stop bot
pkill -f telegram_bot.py
```

## 📞 Support

This is a personal project. Use at your own risk.

---

**Remember:** Always use responsibly and legally. Test only on authorized systems with test data.