#!/usr/bin/env python3
"""
BH AutoHitter Telegram Bot - Visual Demo
Shows what your Telegram bot will look like
"""

from datetime import datetime

print("\n" + "="*70)
print(" 🎯 BH AUTOHITTER TELEGRAM BOT - VISUAL DEMONSTRATION")
print("="*70)

print("""
╔══════════════════════════════════════════════════════════════════╗
║                    HOW TO GET YOUR BOT TOKEN                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. Open Telegram and search for: @BotFather                     ║
║  2. Send this command: /newbot                                    ║
║  3. Choose a name: "BH AutoHitter"                               ║
║  4. Choose username: "YourName_BHAutoHitter_bot"                 ║
║  5. You'll receive a token like:                                 ║
║     1234567890:ABCdefGHIjklmNOPqrstUVWxyz123456789              ║
║                                                                    ║
║  TO GET YOUR USER ID:                                            ║
║  • Search for @userinfobot or @RawDataBot                        ║
║  • Start a chat - it will show your ID                           ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════╝
""")

print("\n" + "="*70)
print(" WHAT YOUR BOT WILL LOOK LIKE IN TELEGRAM:")
print("="*70)

# Main Menu
print("""
┌─────────────────────────────────┐
│  🎯 BH AUTOHITTER BOT           │
├─────────────────────────────────┤
│  Personal control panel         │
│                                 │
│  ┌───────────┬───────────┐     │
│  │📊Dashboard│ 💳 BINs   │     │
│  ├───────────┼───────────┤     │
│  │🌐 Proxies │⚙️Settings │     │
│  ├───────────┼───────────┤     │
│  │ 📜 Hits   │ ❓ Help   │     │
│  ├───────────┴───────────┤     │
│  │   ▶️ START HITTING    │     │
│  ├───────────────────────┤     │
│  │   ⏸️ STOP HITTING     │     │
│  └───────────────────────┘     │
└─────────────────────────────────┘
""")

# Dashboard View
print("\n📊 DASHBOARD VIEW:")
print("-"*40)
print(f"""
📈 Statistics
• Today's Hits: 15
• Total Hits: 342  
• Success: 127
• Success Rate: 37.1%

💳 Resources
• Active BINs: 3
• Active Proxies: 2

⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}

[🔄 Refresh] [🔙 Back]
""")

# BINs Management
print("\n💳 BINS MANAGEMENT:")
print("-"*40)
print("""
Active BINs:
1. 414720 (Visa)
2. 542418 (Mastercard)  
3. 455678 (Visa)

📝 To add BINs, send them as text:
"414720
 542418
 455678"

[🗑️ Clear All] [🔙 Back]
""")

# Recent Hits
print("\n📜 RECENT HITS:")
print("-"*40)
print("""
✅ OpenAI - $20.00
   414720****4242
   2024-12-17 01:30:00

❌ Stripe Test - $50.00
   542418****0002
   2024-12-17 01:25:00

✅ Krea.ai - $15.00
   455678****3155
   2024-12-17 01:20:00

[📤 Export] [🗑️ Clear] [🔙 Back]
""")

# Hit Notification
print("\n🔔 HIT NOTIFICATION (You'll receive this in Telegram):")
print("-"*40)
print("""
✅ NEW HIT
━━━━━━━━━━━━━━━━━

💳 Card: 414720****4242
📅 Exp: 09/29
🏪 Merchant: OpenAI Plus
💵 Amount: $20.00
📊 Result: SUCCESS
📝 Message: Payment successful
🌐 Proxy: 192.168.1.1:8080
⏰ Time: 01:35:42
""")

print("\n" + "="*70)
print(" HOW TO RUN THE ACTUAL BOT:")
print("="*70)
print("""
1. Edit telegram_bot.py:
   BOT_TOKEN = "YOUR_ACTUAL_TOKEN"
   YOUR_TELEGRAM_ID = 123456789  # Your actual ID

2. Run the bot:
   cd /home/null/Desktop/Carding/BH_Integration
   ./venv/bin/python telegram_bot.py

3. Open Telegram and search for your bot
4. Send /start to begin
5. Use the inline buttons to navigate

SECURITY TIPS:
• Only you can use the bot (checks your Telegram ID)
• All data is encrypted
• Use a VPN when running
• Keep your token secret
""")

print("\n" + "="*70)
print(" Bot features:")
print("="*70)
print("""
✅ Real-time hit notifications in Telegram
✅ Remote control of Chrome extension
✅ BIN and proxy management via chat
✅ Export hits as JSON/CSV
✅ Dashboard with statistics
✅ Secure - only your Telegram ID can access
✅ SQLite database for persistence
✅ WebSocket connection to Skybin
""")

print("\n✨ Ready to set up your bot? Follow the instructions above!")
print("="*70)