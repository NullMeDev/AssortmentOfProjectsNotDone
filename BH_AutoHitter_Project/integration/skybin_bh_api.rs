// BH AutoHitter API Integration for Skybin
// For personal use only - NOT for commercial purposes
//
// Add this module to your Skybin src/main.rs or create as a separate module

use actix_web::{web, HttpRequest, HttpResponse, Result};
use serde::{Deserialize, Serialize};
use sqlx::{Pool, Sqlite};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use uuid::Uuid;
use base64;

#[derive(Debug, Serialize, Deserialize)]
pub struct BHHitData {
    pub timestamp: i64,
    pub hit_type: String,
    pub data: String, // Encrypted data
    pub auth: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BHConfig {
    pub bins: Vec<String>,
    pub proxies: Vec<String>,
    pub settings: HashMap<String, serde_json::Value>,
    pub telegram: TelegramConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TelegramConfig {
    pub enabled: bool,
    pub chat_id: Option<i64>,
    pub bot_token: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BHPaste {
    pub title: String,
    pub content: String,
    pub syntax: String,
    pub visibility: String,
    pub tags: Vec<String>,
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BHCommand {
    pub action: String,
    pub params: HashMap<String, serde_json::Value>,
}

/// Verify authentication token
fn verify_auth(auth_token: &str) -> bool {
    // For personal use, implement your own auth verification
    // This is a simple check - enhance based on your security needs
    auth_token.starts_with("bh_") && auth_token.len() > 10
}

/// Decrypt data (simple XOR for personal use)
fn decrypt_data(encrypted: &str, key: &str) -> Result<String, Box<dyn std::error::Error>> {
    let decoded = base64::decode(encrypted)?;
    let mut decrypted = Vec::new();
    
    for (i, byte) in decoded.iter().enumerate() {
        let key_byte = key.as_bytes()[i % key.len()];
        decrypted.push(byte ^ key_byte);
    }
    
    Ok(String::from_utf8(decrypted)?)
}

/// Handle BH hit data submission
pub async fn handle_bh_hit(
    req: HttpRequest,
    hit_data: web::Json<BHHitData>,
    pool: web::Data<Pool<Sqlite>>,
) -> Result<HttpResponse> {
    // Check authorization
    let auth_header = req.headers()
        .get("X-BH-Auth")
        .and_then(|h| h.to_str().ok())
        .unwrap_or("");
    
    if !verify_auth(auth_header) {
        return Ok(HttpResponse::Unauthorized().json(serde_json::json!({
            "error": "Unauthorized"
        })));
    }
    
    // Store hit in database
    let hit_id = Uuid::new_v4().to_string();
    let timestamp = Utc::now();
    
    sqlx::query!(
        "INSERT INTO bh_hits (id, timestamp, type, data, auth_token) VALUES (?, ?, ?, ?, ?)",
        hit_id,
        timestamp,
        hit_data.hit_type,
        hit_data.data,
        auth_header
    )
    .execute(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    // Send to Telegram if configured
    if let Ok(decrypted) = decrypt_data(&hit_data.data, "YOUR_ENCRYPTION_KEY") {
        // Parse and send to Telegram bot
        // Implementation depends on your Telegram integration
    }
    
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "hit_id": hit_id,
        "timestamp": timestamp
    })))
}

/// Get BH configuration
pub async fn get_bh_config(
    req: HttpRequest,
    pool: web::Data<Pool<Sqlite>>,
) -> Result<HttpResponse> {
    // Check authorization
    let auth_header = req.headers()
        .get("X-BH-Auth")
        .and_then(|h| h.to_str().ok())
        .unwrap_or("");
    
    if !verify_auth(auth_header) {
        return Ok(HttpResponse::Unauthorized().json(serde_json::json!({
            "error": "Unauthorized"
        })));
    }
    
    // Fetch configuration from database
    let bins: Vec<String> = sqlx::query_scalar!("SELECT bin FROM bh_bins WHERE active = 1")
        .fetch_all(pool.get_ref())
        .await
        .unwrap_or_else(|_| Vec::new());
    
    let proxies: Vec<String> = sqlx::query_scalar!("SELECT proxy FROM bh_proxies WHERE active = 1")
        .fetch_all(pool.get_ref())
        .await
        .unwrap_or_else(|_| Vec::new());
    
    let config = BHConfig {
        bins,
        proxies,
        settings: HashMap::new(),
        telegram: TelegramConfig {
            enabled: true,
            chat_id: None,
            bot_token: None,
        },
    };
    
    Ok(HttpResponse::Ok().json(config))
}

/// Create a paste for BH hit
pub async fn create_bh_paste(
    paste_data: web::Json<BHPaste>,
    pool: web::Data<Pool<Sqlite>>,
) -> Result<HttpResponse> {
    let paste_id = Uuid::new_v4().to_string();
    let delete_token = Uuid::new_v4().to_string();
    let timestamp = Utc::now();
    
    // Insert paste into database
    sqlx::query!(
        "INSERT INTO pastes (id, title, content, syntax, created_at, delete_token, source) 
         VALUES (?, ?, ?, ?, ?, ?, ?)",
        paste_id,
        paste_data.title,
        paste_data.content,
        paste_data.syntax,
        timestamp,
        delete_token,
        "bh_autohitter"
    )
    .execute(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    // Insert tags
    for tag in &paste_data.tags {
        sqlx::query!(
            "INSERT INTO paste_tags (paste_id, tag) VALUES (?, ?)",
            paste_id,
            tag
        )
        .execute(pool.get_ref())
        .await
        .ok();
    }
    
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "id": paste_id,
        "deleteToken": delete_token,
        "url": format!("/paste/{}", paste_id)
    })))
}

/// WebSocket handler for real-time BH communication
pub async fn bh_websocket(
    req: HttpRequest,
    stream: web::Payload,
    pool: web::Data<Pool<Sqlite>>,
) -> Result<HttpResponse> {
    use actix_web_actors::ws;
    
    // Create WebSocket actor
    let actor = BHWebSocketActor::new(pool.get_ref().clone());
    ws::start(actor, &req, stream)
}

/// WebSocket actor for BH real-time communication
pub struct BHWebSocketActor {
    pool: Pool<Sqlite>,
    authenticated: bool,
}

impl BHWebSocketActor {
    pub fn new(pool: Pool<Sqlite>) -> Self {
        Self {
            pool,
            authenticated: false,
        }
    }
}

impl actix::Actor for BHWebSocketActor {
    type Context = ws::WebsocketContext<Self>;
    
    fn started(&mut self, ctx: &mut Self::Context) {
        // Send welcome message
        ctx.text(serde_json::json!({
            "type": "welcome",
            "message": "Connected to BH WebSocket"
        }).to_string());
    }
}

impl actix_web_actors::ws::StreamHandler<Result<ws::Message, ws::ProtocolError>> 
    for BHWebSocketActor 
{
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Text(text)) => {
                // Parse message
                if let Ok(message) = serde_json::from_str::<serde_json::Value>(&text) {
                    match message["type"].as_str() {
                        Some("auth") => {
                            // Authenticate
                            if let Some(token) = message["token"].as_str() {
                                if verify_auth(token) {
                                    self.authenticated = true;
                                    ctx.text(serde_json::json!({
                                        "type": "auth_success",
                                        "message": "Authentication successful"
                                    }).to_string());
                                }
                            }
                        }
                        Some("command") if self.authenticated => {
                            // Handle command
                            if let Ok(command) = serde_json::from_value::<BHCommand>(message["data"].clone()) {
                                // Process command
                                ctx.text(serde_json::json!({
                                    "type": "command_ack",
                                    "action": command.action
                                }).to_string());
                            }
                        }
                        _ => {}
                    }
                }
            }
            Ok(ws::Message::Close(_)) => {
                ctx.stop();
            }
            _ => {}
        }
    }
}

/// Configure BH API routes
pub fn configure_bh_routes(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/api/bh")
            .route("/hit", web::post().to(handle_bh_hit))
            .route("/config", web::get().to(get_bh_config))
            .route("/paste", web::post().to(create_bh_paste))
            .route("/ws", web::get().to(bh_websocket))
    );
}

// SQL schema for BH integration (add to your migrations)
pub const BH_SCHEMA: &str = r#"
CREATE TABLE IF NOT EXISTS bh_hits (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL,
    data TEXT NOT NULL,
    auth_token TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bh_bins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin TEXT UNIQUE NOT NULL,
    active INTEGER DEFAULT 1,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bh_proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy TEXT UNIQUE NOT NULL,
    active INTEGER DEFAULT 1,
    last_used DATETIME,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bh_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bh_hits_timestamp ON bh_hits(timestamp);
CREATE INDEX idx_bh_hits_type ON bh_hits(type);
"#;