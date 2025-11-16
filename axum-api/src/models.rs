use std::collections::HashMap;

use chrono::Utc;
use serde::{Deserialize, Serialize};

use crate::schema;

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct User {
    pub username: String,
    pub password_hash: String,
    pub metadata: HashMap<String, String>
}

impl From<crate::schema::User> for User {
    fn from(src: schema::User) -> Self {
        let mut metadata = HashMap::new();
        metadata.insert("registered_at".to_string(), Utc::now().to_rfc3339());

        Self {
            username: src.username,
            password_hash: src.password_hash,
            metadata,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Project {
    pub id: uuid::Uuid
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Ticket {
    pub id: uuid::Uuid
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Group {
    pub id: uuid::Uuid
}