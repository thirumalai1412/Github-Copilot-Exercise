from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

BASELINE_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    activities.clear()
    activities.update(deepcopy(BASELINE_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(BASELINE_ACTIVITIES))


def test_get_activities_returns_activity_payload():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_student_email():
    original_participants = activities["Chess Club"]["participants"].copy()

    try:
        email = "qa-joiner@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")

        assert response.status_code == 200
        payload = response.json()
        assert payload["message"] == f"Signed up {email} for Chess Club"
        assert email in activities["Chess Club"]["participants"]
    finally:
        activities["Chess Club"]["participants"] = original_participants


def test_signup_rejects_duplicate_student():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Student is already signed up for this activity"


def test_unregister_activity_endpoint_removes_email():
    original_participants = activities["Chess Club"]["participants"].copy()

    try:
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")

        assert response.status_code == 200
        payload = response.json()
        assert payload["message"] == f"Unregistered {email} from Chess Club"
        assert email not in activities["Chess Club"]["participants"]
    finally:
        activities["Chess Club"]["participants"] = original_participants


def test_unregister_rejects_unknown_activity():
    response = client.delete("/activities/Does Not Exist/unregister?email=test@example.com")

    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "Activity not found"
