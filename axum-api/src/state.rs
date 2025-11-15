use std::sync::Arc;

use crate::{
    config::{AppConfig, RuntimeConfig},
    db::{DatabaseInterface, inmemory::InMemoryDatabase},
    middleware::{auth::Auth, user_utils::UserUtils},
};

#[derive(Clone)]
pub struct AppState {
    pub config: Arc<AppConfig>,
    pub auth: Arc<Auth>,
    pub users: Arc<UserUtils>,
    pub db: Arc<dyn DatabaseInterface>,
    pub runtime_config: Arc<RuntimeConfig>,
}

impl AppState {
    pub fn new(config: AppConfig, auth: Auth) -> Self {
        Self {
            config: Arc::new(config),
            auth: Arc::new(auth),
            users: Arc::new(UserUtils {}),
            db: Arc::new(InMemoryDatabase::new()),
            runtime_config: Arc::new(
                AppConfig::runtime_from_env().unwrap_or(RuntimeConfig::default()),
            ),
        }
    }
}
