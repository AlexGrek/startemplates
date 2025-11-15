use std::sync::Arc;

use crate::{
    config::{AppConfig, RuntimeConfig},
    controllers::Controller,
    db::{DatabaseInterface, inmemory::InMemoryDatabase},
    middleware::auth::Auth,
};

#[derive(Clone)]
pub struct AppState {
    pub config: Arc<AppConfig>,
    pub auth: Arc<Auth>,
    pub controller: Arc<Controller>,
    pub db: Arc<dyn DatabaseInterface>,
    pub runtime_config: Arc<RuntimeConfig>,
}

impl AppState {
    pub fn new(config: AppConfig, auth: Auth) -> Self {
        let db = Arc::new(InMemoryDatabase::new());

        // cast once to trait object
        let db_trait: Arc<dyn DatabaseInterface> = db.clone();

        Self {
            config: Arc::new(config),
            auth: Arc::new(auth),
            db: db_trait.clone(),
            runtime_config: Arc::new(
                AppConfig::runtime_from_env().unwrap_or(RuntimeConfig::default()),
            ),
            controller: Arc::new(Controller::new(db_trait.clone())),
        }
    }
}
