mod bin_detector;
mod formatter;
mod telegram;
mod config;
mod stealth;

use anyhow::Result;
use tracing::{info, error};
use std::sync::Arc;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(false)
        .with_file(false)
        .with_line_number(false)
        .init();
    
    info!("🚀 Starting BIN Scraper Bot...");
    
    // Load configuration
    let config = match config::Config::from_file("config.toml") {
        Ok(c) => {
            info!("✅ Loaded config from file");
            c
        }
        Err(_) => {
            info!("📝 Loading config from environment variables");
            match config::Config::from_env() {
                Ok(c) => c,
                Err(e) => {
                    error!("❌ Failed to load config: {}", e);
                    error!("Please copy config.toml.example to config.toml and fill in your settings");
                    return Err(e);
                }
            }
        }
    };
    
    // Validate config
    config.validate()?;
    info!("✅ Configuration validated");
    
    // Initialize components
    let detector = Arc::new(bin_detector::BinDetector::new(
        config.min_confidence,
        config.dedupe_hours,
    ));
    info!("🔍 BIN detector initialized");
    
    let formatter = Arc::new(formatter::BinFormatter::new(
        config.post_style.clone().into()
    ));
    info!("📝 Formatter initialized with {:?} style", config.post_style);
    
    let stealth = Arc::new(stealth::StealthMode::new(
        config.stealth_level.clone().into()
    ));
    info!("🥷 Stealth mode set to {:?}", config.stealth_level);
    
    // Connect to Telegram
    let mut telegram_client = telegram::TelegramClient::connect(config.clone()).await?;
    info!("✅ Connected to Telegram");
    
    info!("🎯 Monitoring {} groups", config.monitored_groups.len());
    info!("📮 Posting to channel ID: {}", config.target_channel_id);
    
    // Start monitoring
    telegram_client.start_monitoring(
        detector,
        formatter,
        stealth,
    ).await?;
    
    Ok(())
}
