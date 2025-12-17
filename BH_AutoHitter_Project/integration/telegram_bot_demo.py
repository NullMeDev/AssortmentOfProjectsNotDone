#!/usr/bin/env python3
"""
BH AutoHitter Telegram Bot - DEMO VERSION
This demonstrates what the bot interface looks like
"""

import asyncio
from datetime import datetime

# Demo class to show what the bot looks like
class BHTelegramBotDemo:
    def __init__(self):
        self.demo_bins = ["414720", "542418", "455678"]
        self.demo_proxies = ["192.168.1.1:8080", "10.0.0.1:3128"]
        self.demo_hits = [
            ("2024-12-17 01:30:00", "OpenAI", 20.00, "success", "414720", "4242"),
            ("2024-12-17 01:25:00", "Stripe Test", 50.00, "declined", "542418", "0002"),
            ("2024-12-17 01:20:00", "Krea.ai", 15.00, "success", "455678", "3155"),
        ]
    
    def show_main_menu(self):
        print("\n" + "="*50)
        print("🎯 BH AUTOHITTER BOT")
        print("="*50)
        print("\nThis is what your Telegram bot will look like:")
        print("\n📱 MAIN MENU:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("[📊 Dashboard]  [💳 BINs]")
        print("[🌐 Proxies]    [⚙️ Settings]") 
        print("[📜 Hits]       [❓ Help]")
        print("[▶️ Start Hitting] [⏸️ Stop Hitting]")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def show_dashboard(self):
        print("\n📊 DASHBOARD")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n📈 Statistics")
        print(f"• Today's Hits: 15")
        print(f"• Total Hits: 342")
        print(f"• Success: 127")
        print(f"• Success Rate: 37.1%")
        print("\n💳 Resources")
        print(f"• Active BINs: {len(self.demo_bins)}")
        print(f"• Active Proxies: {len(self.demo_proxies)}")
        print(f"\n⏰ Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n[🔄 Refresh] [🔙 Back]")
    
    def show_bins_menu(self):
        print("\n💳 ACTIVE BINS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for i, bin_num in enumerate(self.demo_bins, 1):
            print(f"{i}. {bin_num}")
        print("\n📝 Send BINs (one per line) to add")
        print("\n[🗑️ Clear All] [🔙 Back]")
    
    def show_proxies_menu(self):
        print("\n🌐 ACTIVE PROXIES")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for i, proxy in enumerate(self.demo_proxies, 1):
            masked = proxy[:10] + "..." if len(proxy) > 10 else proxy
            print(f"{i}. {masked} (✅5/❌2)")
        print("\n📝 Send proxies (format: host:port)")
        print("\n[🗑️ Clear All] [🔙 Back]")
    
    def show_recent_hits(self):
        print("\n📜 RECENT HITS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for timestamp, merchant, amount, result, bin_num, last4 in self.demo_hits:
            emoji = "✅" if result == "success" else "❌"
            print(f"\n{emoji} {merchant} - ${amount}")
            print(f"   {bin_num}****{last4}")
            print(f"   {timestamp}")
        print("\n[📤 Export] [🗑️ Clear] [🔙 Back]")
    
    def show_hit_notification(self):
        print("\n" + "="*50)
        print("🔔 NEW HIT NOTIFICATION")
        print("="*50)
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
    
    def show_settings(self):
        print("\n⚙️ SETTINGS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n🔔 Notifications")
        print("• Send Hits to Telegram: ✅ Enabled")
        print("• Auto Screenshot: ✅ Enabled")
        print("• Sound Alerts: ❌ Disabled")
        print("\n🔒 Security")
        print("• Max Hits/Day: 100")
        print("• Cooldown: 30s")
        print("• Blur Sensitive Info: ✅ Enabled")
        print("\n[💾 Save] [🔙 Back]")
    
    def show_start_hitting(self):
        print("\n▶️ STARTING AUTOHITTER...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\nThe Chrome extension will begin hitting with:")
        print(f"• {len(self.demo_bins)} configured BINs")
        print(f"• {len(self.demo_proxies)} active proxies")
        print("\nYou'll receive notifications for successful hits.")
        print("\nStatus: 🟢 ACTIVE")
    
    def run_demo(self):
        print("\n" + "="*60)
        print(" BH AUTOHITTER TELEGRAM BOT - INTERFACE DEMO")
        print("="*60)
        print("\nThis demo shows what your Telegram bot interface will look like.")
        print("In the actual bot, these will be interactive buttons in Telegram.\n")
        
        while True:
            print("\n" + "-"*50)
            print("SELECT DEMO OPTION:")
            print("1. Main Menu")
            print("2. Dashboard") 
            print("3. BINs Management")
            print("4. Proxies Management")
            print("5. Recent Hits")
            print("6. Settings")
            print("7. Start Hitting")
            print("8. Show Hit Notification")
            print("0. Exit Demo")
            print("-"*50)
            
            choice = input("\nEnter option (0-8): ")
            
            if choice == "1":
                self.show_main_menu()
            elif choice == "2":
                self.show_dashboard()
            elif choice == "3":
                self.show_bins_menu()
            elif choice == "4":
                self.show_proxies_menu()
            elif choice == "5":
                self.show_recent_hits()
            elif choice == "6":
                self.show_settings()
            elif choice == "7":
                self.show_start_hitting()
            elif choice == "8":
                self.show_hit_notification()
            elif choice == "0":
                print("\nExiting demo...")
                break
            else:
                print("Invalid option. Please try again.")
            
            if choice != "0":
                input("\nPress Enter to continue...")

def show_setup_instructions():
    print("\n" + "="*60)
    print(" HOW TO GET YOUR TELEGRAM BOT TOKEN")
    print("="*60)
    print("""
1. GETTING BOT TOKEN:
   • Open Telegram and search for @BotFather
   • Send /newbot to create a new bot
   • Choose a name (e.g., "BH AutoHitter")
   • Choose a username (must end in 'bot', e.g., "BHAutoHitter_bot")
   • BotFather will give you a token like:
     1234567890:ABCdefGHIjklmNOPqrstUVWxyz123456789
   • Save this token securely!

2. GETTING YOUR USER ID:
   • Search for @userinfobot or @RawDataBot
   • Start a chat and it will show your ID
   • It will be a number like: 123456789

3. CONFIGURING THE BOT:
   • Edit telegram_bot.py
   • Replace BOT_TOKEN with your actual token
   • Replace YOUR_TELEGRAM_ID with your user ID
   • Run: python3 telegram_bot.py

4. SECURITY TIPS:
   • NEVER share your bot token publicly
   • Only use your personal Telegram ID
   • Keep the bot private (don't add to groups)
   • Use a VPN when running the bot
    """)

if __name__ == "__main__":
    print("\n🎯 BH AUTOHITTER TELEGRAM BOT - DEMO VERSION")
    print("="*60)
    
    print("\nOptions:")
    print("1. Show interface demo")
    print("2. Show setup instructions")
    
    choice = input("\nSelect option (1-2): ")
    
    if choice == "1":
        demo = BHTelegramBotDemo()
        demo.run_demo()
    elif choice == "2":
        show_setup_instructions()
    else:
        print("Invalid option. Showing setup instructions...")
        show_setup_instructions()