#!/usr/bin/env python3
"""
Personal Telegram Bot for SkyBin
Allows querying and receiving notifications about high-value leaks
"""

import logging
import asyncio
import os
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your-bot-token-here')
SKYBIN_API = os.getenv('SKYBIN_API_URL', 'http://localhost:8082')
ADMIN_CHAT_IDS = os.getenv('ADMIN_CHAT_IDS', '').split(',')  # Comma-separated list
NOTIFICATION_CHANNEL = os.getenv('NOTIFICATION_CHANNEL', '')  # Channel ID for broadcasts

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User session storage (in production, use Redis)
user_sessions = {}
notification_preferences = {}


class SkybinBot:
    """Personal Telegram bot for SkyBin interaction"""
    
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.last_check = datetime.now()
        
    def setup_handlers(self):
        """Setup command and message handlers"""
        # Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("search", self.cmd_search))
        self.app.add_handler(CommandHandler("latest", self.cmd_latest))
        self.app.add_handler(CommandHandler("stats", self.cmd_stats))
        self.app.add_handler(CommandHandler("subscribe", self.cmd_subscribe))
        self.app.add_handler(CommandHandler("unsubscribe", self.cmd_unsubscribe))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("highvalue", self.cmd_highvalue))
        
        # Callback queries for inline keyboards
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Direct messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized access.")
            return
        
        welcome_msg = """
🔐 **SkyBin Personal Bot**

Welcome to your personal credential monitoring bot!

**Available Commands:**
• /search <query> - Search for specific credentials
• /latest - View latest discoveries
• /highvalue - Show high-value finds only
• /stats - View statistics
• /subscribe - Enable notifications
• /unsubscribe - Disable notifications
• /help - Show this help

**Quick Actions:**
Just send any text to search instantly!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Latest", callback_data="latest"),
                InlineKeyboardButton("⭐ High Value", callback_data="highvalue")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_msg, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /search <query>\nExample: /search netflix")
            return
        
        query = ' '.join(context.args)
        await self.perform_search(update, query)
    
    async def perform_search(self, update: Update, query: str):
        """Perform search and send results"""
        try:
            # Search SkyBin
            response = requests.get(
                f"{SKYBIN_API}/api/search",
                params={'q': query, 'limit': 10},
                timeout=10
            )
            
            if response.status_code != 200:
                await update.message.reply_text("❌ Search failed. Try again later.")
                return
            
            data = response.json()
            pastes = data.get('data', [])
            
            if not pastes:
                await update.message.reply_text(f"No results found for: {query}")
                return
            
            # Format results
            msg = f"🔍 **Search Results for '{query}':**\n\n"
            
            for paste in pastes[:5]:  # Limit to 5 results
                title = paste.get('title', 'Untitled')
                paste_id = paste.get('id', '')
                source = paste.get('source', 'unknown')
                created = self._format_time(paste.get('created_at', 0))
                
                # Truncate title if too long
                if len(title) > 50:
                    title = title[:47] + "..."
                
                msg += f"📄 **{title}**\n"
                msg += f"   Source: {source} | {created}\n"
                msg += f"   [View]({SKYBIN_API}/paste/{paste_id})\n\n"
            
            keyboard = [[
                InlineKeyboardButton("🔍 Search More", callback_data=f"search_more:{query}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await update.message.reply_text("❌ An error occurred during search.")
    
    async def cmd_latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /latest command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized.")
            return
        
        await self.fetch_latest(update)
    
    async def fetch_latest(self, update: Update, high_value_only: bool = False):
        """Fetch and display latest pastes"""
        try:
            params = {'limit': 10}
            if high_value_only:
                params['high_value'] = 'true'
            
            response = requests.get(
                f"{SKYBIN_API}/api/pastes",
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                await update.message.reply_text("❌ Failed to fetch latest pastes.")
                return
            
            data = response.json()
            pastes = data.get('data', [])
            
            if not pastes:
                msg = "No high-value pastes found." if high_value_only else "No pastes found."
                await update.message.reply_text(msg)
                return
            
            # Format results
            title = "⭐ **High-Value Discoveries:**" if high_value_only else "📋 **Latest Discoveries:**"
            msg = f"{title}\n\n"
            
            for paste in pastes[:10]:
                paste_title = paste.get('title', 'Untitled')
                paste_id = paste.get('id', '')
                source = paste.get('source', 'unknown')
                is_sensitive = paste.get('is_sensitive', False)
                created = self._format_time(paste.get('created_at', 0))
                
                # Add emoji based on sensitivity
                emoji = "🔴" if is_sensitive else "🟢"
                
                # Truncate title
                if len(paste_title) > 45:
                    paste_title = paste_title[:42] + "..."
                
                msg += f"{emoji} **{paste_title}**\n"
                msg += f"   {source} | {created}\n"
                msg += f"   [View]({SKYBIN_API}/paste/{paste_id})\n\n"
            
            await update.message.reply_text(
                msg,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Latest fetch error: {e}")
            await update.message.reply_text("❌ An error occurred.")
    
    async def cmd_highvalue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /highvalue command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized.")
            return
        
        await self.fetch_latest(update, high_value_only=True)
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized.")
            return
        
        try:
            response = requests.get(f"{SKYBIN_API}/api/stats", timeout=10)
            
            if response.status_code != 200:
                await update.message.reply_text("❌ Failed to fetch stats.")
                return
            
            data = response.json().get('data', {})
            
            total = data.get('total_pastes', 0)
            sensitive = data.get('sensitive_pastes', 0)
            recent = data.get('recent_count', 0)
            
            msg = f"""
📊 **SkyBin Statistics**

**Total Pastes:** {total:,}
**Sensitive:** {sensitive:,} ({sensitive/max(total,1)*100:.1f}%)
**Last 24h:** {recent:,}

**Top Sources:**
"""
            
            by_source = data.get('by_source', {})
            for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:5]:
                msg += f"• {source}: {count:,}\n"
            
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await update.message.reply_text("❌ An error occurred.")
    
    async def cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await update.message.reply_text("⛔ Unauthorized.")
            return
        
        notification_preferences[user_id] = {
            'enabled': True,
            'high_value_only': False,
            'keywords': []
        }
        
        await update.message.reply_text(
            "🔔 **Notifications Enabled!**\n\n"
            "You will receive notifications for new high-value discoveries.\n\n"
            "Customize with:\n"
            "• /subscribe keywords api,netflix,aws - Monitor specific keywords\n"
            "• /subscribe highvalue - Only high-value items",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user_id = str(update.effective_user.id)
        
        if user_id in notification_preferences:
            notification_preferences[user_id]['enabled'] = False
        
        await update.message.reply_text("🔕 Notifications disabled.")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.cmd_start(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct text messages as search queries"""
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            return
        
        query = update.message.text
        await self.perform_search(update, query)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        user_id = str(update.effective_user.id)
        
        if user_id not in ADMIN_CHAT_IDS:
            await query.answer("Unauthorized", show_alert=True)
            return
        
        await query.answer()
        
        data = query.data
        
        if data == "latest":
            await self.fetch_latest(query)
        elif data == "highvalue":
            await self.fetch_latest(query, high_value_only=True)
        elif data == "stats":
            await self.cmd_stats(query, context)
        elif data == "subscribe":
            await self.cmd_subscribe(query, context)
        elif data.startswith("search_more:"):
            search_query = data.split(":", 1)[1]
            await self.perform_search(query, search_query)
    
    def _format_time(self, timestamp: int) -> str:
        """Format timestamp to relative time"""
        if not timestamp:
            return "unknown"
        
        now = datetime.now()
        then = datetime.fromtimestamp(timestamp)
        diff = now - then
        
        if diff.days > 7:
            return then.strftime("%Y-%m-%d")
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    
    async def check_new_pastes(self):
        """Background task to check for new high-value pastes"""
        while True:
            try:
                # Check every 5 minutes
                await asyncio.sleep(300)
                
                # Get latest high-value pastes
                response = requests.get(
                    f"{SKYBIN_API}/api/pastes",
                    params={'high_value': 'true', 'limit': 5},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    pastes = data.get('data', [])
                    
                    for paste in pastes:
                        created = paste.get('created_at', 0)
                        if created > self.last_check.timestamp():
                            await self.notify_users(paste)
                    
                    self.last_check = datetime.now()
                    
            except Exception as e:
                logger.error(f"Background check error: {e}")
    
    async def notify_users(self, paste: Dict):
        """Send notification to subscribed users"""
        title = paste.get('title', 'New Discovery')
        paste_id = paste.get('id', '')
        
        msg = f"🔔 **New High-Value Discovery!**\n\n{title}\n\n[View]({SKYBIN_API}/paste/{paste_id})"
        
        for user_id, prefs in notification_preferences.items():
            if prefs.get('enabled', False):
                try:
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=msg,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Failed to notify {user_id}: {e}")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting SkyBin Telegram Bot...")
        
        # Start background task
        asyncio.create_task(self.check_new_pastes())
        
        # Run bot
        self.app.run_polling()


if __name__ == "__main__":
    bot = SkybinBot()
    bot.run()