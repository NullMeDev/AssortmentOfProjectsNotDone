use serde::{Deserialize, Serialize};
use std::path::Path;
use anyhow::Result;
use crate::stealth::StealthLevel;
use crate::formatter::PostStyle;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    // Telegram API credentials
    pub api_id: i32,
    pub api_hash: String,
    pub phone: String,
    pub session_file: String,
    
    // Target channel for posting
    pub target_channel_id: i64,
    
    // Groups to monitor
    pub monitored_groups: Vec<i64>,
    
    // Stealth settings
    pub stealth_level: StealthLevelConfig,
    
    // Formatter settings  
    pub post_style: PostStyleConfig,
    
    // Detection settings
    pub min_confidence: f64,
    pub only_high_value: bool,
    pub dedupe_hours: u64,
    
    // Database
    pub database_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum StealthLevelConfig {
    Ghost,
    Normal,
    Aggressive,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum PostStyleConfig {
    Clean,
    Detailed,
    Stealth,
}

impl From<StealthLevelConfig> for StealthLevel {
    fn from(config: StealthLevelConfig) -> Self {
        match config {
            StealthLevelConfig::Ghost => StealthLevel::Ghost,
            StealthLevelConfig::Normal => StealthLevel::Normal,
            StealthLevelConfig::Aggressive => StealthLevel::Aggressive,
        }
    }
}

impl From<PostStyleConfig> for PostStyle {
    fn from(config: PostStyleConfig) -> Self {
        match config {
            PostStyleConfig::Clean => PostStyle::Clean,
            PostStyleConfig::Detailed => PostStyle::Detailed,
            PostStyleConfig::Stealth => PostStyle::Stealth,
        }
    }
}

impl Config {
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        let contents = std::fs::read_to_string(path)?;
        let config: Config = toml::from_str(&contents)?;
        Ok(config)
    }
    
    pub fn from_env() -> Result<Self> {
        // Load from environment variables
        Ok(Config {
            api_id: std::env::var("TELEGRAM_API_ID")?
                .parse()
                .map_err(|e| anyhow::anyhow!("Invalid API ID: {}", e))?,
            api_hash: std::env::var("TELEGRAM_API_HASH")?,
            phone: std::env::var("TELEGRAM_PHONE")?,
            session_file: std::env::var("SESSION_FILE")
                .unwrap_or_else(|_| "bin_scraper.session".to_string()),
            target_channel_id: std::env::var("TARGET_CHANNEL_ID")?
                .parse()
                .map_err(|e| anyhow::anyhow!("Invalid channel ID: {}", e))?,
            monitored_groups: std::env::var("MONITORED_GROUPS")
                .unwrap_or_else(|_| String::new())
                .split(',')
                .filter_map(|s| s.trim().parse().ok())
                .collect(),
            stealth_level: match std::env::var("STEALTH_LEVEL")
                .unwrap_or_else(|_| "normal".to_string())
                .to_lowercase()
                .as_str()
            {
                "ghost" => StealthLevelConfig::Ghost,
                "aggressive" => StealthLevelConfig::Aggressive,
                _ => StealthLevelConfig::Normal,
            },
            post_style: match std::env::var("POST_STYLE")
                .unwrap_or_else(|_| "clean".to_string())
                .to_lowercase()
                .as_str()
            {
                "detailed" => PostStyleConfig::Detailed,
                "stealth" => PostStyleConfig::Stealth,
                _ => PostStyleConfig::Clean,
            },
            min_confidence: std::env::var("MIN_CONFIDENCE")
                .unwrap_or_else(|_| "0.7".to_string())
                .parse()
                .unwrap_or(0.7),
            only_high_value: std::env::var("ONLY_HIGH_VALUE")
                .unwrap_or_else(|_| "true".to_string())
                .parse()
                .unwrap_or(true),
            dedupe_hours: std::env::var("DEDUPE_HOURS")
                .unwrap_or_else(|_| "24".to_string())
                .parse()
                .unwrap_or(24),
            database_path: std::env::var("DATABASE_PATH")
                .unwrap_or_else(|_| "bin_scraper.db".to_string()),
        })
    }
    
    pub fn default() -> Self {
        Config {
            api_id: 0,
            api_hash: String::new(),
            phone: String::new(),
            session_file: "bin_scraper.session".to_string(),
            target_channel_id: 0,
            monitored_groups: vec![],
            stealth_level: StealthLevelConfig::Normal,
            post_style: PostStyleConfig::Clean,
            min_confidence: 0.7,
            only_high_value: true,
            dedupe_hours: 24,
            database_path: "bin_scraper.db".to_string(),
        }
    }
    
    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> Result<()> {
        let toml_string = toml::to_string_pretty(self)?;
        std::fs::write(path, toml_string)?;
        Ok(())
    }
    
    pub fn validate(&self) -> Result<()> {
        if self.api_id == 0 {
            return Err(anyhow::anyhow!("API ID is required"));
        }
        
        if self.api_hash.is_empty() {
            return Err(anyhow::anyhow!("API hash is required"));
        }
        
        if self.phone.is_empty() {
            return Err(anyhow::anyhow!("Phone number is required"));
        }
        
        if self.target_channel_id == 0 {
            return Err(anyhow::anyhow!("Target channel ID is required"));
        }
        
        if self.monitored_groups.is_empty() {
            return Err(anyhow::anyhow!("At least one monitored group is required"));
        }
        
        if self.min_confidence < 0.0 || self.min_confidence > 1.0 {
            return Err(anyhow::anyhow!("Min confidence must be between 0 and 1"));
        }
        
        Ok(())
    }
}