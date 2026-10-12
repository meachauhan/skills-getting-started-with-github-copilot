from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_seeded_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "michael@mergington.edu" in response.json()[expected_activity]["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    original_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == original_count + 1


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = deepcopy(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new-student@mergington.edu"
    original_activities = deepcopy(app_module.activities)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert app_module.activities == original_activities


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"
    original_participants = deepcopy(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == original_participants


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    original_activities = deepcopy(app_module.activities)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert app_module.activities == original_activities