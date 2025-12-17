use crate::bin_detector::Card;
use chrono::{DateTime, Utc};
use std::collections::HashMap;

pub struct BinFormatter {
    post_style: PostStyle,
    include_emojis: bool,
    max_cards_per_post: usize,
}

#[derive(Clone)]
pub enum PostStyle {
    Clean,      // Minimal formatting
    Detailed,   // Full card info
    Stealth,    // Looks like casual message
}

impl BinFormatter {
    pub fn new(style: PostStyle) -> Self {
        Self {
            post_style: style,
            include_emojis: true,
            max_cards_per_post: 10,
        }
    }
    
    pub fn format_cards(&self, cards: &[Card], source: &str) -> String {
        match self.post_style {
            PostStyle::Clean => self.format_clean(cards, source),
            PostStyle::Detailed => self.format_detailed(cards, source),
            PostStyle::Stealth => self.format_stealth(cards),
        }
    }
    
    fn format_clean(&self, cards: &[Card], source: &str) -> String {
        let mut output = String::new();
        
        if self.include_emojis {
            output.push_str("💳 ");
        }
        
        output.push_str(&format!("Fresh Drop | {} cards\n", cards.len()));
        output.push_str("━━━━━━━━━━━━━━━━\n");
        
        // Group by brand
        let mut by_brand: HashMap<&str, Vec<&Card>> = HashMap::new();
        for card in cards {
            by_brand.entry(&card.brand).or_insert_with(Vec::new).push(card);
        }
        
        for (brand, brand_cards) in by_brand {
            output.push_str(&format!("\n{} ({})\n", brand, brand_cards.len()));
            
            for card in brand_cards.iter().take(self.max_cards_per_post) {
                output.push_str(&format!(
                    "{} | {} | {}\n",
                    card.number,
                    card.exp_date.as_deref().unwrap_or("XX/XX"),
                    card.cvv.as_deref().unwrap_or("XXX")
                ));
                
                if let Some(fullz) = &card.fullz_info {
                    output.push_str(&format!("  └─ {}\n", fullz));
                }
            }
        }
        
        output.push_str("\n━━━━━━━━━━━━━━━━\n");
        output.push_str(&format!("Source: {}\n", source));
        output.push_str(&format!("Time: {}\n", Utc::now().format("%H:%M UTC")));
        
        output
    }
    
    fn format_detailed(&self, cards: &[Card], source: &str) -> String {
        let mut output = String::new();
        
        output.push_str("🔥 NEW DROP ALERT 🔥\n");
        output.push_str("═══════════════════\n\n");
        
        for (idx, card) in cards.iter().enumerate().take(self.max_cards_per_post) {
            output.push_str(&format!("#{} ", idx + 1));
            
            // Add brand emoji
            let emoji = match card.brand.as_str() {
                "Visa" => "💳",
                "MasterCard" => "💰",
                "AmEx" => "💎",
                "Discover" => "🎯",
                _ => "🏦",
            };
            
            output.push_str(&format!("{} {} ", emoji, card.brand));
            
            // Confidence indicator
            let confidence_stars = match card.confidence {
                c if c >= 0.9 => "⭐⭐⭐⭐⭐",
                c if c >= 0.8 => "⭐⭐⭐⭐",
                c if c >= 0.7 => "⭐⭐⭐",
                c if c >= 0.6 => "⭐⭐",
                _ => "⭐",
            };
            
            output.push_str(&format!("[{}]\n", confidence_stars));
            
            // Card details
            output.push_str(&format!("├─ Number: {}\n", card.number));
            
            if let Some(exp) = &card.exp_date {
                output.push_str(&format!("├─ Exp: {}\n", exp));
            }
            
            if let Some(cvv) = &card.cvv {
                output.push_str(&format!("├─ CVV: {}\n", cvv));
            }
            
            if let Some(pin) = &card.pin {
                output.push_str(&format!("├─ PIN: {}\n", pin));
            }
            
            if let Some(fullz) = &card.fullz_info {
                output.push_str(&format!("├─ Fullz: {}\n", fullz));
            }
            
            output.push_str(&format!(
                "└─ Valid: {} | Type: {}\n\n",
                if card.is_valid { "✅" } else { "❌" },
                card.card_type.as_deref().unwrap_or("Unknown")
            ));
        }
        
        if cards.len() > self.max_cards_per_post {
            output.push_str(&format!(
                "... and {} more cards\n\n",
                cards.len() - self.max_cards_per_post
            ));
        }
        
        output.push_str("═══════════════════\n");
        output.push_str(&format!("📍 Source: {}\n", source));
        output.push_str(&format!("🕒 Timestamp: {}\n", Utc::now().format("%Y-%m-%d %H:%M:%S UTC")));
        output.push_str(&format!("📊 Total: {} cards", cards.len()));
        
        output
    }
    
    fn format_stealth(&self, cards: &[Card]) -> String {
        // Format as casual message that doesn't look suspicious
        let mut output = String::new();
        
        let intros = vec![
            "found these",
            "check this out",
            "new stuff",
            "fresh",
            "got some",
        ];
        
        let intro = intros[rand::random::<usize>() % intros.len()];
        output.push_str(&format!("{}\n\n", intro));
        
        for card in cards.iter().take(5) {
            // Just post the essentials, no fancy formatting
            output.push_str(&format!("{}", card.number));
            
            if let Some(exp) = &card.exp_date {
                output.push_str(&format!(" {}", exp));
            }
            
            if let Some(cvv) = &card.cvv {
                output.push_str(&format!(" {}", cvv));
            }
            
            output.push_str("\n");
        }
        
        if cards.len() > 5 {
            output.push_str(&format!("+ {} more", cards.len() - 5));
        }
        
        output
    }
    
    pub fn format_error(&self, error: &str) -> String {
        format!("⚠️ Error: {}", error)
    }
    
    pub fn format_stats(&self, total_found: usize, valid: usize, posted: usize) -> String {
        let mut output = String::new();
        
        output.push_str("📊 Session Stats\n");
        output.push_str("━━━━━━━━━━━━━━━━\n");
        output.push_str(&format!("🔍 Found: {}\n", total_found));
        output.push_str(&format!("✅ Valid: {}\n", valid));
        output.push_str(&format!("📮 Posted: {}\n", posted));
        output.push_str(&format!("🕒 {}\n", Utc::now().format("%H:%M UTC")));
        
        output
    }
}