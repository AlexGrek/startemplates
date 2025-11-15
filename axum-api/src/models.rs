use serde::{Deserialize, Serialize};

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