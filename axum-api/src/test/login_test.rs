use std::sync::Arc;

use axum_test::TestServer;
use serde_json::json;

use crate::{create_app, create_mock_shared_state};

#[tokio::test]
async fn test_health_check() {
    // 1. Create a TestServer from the application router.
    // This creates an in-memory server, avoiding actual networking setup.
    let state = create_mock_shared_state().unwrap();
    let server = TestServer::new(create_app(Arc::new(state))).expect("Failed to create TestServer");

    // 2. Send a GET request to the "/health" endpoint.
    let response = server.get("/health").await;

    // 3. Assert the HTTP status code is 200 OK.
    response.assert_status_ok();

    // 4. Assert the Content-Type header is JSON.
    response.assert_header("Content-Type", "application/json");

    // 5. Assert the JSON body structure and content.
    // We expect the 'status' field to be 'healthy', ignoring the 'timestamp'.
    response.assert_json_contains(&json!({
        "status": "healthy",
        // The assert_json_matches method allows you to check for a subset
        // of the JSON fields, which is perfect for ignoring the dynamic timestamp.
    }));
}
