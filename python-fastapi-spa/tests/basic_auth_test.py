import yaml
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from faker import Faker
from main import app

# Initialize Faker to generate random data
fake = Faker()

# --- FIXTURES ---

@pytest.fixture
def client():
    """Fixture to create a fresh TestClient for each test."""
    return TestClient(app)

@pytest.fixture
def test_user(client):
    """
    Fixture to handle the full lifecycle of a test user.

    1.  Generates a random username and password.
    2.  Registers the user via the API.
    3.  Yields the user's details (username, password, access_token) to the test.
    4.  Cleans up by removing the user from users.yaml after the test is complete.
    """
    users_file = Path("users.yaml")
    # Generate random, unique credentials for each test run
    username = fake.user_name()
    password = fake.password()

    try:
        # === SETUP ===
        # Register the new user
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "password": password
        })
        assert register_response.status_code == 201, "Test setup failed: Could not register user."
        token = register_response.json()["access_token"]

        # Provide the user data to the test function
        yield {
            "username": username,
            "password": password,
            "access_token": token
        }

    finally:
        # === TEARDOWN ===
        # This code runs after the test finishes, ensuring the user is removed.
        if not users_file.exists():
            return

        with open(users_file, 'r+') as f:
            try:
                # Load existing users; handle empty or invalid YAML
                data = yaml.safe_load(f) or {}
                users = data.get("users", [])
            except yaml.YAMLError:
                users = []

            # Filter out the user created for this test
            updated_users = [user for user in users if user.get('username') != username]

            # Overwrite the file with the cleaned user list
            f.seek(0)
            yaml.safe_dump({"users": updated_users}, f)
            f.truncate()


# --- REGISTRATION ENDPOINT TESTS ---

def test_register_success(client, test_user):
    """Test that the user registration process within the fixture works correctly."""
    # The 'test_user' fixture already performs a successful registration.
    # We just need to assert that the token it generated is not None.
    assert test_user["access_token"] is not None


def test_register_duplicate_user(client, test_user):
    """Test registration fails if the username already exists."""
    # The 'test_user' fixture has already created a user.
    # Attempt to register a new user with the exact same username.
    response = client.post("/api/v1/auth/register", json={
        "username": test_user["username"],
        "password": fake.password()  # Use a different password
    })
    assert response.status_code == 400, "Should not be able to register a duplicate user."


def test_register_missing_fields(client):
    """Test registration fails if username or password is missing."""
    # Missing password
    response_no_pass = client.post("/api/v1/auth/register", json={"username": fake.user_name()})
    assert response_no_pass.status_code == 422

    # Missing username
    response_no_user = client.post("/api/v1/auth/register", json={"password": fake.password()})
    assert response_no_user.status_code == 422


def test_register_empty_fields(client):
    """Test registration fails if username or password is an empty string."""
    response = client.post("/api/v1/auth/register", json={"username": "", "password": ""})
    assert response.status_code == 422


# --- LOGIN ENDPOINT TESTS ---

def test_login_success(client, test_user):
    """Test a registered user can successfully log in."""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] is not None


def test_login_wrong_password(client, test_user):
    """Test login fails with an incorrect password."""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": "thisIsTheWrongPassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login fails for a user that has not been registered."""
    response = client.post("/api/v1/auth/login", json={
        "username": "nonexistent_user",
        "password": "password123"
    })
    assert response.status_code == 401


def test_login_missing_fields(client):
    """Test login fails if username or password fields are missing."""
    response_no_pass = client.post("/api/v1/auth/login", json={"username": "user"})
    assert response_no_pass.status_code == 422

    response_no_user = client.post("/api/v1/auth/login", json={"password": "pass"})
    assert response_no_user.status_code == 422


# --- WHOAMI ENDPOINT TESTS ---

def test_whoami_success_with_header(client, test_user):
    """Test /whoami returns the correct username with a valid token in the header."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.get("/api/v1/auth/whoami", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]


def test_whoami_success_with_cookie(client, test_user):
    """Test /whoami returns the correct username with a valid token in a cookie."""
    cookies = {"access_token": test_user['access_token']}
    response = client.get("/api/v1/auth/whoami", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]


def test_whoami_no_token(client):
    """Test /whoami fails when no token is provided."""
    response = client.get("/api/v1/auth/whoami")
    assert response.status_code == 401


def test_whoami_invalid_token(client):
    """Test /whoami fails with an invalid or malformed token."""
    headers_invalid = {"Authorization": "Bearer invalid_token"}
    response_invalid = client.get("/api/v1/auth/whoami", headers=headers_invalid)
    assert response_invalid.status_code == 401

    headers_malformed = {"Authorization": "NotBearer invalid_token"}
    response_malformed = client.get("/api/v1/auth/whoami", headers=headers_malformed)
    assert response_malformed.status_code == 401


# --- PRIVATE SECRET ENDPOINT TESTS ---

def test_private_secret_access_success(client, test_user):
    """Test a private endpoint can be accessed with a valid token."""
    # Test with Authorization header
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response_header = client.get("/api/v1/private/secret", headers=headers)
    assert response_header.status_code == 200

    # Test with cookie
    cookies = {"access_token": test_user['access_token']}
    response_cookie = client.get("/api/v1/private/secret", cookies=cookies)
    assert response_cookie.status_code == 200


def test_private_secret_access_failure(client):
    """Test a private endpoint cannot be accessed without proper authentication."""
    # No auth
    response_no_auth = client.get("/api/v1/private/secret")
    assert response_no_auth.status_code == 401

    # Invalid token
    headers_invalid = {"Authorization": "Bearer invalid_token"}
    response_invalid = client.get("/api/v1/private/secret", headers=headers_invalid)
    assert response_invalid.status_code == 401

    # Malformed token
    headers_malformed = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"}
    response_malformed = client.get("/api/v1/private/secret", headers=headers_malformed)
    assert response_malformed.status_code == 401


# --- WEBSOCKET ENDPOINT TESTS ---

def test_websocket_connection_success(client, test_user):
    """Test WebSocket connection succeeds with a valid token and can echo messages."""
    token = test_user["access_token"]
    username = test_user["username"]

    with client.websocket_connect(f"/api/v1/ws?token={token}") as websocket:
        # Check for welcome message
        welcome_message = websocket.receive_text()
        assert f"Hello, Client {username}!" in welcome_message

        # Test message echoing
        test_message = "Hello from the test!"
        websocket.send_text(test_message)
        response_data = websocket.receive_text()
        assert f"Message received: {test_message}" == response_data


def test_websocket_connection_failure(client):
    """Test WebSocket connection fails without a token or with an invalid one."""
    # No token
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/ws"):
            pass

    # Invalid token in query
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/ws?token=invalid_token"):
            pass
            
    # Empty token in query
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/ws?token="):
            pass
