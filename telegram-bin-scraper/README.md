# BIN Scraper Bot 🥷

A stealthy Telegram bot that monitors groups for BINs, credit card info, and fullz data, then posts findings to your private channel.

## Features

- 🔍 **Advanced BIN Detection**: Detects cards, CVVs, expiry dates, PINs, and fullz format
- ✅ **Luhn Validation**: Validates card numbers using Luhn algorithm
- 🏦 **Brand Detection**: Identifies Visa, MasterCard, AmEx, Discover, etc.
- 🥷 **Stealth Mode**: Three levels of stealth to avoid detection
- 🚫 **Deduplication**: Avoids reposting the same BINs
- 📊 **Confidence Scoring**: Rates detected cards by confidence level
- 📄 **File Processing**: Scans text files, CSVs, and logs in messages

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 2. Configure the Bot

Copy the example config:
```bash
cp config.toml.example config.toml
# OR use environment variables
cp .env.example .env
```

Edit the config with your details:
- Telegram API credentials
- Your phone number
- Target channel ID (where BINs will be posted)
- Group IDs to monitor

### 3. Get Channel/Group IDs

To get IDs:
1. Add @userinfobot to your channel/group
2. It will show the ID
3. Remove the bot after getting the ID

### 4. Build and Run

```bash
# Build
cargo build --release

# Run with config file
./target/release/bin-scraper

# Or run with environment variables
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=your_hash
# ... set other vars
./target/release/bin-scraper
```

## Configuration Options

### Stealth Levels
- **Ghost**: Ultra-stealth, very slow actions, maximum delays
- **Normal**: Balanced between speed and stealth
- **Aggressive**: Faster but higher risk of detection

### Post Styles
- **Clean**: Minimal formatting, organized by brand
- **Detailed**: Full card info with confidence stars
- **Stealth**: Looks like casual message

### Detection Settings
- `min_confidence`: Minimum confidence score (0.0-1.0)
- `only_high_value`: Only post premium cards (Gold, Platinum, etc.)
- `dedupe_hours`: Remember cards for X hours to avoid duplicates

## Output Examples

### Clean Style
```
💳 Fresh Drop | 5 cards
━━━━━━━━━━━━━━━━
Visa (3)
4532015112830366 | 08/25 | 737
  └─ John Doe, 123 Main St
MasterCard (2)  
5425233430109903 | 04/26 | 222
━━━━━━━━━━━━━━━━
Source: Group Name
Time: 14:32 UTC
```

### Detailed Style
```
🔥 NEW DROP ALERT 🔥
═══════════════════
#1 💳 Visa [⭐⭐⭐⭐⭐]
├─ Number: 4532015112830366
├─ Exp: 08/25
├─ CVV: 737
├─ Fullz: John Doe, 123 Main St
└─ Valid: ✅ | Type: Credit
```

### Stealth Style
```
found these

4532015112830366 08/25 737
5425233430109903 04/26 222
+ 3 more
```

## Safety Tips

1. Use a separate Telegram account for the bot
2. Start with Ghost mode to test
3. Monitor fewer groups initially
4. Use a VPN/proxy if needed
5. Don't join/leave groups rapidly

## Troubleshooting

- **Session expired**: Delete `bin_scraper.session` and re-authenticate
- **Rate limiting**: Switch to Ghost mode or reduce monitored groups
- **Not finding BINs**: Check min_confidence setting, lower if needed
- **Duplicate posts**: Increase dedupe_hours

## Legal Notice

This tool is for educational purposes only. Ensure you comply with all applicable laws and Telegram's Terms of Service. The authors are not responsible for any misuse.