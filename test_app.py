from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_unregister_participant_endpoint_removes_email():
    initial_count = len(activities["Chess Club"]["participants"])

    response = client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Unregistered michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == initial_count - 1


def test_unregister_participant_requires_existing_activity():
    response = client.delete("/activities/Does Not Exist/unregister?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
