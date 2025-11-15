use crate::{
    error::AppError,
    schema::{LoginRequest, LoginResponse, RegisterRequest, User},
    state::AppState,
};
use axum::{
    extract::{Json, State},
    http::StatusCode,
    response::IntoResponse,
};
use std::sync::Arc;

pub async fn register(
    State(app_state): State<Arc<AppState>>,
    Json(req): Json<RegisterRequest>,
) -> Result<impl IntoResponse, AppError> {
    let hashed_password = app_state.auth.hash_password(&req.password)?;

    let user = User {
        username: req.email.clone(),
        password_hash: hashed_password,
    };

    let uid = user.username.clone();

    app_state.db.users().create_user(user).await?;

    log::info!(
        "Register event -> {}",
        format!("User with ID {:?} created: {}", &uid, &req.email)
    );

    Ok(StatusCode::OK)
}

pub async fn login(
    State(app_state): State<Arc<AppState>>,
    Json(req): Json<LoginRequest>,
) -> Result<impl IntoResponse, AppError> {
    let user = app_state.db.users().get_user(&req.email).await?;

    if !app_state
        .auth
        .verify_password(&req.password, &user.password_hash)?
    {
        return Err(AppError::Authorization("Unauthorized".to_string()));
    }

    let token = app_state.auth.create_token(&user.username)?;

    log::info!(
        "Auth event -> {}",
        format!("User logged in: {}", &user.username)
    );

    Ok(Json(LoginResponse { token: token.0 }))
}
