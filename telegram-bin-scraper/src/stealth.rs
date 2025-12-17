use tokio::time::{sleep, Duration};
use rand::Rng;
use tracing::{debug, info};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

pub struct StealthMode {
    mode: StealthLevel,
    actions_count: Arc<AtomicUsize>,
    last_action_time: Arc<tokio::sync::RwLock<std::time::Instant>>,
}

#[derive(Clone, Debug)]
pub enum StealthLevel {
    Ghost,      // Ultra-stealth, very slow
    Normal,     // Balanced
    Aggressive, // Faster but riskier
}

impl StealthMode {
    pub fn new(level: StealthLevel) -> Self {
        Self {
            mode: level,
            actions_count: Arc::new(AtomicUsize::new(0)),
            last_action_time: Arc::new(tokio::sync::RwLock::new(std::time::Instant::now())),
        }
    }
    
    /// Random delay between min and max seconds
    pub async fn random_delay(&self, min_seconds: f64, max_seconds: f64) {
        let multiplier = match self.mode {
            StealthLevel::Ghost => 2.5,    // Much slower
            StealthLevel::Normal => 1.0,   // Standard timing
            StealthLevel::Aggressive => 0.3, // Faster
        };
        
        let mut rng = rand::thread_rng();
        let delay = rng.gen_range(min_seconds..max_seconds) * multiplier;
        
        debug!("🕐 Stealth delay: {:.1}s", delay);
        sleep(Duration::from_secs_f64(delay)).await;
    }
    
    /// Simulate human reading speed
    pub async fn simulate_human_reading(&self, text_length: usize) {
        // Average human reads 200-250 words per minute
        // Assume 5 chars per word
        let words = text_length / 5;
        let base_reading_time = (words as f64 / 250.0) * 60.0; // seconds
        
        let multiplier = match self.mode {
            StealthLevel::Ghost => 1.5,
            StealthLevel::Normal => 1.0,
            StealthLevel::Aggressive => 0.5,
        };
        
        let mut rng = rand::thread_rng();
        let variance = rng.gen_range(0.8..1.2);
        let reading_time = base_reading_time * multiplier * variance;
        
        // Cap at reasonable limits
        let reading_time = reading_time.min(30.0).max(0.5);
        
        debug!("📖 Simulating reading for {:.1}s", reading_time);
        sleep(Duration::from_secs_f64(reading_time)).await;
    }
    
    /// Simulate typing delay
    pub async fn simulate_typing(&self, text: &str) {
        let chars = text.len();
        // Average typing speed: 40 WPM = 200 CPM = 3.3 CPS
        let base_typing_time = chars as f64 / 3.3;
        
        let multiplier = match self.mode {
            StealthLevel::Ghost => 1.2,
            StealthLevel::Normal => 1.0,
            StealthLevel::Aggressive => 0.6,
        };
        
        let mut rng = rand::thread_rng();
        let variance = rng.gen_range(0.9..1.1);
        let typing_time = base_typing_time * multiplier * variance;
        
        debug!("⌨️ Simulating typing for {:.1}s", typing_time);
        sleep(Duration::from_secs_f64(typing_time)).await;
    }
    
    /// Track actions and enforce rate limiting
    pub async fn track_action(&self) {
        let count = self.actions_count.fetch_add(1, Ordering::Relaxed);
        let mut last_time = self.last_action_time.write().await;
        
        let elapsed = last_time.elapsed();
        *last_time = std::time::Instant::now();
        
        // Rate limiting based on mode
        let (max_actions_per_minute, min_gap_seconds) = match self.mode {
            StealthLevel::Ghost => (5, 10.0),      // 5 actions/min, 10s gap
            StealthLevel::Normal => (15, 3.0),     // 15 actions/min, 3s gap
            StealthLevel::Aggressive => (30, 1.0), // 30 actions/min, 1s gap
        };
        
        // Check if we need to slow down
        if count > 0 && elapsed.as_secs_f64() < min_gap_seconds {
            let wait_time = min_gap_seconds - elapsed.as_secs_f64();
            debug!("⏸️ Rate limiting: waiting {:.1}s", wait_time);
            sleep(Duration::from_secs_f64(wait_time)).await;
        }
        
        // Reset counter periodically
        if count >= max_actions_per_minute {
            self.actions_count.store(0, Ordering::Relaxed);
            info!("🔄 Action counter reset after {} actions", count);
        }
    }
    
    /// Random online/offline pattern
    pub async fn simulate_presence(&self) {
        let mut rng = rand::thread_rng();
        
        loop {
            // Online period
            let online_duration = match self.mode {
                StealthLevel::Ghost => rng.gen_range(10..30),     // 10-30 minutes
                StealthLevel::Normal => rng.gen_range(30..120),   // 30-120 minutes  
                StealthLevel::Aggressive => rng.gen_range(60..240), // 60-240 minutes
            };
            
            info!("🟢 Simulating online presence for {} minutes", online_duration);
            sleep(Duration::from_secs(online_duration * 60)).await;
            
            // Offline period
            let offline_duration = match self.mode {
                StealthLevel::Ghost => rng.gen_range(5..15),    // 5-15 minutes
                StealthLevel::Normal => rng.gen_range(2..10),   // 2-10 minutes
                StealthLevel::Aggressive => rng.gen_range(1..5), // 1-5 minutes
            };
            
            info!("⚫ Going offline for {} minutes", offline_duration);
            sleep(Duration::from_secs(offline_duration * 60)).await;
        }
    }
    
    /// Random scroll simulation
    pub async fn simulate_scrolling(&self) {
        let mut rng = rand::thread_rng();
        
        // Scroll duration
        let scroll_time = match self.mode {
            StealthLevel::Ghost => rng.gen_range(2.0..5.0),
            StealthLevel::Normal => rng.gen_range(1.0..3.0),
            StealthLevel::Aggressive => rng.gen_range(0.5..1.5),
        };
        
        debug!("📜 Simulating scroll for {:.1}s", scroll_time);
        sleep(Duration::from_secs_f64(scroll_time)).await;
    }
    
    /// Simulate mouse movements/interactions
    pub async fn simulate_interaction(&self) {
        let mut rng = rand::thread_rng();
        
        // Random chance of interaction
        let interact_chance = match self.mode {
            StealthLevel::Ghost => 0.1,      // 10% chance
            StealthLevel::Normal => 0.3,     // 30% chance
            StealthLevel::Aggressive => 0.5, // 50% chance
        };
        
        if rng.gen::<f64>() < interact_chance {
            debug!("🖱️ Simulating user interaction");
            self.random_delay(0.5, 2.0).await;
        }
    }
    
    /// Get a random user agent
    pub fn get_user_agent(&self) -> &'static str {
        let agents = vec![
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101",
        ];
        
        let mut rng = rand::thread_rng();
        agents[rng.gen_range(0..agents.len())]
    }
    
    /// Check if we should skip this action (random sampling)
    pub fn should_skip(&self) -> bool {
        let mut rng = rand::thread_rng();
        
        let skip_chance = match self.mode {
            StealthLevel::Ghost => 0.3,      // Skip 30% of actions
            StealthLevel::Normal => 0.1,     // Skip 10%
            StealthLevel::Aggressive => 0.0, // Skip none
        };
        
        rng.gen::<f64>() < skip_chance
    }
}