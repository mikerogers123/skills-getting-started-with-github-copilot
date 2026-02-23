import pytest
from fastapi.testclient import TestClient
from src.app import app  # Import the FastAPI app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange: No specific setup needed as activities are predefined

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and response structure
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success(client):
    # Arrange: Define test data
    email = "test@example.com"
    activity = "Chess Club"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check success response and data update
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Verify addition in activities
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found(client):
    # Arrange: Use non-existent activity
    email = "test@example.com"
    activity = "NonExistent"

    # Act: Attempt signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check 404 error
    assert response.status_code == 404


def test_signup_duplicate(client):
    # Arrange: Sign up once first
    email = "duplicate@example.com"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Attempt duplicate signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check 400 error for duplicate
    assert response.status_code == 400


def test_unregister_success(client):
    # Arrange: Sign up first
    email = "unreg@example.com"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Unregister
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check success and removal
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    # Verify removal
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up(client):
    # Arrange: Use email not signed up
    email = "notsigned@example.com"
    activity = "Chess Club"

    # Act: Attempt unregister
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Check 400 error
    assert response.status_code == 400


def test_root_redirect(client):
    # Arrange: No setup

    # Act: GET root
    response = client.get("/")

    # Assert: Check redirect (TestClient follows redirects by default)
    assert response.status_code == 200
    # Since it's a redirect to static, check if content includes expected elements or URL
    assert "index.html" in str(response.url) or b"Mergington High School" in response.content