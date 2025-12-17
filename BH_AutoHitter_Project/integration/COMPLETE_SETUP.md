# 📍 COMPLETE BH AUTOHITTER SETUP - FILE LOCATIONS & INSTRUCTIONS

## 📂 Directory Structure & File Locations

```
/home/null/Desktop/Carding/
│
├── BH.zip                    ← Original Chrome extension archive
│
├── BH_extracted/             ← Chrome extension files (READY TO USE)
│   ├── manifest.json         ← Extension configuration
│   ├── settings.html         ← Extension dashboard
│   ├── scripts/              ← All extension scripts
│   ├── assets/               ← Images, styles, sounds
│   └── models/               ← ML models for detection
│
└── BH_Integration/           ← Your integration files (NEW)
    ├── telegram_bot.py       ← Main Telegram bot (EDIT THIS)
    ├── web_api_integration.js ← Web integration for Skybin
    ├── skybin_bh_api.rs      ← Rust API for Skybin
    ├── requirements.txt       ← Python dependencies
    ├── venv/                  ← Python virtual environment (INSTALLED)
    └── SETUP_GUIDE.md         ← Setup documentation
```

---

## 🚀 QUICK START - STEP BY STEP

### 1️⃣ Install Chrome Extension

```bash
# The extension is already extracted and ready!
# Location: /home/null/Desktop/Carding/BH_extracted/

1. Open Chrome
2. Go to: chrome://extensions/
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select folder: /home/null/Desktop/Carding/BH_extracted/
6. Extension will appear in Chrome!
```

### 2️⃣ Get Your Telegram Credentials

#### A. Create Bot Token:
```
1. Open Telegram app
2. Search: @BotFather
3. Send: /newbot
4. Name it: BH AutoHitter
5. Username: YourName_BHAutoHitter_bot
6. Copy the token: 1234567890:ABCdef...
```

#### B. Get Your User ID:
```
1. Search: @userinfobot
2. Start chat
3. Copy your ID: 123456789
```

### 3️⃣ Configure Telegram Bot

```bash
# Edit the bot configuration
cd /home/null/Desktop/Carding/BH_Integration
nano telegram_bot.py

# Go to the bottom (line 501-502) and update:
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with token from BotFather
YOUR_TELEGRAM_ID = 123456789       # Replace with your user ID

# Save and exit: Ctrl+X, Y, Enter
```

### 4️⃣ Run the Telegram Bot

```bash
# Navigate to integration folder
cd /home/null/Desktop/Carding/BH_Integration

# Run the bot using virtual environment
./venv/bin/python telegram_bot.py
```

### 5️⃣ Test Your Bot

```
1. Open Telegram
2. Search for your bot username
3. Send: /start
4. You should see the menu!
```

---

## 📝 CONFIGURATION FILES TO EDIT

### File 1: Telegram Bot Configuration
**Location:** `/home/null/Desktop/Carding/BH_Integration/telegram_bot.py`
```python
# Line 501-502 - Edit these:
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
YOUR_TELEGRAM_ID = 123456789
```

### File 2: Web Integration (Optional)
**Location:** `/home/null/Desktop/Carding/BH_Integration/web_api_integration.js`
```javascript
// Line 10 - Edit if needed:
this.baseUrl = 'https://nullme.lol';
```

### File 3: Create Config File (Optional)
**Create:** `/home/null/Desktop/Carding/BH_Integration/config.json`
```json
{
    "telegram": {
        "botToken": "YOUR_BOT_TOKEN",
        "userId": YOUR_USER_ID
    },
    "skybin": {
        "url": "https://nullme.lol",
        "authToken": "bh_YOUR_SECURE_TOKEN"
    }
}
```

---

## 🔧 COMMANDS CHEATSHEET

```bash
# Navigate to integration folder
cd /home/null/Desktop/Carding/BH_Integration

# Edit bot configuration
nano telegram_bot.py

# Run the bot
./venv/bin/python telegram_bot.py

# Stop the bot
Ctrl + C

# Run bot in background
nohup ./venv/bin/python telegram_bot.py &

# Check if bot is running
ps aux | grep telegram_bot

# View bot logs
tail -f nohup.out

# Install additional packages (if needed)
./venv/bin/pip install package_name
```

---

## 🎯 CHROME EXTENSION USAGE

### After Loading Extension:
1. Click extension icon in Chrome toolbar
2. Or go to any Stripe checkout page
3. Extension dashboard opens automatically
4. Configure:
   - Add BINs (Card numbers to test)
   - Add proxies (optional)
   - Set email
   - Configure Telegram integration

### Settings Page:
```
chrome-extension://[EXTENSION_ID]/settings.html
```
*Replace [EXTENSION_ID] with actual ID shown in chrome://extensions*

---

## 🔐 SECURITY CHECKLIST

- [ ] Bot token saved securely (not in public repos)
- [ ] Your Telegram ID configured correctly  
- [ ] VPN enabled when running
- [ ] Extension loaded in incognito mode
- [ ] Using test cards only (4242424242424242)
- [ ] Not sharing configuration files
- [ ] Database files kept private

---

## 📱 TELEGRAM BOT FEATURES

Once running, your bot can:
- 📊 Show dashboard with statistics
- 💳 Manage BINs remotely
- 🌐 Manage proxies
- 📜 View hit history
- 📤 Export data as JSON/CSV
- 🔔 Send real-time notifications
- ▶️ Start/stop hitting remotely

---

## 🆘 TROUBLESHOOTING

### Bot not responding:
```bash
# Check if running
ps aux | grep telegram_bot

# Check for errors
./venv/bin/python telegram_bot.py
```

### Extension not loading:
```
1. Check Developer mode is ON
2. Verify folder path is correct
3. Check Chrome console for errors (F12)
```

### Permission errors:
```bash
# Make scripts executable
chmod +x /home/null/Desktop/Carding/BH_Integration/*.py
```

---

## 📁 DATABASE LOCATION

The bot creates a local database:
```
/home/null/Desktop/Carding/BH_Integration/bh_bot.db
```

This stores:
- Hit history
- BINs list
- Proxies list
- Settings

---

## 🎬 STARTUP SEQUENCE

1. **Start VPN** (recommended)
2. **Load Chrome Extension**
   - chrome://extensions
   - Load unpacked: BH_extracted folder
3. **Start Telegram Bot**
   ```bash
   cd /home/null/Desktop/Carding/BH_Integration
   ./venv/bin/python telegram_bot.py
   ```
4. **Open Telegram**
   - Find your bot
   - Send /start
5. **Configure via Telegram**
   - Add BINs
   - Add proxies
   - Start hitting

---

## ⚡ QUICK COMMANDS

```bash
# One-liner to start bot
cd /home/null/Desktop/Carding/BH_Integration && ./venv/bin/python telegram_bot.py

# Run in background
cd /home/null/Desktop/Carding/BH_Integration && nohup ./venv/bin/python telegram_bot.py > bot.log 2>&1 &

# View logs
tail -f /home/null/Desktop/Carding/BH_Integration/bot.log
```

---

## 📞 SUPPORT RESOURCES

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Chrome Extensions:** https://developer.chrome.com/docs/extensions/
- **Python Telegram Bot:** https://python-telegram-bot.org/

---

Remember: This is for PERSONAL EDUCATIONAL USE ONLY!
Always use test cards and your own test systems.