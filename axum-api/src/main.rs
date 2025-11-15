pub mod api;
pub mod config;
pub mod db;
pub mod error;
pub mod middleware;
pub mod models;
pub mod schema;
pub mod state;
pub mod test;
pub mod validation;

use std::sync::Arc;

use crate::{error::AppError, middleware::auth::Auth, state::AppState};
use axum::{Json, Router, middleware::from_fn_with_state, routing::*};
use log::info;
use serde_json::{Value, json};
use tokio::net::TcpListener;
use tower_http::{
    cors::{Any, CorsLayer},
    trace::TraceLayer,
};

pub fn create_app(shared_state: Arc<AppState>) -> Router {
    Router::new()
        // Health check and stats
        .route("/health", get(health_check))
        .nest(
            "/api",
            Router::new()
                .route("/ping", get(health_check))
                .layer(from_fn_with_state(
                    shared_state.clone(),
                    middleware::apikey_auth_middleware_user,
                )),
        )
        .with_state(shared_state.clone())
        .layer(TraceLayer::new_for_http())
        .layer(
            CorsLayer::new()
                .allow_origin(Any)
                .allow_methods(Any)
                .allow_headers(Any),
        )
}

pub fn create_mock_shared_state() -> Result<AppState, Box<dyn std::error::Error>> {
    let config = config::AppConfig::from_env()?;
    let auth = Auth::new(config.jwt_secret.as_bytes());
    Ok(AppState::new(config, auth))
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    // tracing_subscriber::init();

    let config = config::AppConfig::from_env()?;
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    info!("Starting application with config:");
    info!("  Host: {}", config.host);
    info!("  Port: {}", config.port);
    info!(
        "  Database connection: {}",
        config.database_connection_string
    );
    info!("  Client API keys: {:?}", config.client_api_keys);
    info!("  Management token: {}", config.management_token);

    // Create app state
    let auth = Auth::new(config.jwt_secret.as_bytes());
    let app_state = AppState::new(config.clone(), auth);
    let shared_state = Arc::new(app_state);

    // Build the application router
    let app = create_app(shared_state);

    // Start the server
    let bind_address = format!("{}:{}", config.host, config.port);
    let listener = TcpListener::bind(&bind_address).await?;
    info!("Server starting on http://{}", bind_address);
    axum::serve(listener, app).await?;

    Ok(())
}

// Utility handlers
async fn health_check() -> Json<Value> {
    Json(json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now()
    }))
}
