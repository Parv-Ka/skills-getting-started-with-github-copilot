from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_data = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_data)


client = TestClient(app)


def test_get_activities_returns_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant_and_returns_message():
    # Arrange
    url = "/activities/Chess%20Club/signup?email=test@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@example.com for Chess Club"
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_returns_400_for_duplicate_registration():
    # Arrange
    url = "/activities/Chess%20Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_missing_activity():
    # Arrange
    url = "/activities/Nonexistent/signup?email=test@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    url = "/activities/Chess%20Club/unregister?email=michael@mergington.edu"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_returns_404_for_missing_participant():
    # Arrange
    url = "/activities/Chess%20Club/unregister?email=unknown@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_returns_404_for_missing_activity():
    # Arrange
    url = "/activities/Nonexistent/unregister?email=test@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
