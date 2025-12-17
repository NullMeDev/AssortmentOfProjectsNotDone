use regex::Regex;
use once_cell::sync::Lazy;
use std::collections::HashMap;
use luhn::valid as luhn_valid;

// BIN patterns and card detection
static CARD_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"\b(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7})\b").unwrap()
});

static BIN_PATTERN: Lazy<Regex> = Lazy::new(|| {
    // Matches 6-8 digit BINs at start of line or after whitespace
    Regex::new(r"(?m)(?:^|\s)(\d{6,8})\b").unwrap()
});

static CVV_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"(?:CVV|CVC|CV2|CID)?:?\s*(\d{3,4})\b").unwrap()
});

static EXPIRY_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"\b(0[1-9]|1[0-2])[/\-\s]?(2[4-9]|\d{2}|\d{4})\b").unwrap()
});

// Fullz pattern (Name|Card|MM/YY|CVV|ZIP)
static FULLZ_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"([A-Za-z\s]+)\s*[|]\s*(\d{13,19})\s*[|]\s*(\d{2}/\d{2,4})\s*[|]\s*(\d{3,4})").unwrap()
});

// Card brand detection
static CARD_BRANDS: Lazy<HashMap<&str, Vec<&str>>> = Lazy::new(|| {
    let mut brands = HashMap::new();
    brands.insert("Visa", vec!["4"]);
    brands.insert("MasterCard", vec!["51", "52", "53", "54", "55", "222", "223", "224", "225", "226", "227", "228", "229"]);
    brands.insert("AmEx", vec!["34", "37"]);
    brands.insert("Discover", vec!["6011", "644", "645", "646", "647", "648", "649", "65"]);
    brands.insert("JCB", vec!["3528", "3529", "353", "354", "355", "356", "357", "358"]);
    brands.insert("Diners", vec!["300", "301", "302", "303", "304", "305", "36", "38"]);
    brands.insert("UnionPay", vec!["62"]);
    brands
});

pub struct BinDetector {
    seen_bins: std::sync::Mutex<std::collections::HashSet<String>>,
    bin_database: HashMap<String, BinInfo>,
}

#[derive(Debug, Clone)]
pub struct BinInfo {
    pub bin: String,
    pub brand: String,
    pub bank: Option<String>,
    pub country: Option<String>,
    pub level: Option<String>, // Classic, Gold, Platinum, etc.
}

#[derive(Debug, Clone)]
pub struct DetectedCard {
    pub card_number: Option<String>,
    pub bin: String,
    pub brand: String,
    pub expiry: Option<String>,
    pub cvv: Option<String>,
    pub holder_name: Option<String>,
    pub is_valid: bool,
    pub confidence: f32,
}

impl BinDetector {
    pub fn new() -> Self {
        Self {
            seen_bins: std::sync::Mutex::new(std::collections::HashSet::new()),
            bin_database: Self::load_bin_database(),
        }
    }
    
    fn load_bin_database() -> HashMap<String, BinInfo> {
        // In production, load from a BIN database file
        // For now, using common patterns
        let mut db = HashMap::new();
        
        // Add some common BINs for testing
        db.insert("414720".to_string(), BinInfo {
            bin: "414720".to_string(),
            brand: "Visa".to_string(),
            bank: Some("Chase".to_string()),
            country: Some("US".to_string()),
            level: Some("Classic".to_string()),
        });
        
        db
    }
    
    pub fn detect_cards(&self, text: &str) -> Vec<DetectedCard> {
        let mut cards = Vec::new();
        
        // Check for fullz format first (highest confidence)
        for cap in FULLZ_PATTERN.captures_iter(text) {
            let name = cap.get(1).map(|m| m.as_str().to_string());
            let card = cap.get(2).map(|m| m.as_str().to_string());
            let expiry = cap.get(3).map(|m| m.as_str().to_string());
            let cvv = cap.get(4).map(|m| m.as_str().to_string());
            
            if let Some(card_num) = &card {
                let clean_card = card_num.replace(&[' ', '-'][..], "");
                if clean_card.len() >= 13 {
                    let bin = clean_card[..6].to_string();
                    let brand = self.detect_brand(&bin);
                    let is_valid = self.validate_card(&clean_card);
                    
                    cards.push(DetectedCard {
                        card_number: Some(clean_card),
                        bin: bin.clone(),
                        brand,
                        expiry,
                        cvv,
                        holder_name: name,
                        is_valid,
                        confidence: if is_valid { 0.95 } else { 0.7 },
                    });
                }
            }
        }
        
        // Then check for individual card numbers
        for cap in CARD_PATTERN.captures_iter(text) {
            if let Some(card_match) = cap.get(1) {
                let card = card_match.as_str().replace(&[' ', '-'][..], "");
                if card.len() >= 13 && card.len() <= 19 {
                    let bin = card[..6].to_string();
                    
                    // Skip if we already detected this as part of fullz
                    if cards.iter().any(|c| c.bin == bin) {
                        continue;
                    }
                    
                    let brand = self.detect_brand(&bin);
                    let is_valid = self.validate_card(&card);
                    
                    // Look for nearby CVV and expiry
                    let context_start = card_match.start().saturating_sub(50);
                    let context_end = (card_match.end() + 50).min(text.len());
                    let context = &text[context_start..context_end];
                    
                    let cvv = CVV_PATTERN.captures(context)
                        .and_then(|c| c.get(1))
                        .map(|m| m.as_str().to_string());
                    
                    let expiry = EXPIRY_PATTERN.captures(context)
                        .and_then(|c| c.get(0))
                        .map(|m| m.as_str().to_string());
                    
                    cards.push(DetectedCard {
                        card_number: Some(card.clone()),
                        bin: bin.clone(),
                        brand,
                        expiry,
                        cvv,
                        holder_name: None,
                        is_valid,
                        confidence: if is_valid { 0.8 } else { 0.5 },
                    });
                }
            }
        }
        
        // Finally, check for standalone BINs
        for cap in BIN_PATTERN.captures_iter(text) {
            if let Some(bin_match) = cap.get(1) {
                let bin = bin_match.as_str();
                if bin.len() >= 6 && bin.len() <= 8 {
                    // Skip if already detected as part of a card
                    if cards.iter().any(|c| c.bin.starts_with(bin)) {
                        continue;
                    }
                    
                    let brand = self.detect_brand(bin);
                    cards.push(DetectedCard {
                        card_number: None,
                        bin: bin.to_string(),
                        brand,
                        expiry: None,
                        cvv: None,
                        holder_name: None,
                        is_valid: false,
                        confidence: 0.3,
                    });
                }
            }
        }
        
        // Deduplicate and track new BINs
        let mut seen_bins = self.seen_bins.lock().unwrap();
        cards.retain(|card| {
            if seen_bins.contains(&card.bin) {
                false // Already seen, skip
            } else {
                seen_bins.insert(card.bin.clone());
                true
            }
        });
        
        cards
    }
    
    pub fn detect_brand(&self, bin: &str) -> String {
        for (brand, prefixes) in CARD_BRANDS.iter() {
            for prefix in prefixes {
                if bin.starts_with(prefix) {
                    return brand.to_string();
                }
            }
        }
        "Unknown".to_string()
    }
    
    pub fn validate_card(&self, card_number: &str) -> bool {
        // Remove non-digits
        let clean: String = card_number.chars().filter(|c| c.is_ascii_digit()).collect();
        
        // Check length
        if clean.len() < 13 || clean.len() > 19 {
            return false;
        }
        
        // Luhn algorithm validation
        luhn_valid(&clean)
    }
    
    pub fn is_high_value(&self, card: &DetectedCard) -> bool {
        // High value indicators
        if card.confidence >= 0.8 {
            return true;
        }
        
        // Check for premium card levels
        if let Some(info) = self.bin_database.get(&card.bin) {
            if let Some(level) = &info.level {
                if level.contains("Gold") || level.contains("Platinum") || level.contains("Black") {
                    return true;
                }
            }
        }
        
        // Fullz data is always high value
        if card.holder_name.is_some() && card.cvv.is_some() && card.expiry.is_some() {
            return true;
        }
        
        false
    }
    
    pub fn has_bins(&self, text: &str) -> bool {
        // Quick check for any BIN-like patterns
        BIN_PATTERN.is_match(text) || CARD_PATTERN.is_match(text) || FULLZ_PATTERN.is_match(text)
    }
}