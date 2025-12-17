# Telegram BIN Scraper Bot

## Project Status
**Status**: In Development  
**Created**: December 2024  
**Language**: Rust  
**Purpose**: Stealth Telegram bot for monitoring groups and detecting payment card information

## Description
A sophisticated Telegram bot that operates stealthily to monitor specified groups for BINs (Bank Identification Numbers), credit card information, and related data. The bot validates detected cards using the Luhn algorithm and posts findings to a designated channel.

## Key Features
- 🔍 Advanced pattern detection for cards, CVVs, expiry dates, PINs
- ✅ Luhn algorithm validation
- 🏦 Automatic brand detection (Visa, MasterCard, AmEx, etc.)
- 🥷 Three stealth modes (Ghost, Normal, Aggressive)
- 📊 Confidence scoring system
- 🚫 Deduplication to avoid reposting
- 📄 File processing (txt, csv, log attachments)
- 💎 High-value card filtering

## Architecture
```
telegram-bin-scraper/
├── src/
│   ├── bin_detector.rs    # Card detection and validation
│   ├── telegram.rs        # Telegram client and monitoring
│   ├── formatter.rs       # Output formatting (Clean/Detailed/Stealth)
│   ├── stealth.rs         # Anti-detection mechanisms
│   ├── config.rs          # Configuration management
│   └── main.rs           # Entry point
├── Cargo.toml            # Rust dependencies
├── config.toml.example   # Sample configuration
└── README.md            # Setup instructions
```

## Technologies Used
- **Rust** - Core implementation
- **grammers** - Telegram client library
- **tokio** - Async runtime
- **regex** - Pattern matching
- **luhn** - Card validation
- **chrono** - Time handling
- **serde/toml** - Configuration

## Setup Requirements
1. Telegram API credentials from https://my.telegram.org
2. Target channel ID for posting findings
3. Group IDs to monitor
4. Rust toolchain installed

## Configuration
Supports both TOML file and environment variable configuration:
- API credentials
- Stealth level (Ghost/Normal/Aggressive)
- Post style (Clean/Detailed/Stealth)
- Detection thresholds
- Deduplication window

## Security Features
- Human behavior simulation (reading, typing, scrolling)
- Rate limiting to avoid detection
- Random delays and presence patterns
- Multiple user agent rotation
- Session persistence

## Related Components
This project was originally part of the SkyBin credential scraping system but has been separated for focused development.

## Notes
- Educational purposes only
- Requires compliance with local laws and Telegram ToS
- Not for commercial use