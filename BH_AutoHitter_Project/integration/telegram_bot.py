#!/usr/bin/env python3
"""
BH AutoHitter Telegram Bot Integration
For personal use only - NOT for commercial purposes

This bot allows you to control and monitor BH AutoHitter via Telegram
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from cryptography.fernet import Fernet
import sqlite3

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BHTelegramBot:
    def __init__(self, token: str, user_id: int):
        """
        Initialize the BH Telegram Bot
        
        Args:
            token: Telegram bot token
            user_id: Your personal Telegram user ID for security
        """
        self.token = token
        self.authorized_user = user_id
        self.skybin_url = "https://nullme.lol"
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.db_path = "bh_bot.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing hits and settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                merchant TEXT,
                amount REAL,
                bin TEXT,
                last4 TEXT,
                result TEXT,
                message TEXT,
                proxy TEXT,
                data TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bin TEXT UNIQUE,
                active INTEGER DEFAULT 1,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE,
                active INTEGER DEFAULT 1,
                last_used DATETIME,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id == self.authorized_user

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized access")
            return
            
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data='dashboard')],
            [InlineKeyboardButton("💳 BINs", callback_data='bins'), 
             InlineKeyboardButton("🌐 Proxies", callback_data='proxies')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
             InlineKeyboardButton("📜 Hits", callback_data='hits')],
            [InlineKeyboardButton("▶️ Start Hitting", callback_data='start_hitting'),
             InlineKeyboardButton("⏸️ Stop Hitting", callback_data='stop_hitting')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *BH AutoHitter Bot*\n"
            "━━━━━━━━━━━━━━━━━\n"
            "Personal control panel for BH AutoHitter\n\n"
            "Select an option:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show dashboard with statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM hits WHERE date(timestamp) = date('now')")
        today_hits = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hits WHERE result = 'success'")
        success_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hits")
        total_hits = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bins WHERE active = 1")
        active_bins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM proxies WHERE active = 1")
        active_proxies = cursor.fetchone()[0]
        
        conn.close()
        
        success_rate = (success_count / total_hits * 100) if total_hits > 0 else 0
        
        dashboard_text = f"""
📊 *DASHBOARD*
━━━━━━━━━━━━━━━━━

📈 *Statistics*
• Today's Hits: {today_hits}
• Total Hits: {total_hits}
• Success: {success_count}
• Success Rate: {success_rate:.1f}%

💳 *Resources*
• Active BINs: {active_bins}
• Active Proxies: {active_proxies}

⏰ *Last Update*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data='dashboard')],
                    [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                dashboard_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                dashboard_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

    async def manage_bins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage BINs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT bin FROM bins WHERE active = 1 LIMIT 10")
        bins = cursor.fetchall()
        conn.close()
        
        bins_text = "💳 *Active BINs*\n━━━━━━━━━━━━━━━━━\n\n"
        if bins:
            for i, (bin_num,) in enumerate(bins, 1):
                bins_text += f"{i}. `{bin_num}`\n"
        else:
            bins_text += "No active BINs configured"
        
        bins_text += "\n📝 Send BINs (one per line) to add"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Clear All", callback_data='clear_bins')],
            [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            bins_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Set state to expect BINs input
        context.user_data['expecting'] = 'bins'

    async def manage_proxies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage proxies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT proxy, success_count, fail_count 
            FROM proxies WHERE active = 1 LIMIT 10
        """)
        proxies = cursor.fetchall()
        conn.close()
        
        proxies_text = "🌐 *Active Proxies*\n━━━━━━━━━━━━━━━━━\n\n"
        if proxies:
            for i, (proxy, success, fail) in enumerate(proxies, 1):
                # Mask proxy for security
                masked_proxy = proxy[:10] + "..." if len(proxy) > 10 else proxy
                proxies_text += f"{i}. `{masked_proxy}` (✅{success}/❌{fail})\n"
        else:
            proxies_text += "No active proxies configured"
        
        proxies_text += "\n📝 Send proxies (format: host:port or user:pass@host:port)"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Clear All", callback_data='clear_proxies')],
            [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            proxies_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Set state to expect proxies input
        context.user_data['expecting'] = 'proxies'

    async def show_hits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent hits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, merchant, amount, result, bin, last4
            FROM hits 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        hits = cursor.fetchall()
        conn.close()
        
        hits_text = "📜 *Recent Hits*\n━━━━━━━━━━━━━━━━━\n\n"
        if hits:
            for hit in hits:
                timestamp, merchant, amount, result, bin_num, last4 = hit
                emoji = "✅" if result == "success" else "❌"
                hits_text += f"{emoji} {merchant} - ${amount}\n"
                hits_text += f"   {bin_num}****{last4}\n"
                hits_text += f"   {timestamp}\n\n"
        else:
            hits_text += "No hits recorded yet"
        
        keyboard = [
            [InlineKeyboardButton("📤 Export", callback_data='export_hits')],
            [InlineKeyboardButton("🗑️ Clear", callback_data='clear_hits')],
            [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            hits_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages based on context"""
        if not self.is_authorized(update.effective_user.id):
            return
        
        expecting = context.user_data.get('expecting')
        text = update.message.text
        
        if expecting == 'bins':
            await self.add_bins(update, text)
        elif expecting == 'proxies':
            await self.add_proxies(update, text)
        else:
            await update.message.reply_text("Use /start to see available options")

    async def add_bins(self, update: Update, text: str):
        """Add BINs to database"""
        bins = [line.strip() for line in text.split('\n') if line.strip()]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added = 0
        for bin_num in bins:
            if len(bin_num) >= 6 and bin_num.isdigit():
                try:
                    cursor.execute("INSERT OR IGNORE INTO bins (bin) VALUES (?)", (bin_num,))
                    if cursor.rowcount > 0:
                        added += 1
                except:
                    pass
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Added {added} new BINs\n"
            f"Total BINs received: {len(bins)}"
        )

    async def add_proxies(self, update: Update, text: str):
        """Add proxies to database"""
        proxies = [line.strip() for line in text.split('\n') if line.strip()]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        added = 0
        for proxy in proxies:
            if ':' in proxy:  # Basic validation
                try:
                    cursor.execute("INSERT OR IGNORE INTO proxies (proxy) VALUES (?)", (proxy,))
                    if cursor.rowcount > 0:
                        added += 1
                except:
                    pass
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Added {added} new proxies\n"
            f"Total proxies received: {len(proxies)}"
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        
        if not self.is_authorized(query.from_user.id):
            await query.answer("Unauthorized", show_alert=True)
            return
        
        await query.answer()
        
        action = query.data
        
        if action == 'dashboard':
            await self.dashboard(update, context)
        elif action == 'bins':
            await self.manage_bins(update, context)
        elif action == 'proxies':
            await self.manage_proxies(update, context)
        elif action == 'hits':
            await self.show_hits(update, context)
        elif action == 'start_hitting':
            await self.start_hitting(update, context)
        elif action == 'stop_hitting':
            await self.stop_hitting(update, context)
        elif action == 'main_menu':
            await self.show_main_menu(update, context)
        elif action == 'clear_bins':
            await self.clear_bins(update, context)
        elif action == 'clear_proxies':
            await self.clear_proxies(update, context)
        elif action == 'clear_hits':
            await self.clear_hits(update, context)
        elif action == 'export_hits':
            await self.export_hits(update, context)

    async def start_hitting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send command to start hitting"""
        # This would integrate with the Chrome extension via WebSocket or API
        await update.callback_query.edit_message_text(
            "▶️ *Starting AutoHitter...*\n\n"
            "The Chrome extension will begin hitting with configured BINs and proxies.\n"
            "You'll receive notifications for successful hits.",
            parse_mode='Markdown'
        )
        
        # Here you would send a command to the Chrome extension
        # via your Skybin API or WebSocket connection

    async def stop_hitting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send command to stop hitting"""
        await update.callback_query.edit_message_text(
            "⏸️ *Stopping AutoHitter...*\n\n"
            "The Chrome extension will stop all hitting activities.",
            parse_mode='Markdown'
        )

    async def export_hits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export hits as JSON file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hits ORDER BY timestamp DESC")
        hits = cursor.fetchall()
        conn.close()
        
        # Convert to JSON
        hits_data = []
        for hit in hits:
            hits_data.append({
                'id': hit[0],
                'timestamp': hit[1],
                'merchant': hit[2],
                'amount': hit[3],
                'bin': hit[4],
                'last4': hit[5],
                'result': hit[6],
                'message': hit[7],
                'proxy': hit[8]
            })
        
        # Save to file
        filename = f"bh_hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(hits_data, f, indent=2)
        
        # Send file
        await update.callback_query.message.reply_document(
            document=open(filename, 'rb'),
            caption=f"📤 Exported {len(hits_data)} hits"
        )
        
        # Clean up
        os.remove(filename)

    async def notify_hit(self, hit_data: Dict):
        """Send notification for new hit"""
        emoji = "✅" if hit_data['result'] == 'success' else "❌"
        
        message = f"""
{emoji} *NEW HIT*
━━━━━━━━━━━━━━━━━

💳 Card: {hit_data['bin']}****{hit_data['last4']}
📅 Exp: {hit_data['exp']}
🏪 Merchant: {hit_data['merchant']}
💵 Amount: ${hit_data['amount']}
📊 Result: {hit_data['result']}
📝 Message: {hit_data['message']}
🌐 Proxy: {hit_data.get('proxy', 'Direct')}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
        """
        
        # Send to authorized user
        app = Application.builder().token(self.token).build()
        await app.bot.send_message(
            chat_id=self.authorized_user,
            text=message,
            parse_mode='Markdown'
        )

    def run(self):
        """Run the bot"""
        app = Application.builder().token(self.token).build()
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.start))
        
        # Callback query handler
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
        
        # Start the bot
        logger.info("Starting BH Telegram Bot...")
        app.run_polling()

if __name__ == "__main__":
    # Configuration
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
    YOUR_TELEGRAM_ID = 123456789  # Your Telegram user ID
    
    # Create and run bot
    bot = BHTelegramBot(BOT_TOKEN, YOUR_TELEGRAM_ID)
    bot.run()