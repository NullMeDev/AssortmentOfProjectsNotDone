# Project: BH AutoHitter
## Automated Payment Testing Tool with Remote Control

### Project Type
Security Research / Automation Tool

### Status
🟡 In Development

### Technologies Used
- **Frontend:** Chrome Extension (JavaScript, HTML, CSS)
- **Backend:** Python (Telegram Bot), Rust (API)
- **Database:** SQLite
- **Communication:** WebSocket, REST API, Telegram Bot API
- **Encryption:** AES, Fernet

### Components

#### 1. Chrome Extension (`chrome_extension/`)
- Manifest V3 Chrome extension
- Automated form filling and submission
- Payment gateway interaction
- Screenshot capabilities
- Proxy rotation support

#### 2. Telegram Bot (`integration/telegram_bot.py`)
- Remote control interface
- Real-time notifications
- Data management (BINs, proxies)
- Statistics dashboard
- Export functionality

#### 3. Web Integration (`integration/web_api_integration.js`)
- REST API client
- WebSocket connection
- Data synchronization
- Encrypted communication

#### 4. Skybin API (`integration/skybin_bh_api.rs`)
- Rust-based API server
- Data persistence
- WebSocket server
- Authentication system

### Setup Requirements
1. Chrome/Chromium browser
2. Python 3.8+ with virtual environment
3. Telegram Bot Token and User ID
4. (Optional) Rust for API compilation
5. (Optional) Node.js for web integration

### Key Files
- `chrome_extension/manifest.json` - Extension configuration
- `integration/telegram_bot.py` - Main bot script (needs credentials)
- `docs/COMPLETE_SETUP.md` - Full setup instructions
- `integration/requirements.txt` - Python dependencies

### Security Notes
- All sensitive data encrypted
- Single-user authentication via Telegram ID
- Local database storage only
- No external data sharing
- Requires explicit permission for system testing

### Legal Disclaimer
**EDUCATIONAL PURPOSE ONLY**
- For security research on authorized systems
- Use only with test payment cards
- Not for unauthorized access or fraud
- Personal use only, not for distribution

### Quick Start
```bash
# Load extension in Chrome
chrome://extensions → Developer mode → Load unpacked → chrome_extension/

# Run Telegram bot
cd integration
./venv/bin/python telegram_bot.py
```

### Project Structure
```
BH_AutoHitter_Project/
├── chrome_extension/     # Browser extension
├── integration/         # Bot and API integrations  
├── docs/               # Documentation
└── BH.zip             # Original archive
```

### Dependencies Status
- ✅ Python packages installed in `integration/venv/`
- ✅ Chrome extension ready to load
- ⚠️ Requires Telegram credentials configuration
- ⚠️ Optional Rust compilation needed for Skybin API

### TODO
- [ ] Add Telegram credentials
- [ ] Test Chrome extension loading
- [ ] Verify bot connectivity
- [ ] Set up Skybin API (optional)
- [ ] Configure proxies (optional)

### Notes
- Virtual environment already created and packages installed
- Extension extracted and ready for Chrome
- All integration modules created
- Documentation complete

---
*Project organized for storage in AssortmentOfProjectsNotDone repository*