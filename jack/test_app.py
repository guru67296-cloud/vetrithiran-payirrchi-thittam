def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_api(client):
    response = client.post(
        "/api/workouts",
        json={
            "user_id": "TEST100",
            "name": "Test User",
            "age": 25,
            "weight": 70,
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "TEST100"
    assert "Day 1" in data["workout_plan"]
    assert data["nutrition_tip"]


def test_feedback_api(client):
    client.post(
        "/api/workouts",
        json={
            "user_id": "TEST200",
            "name": "Test User",
            "age": 30,
            "weight": 65,
            "goal": "general wellness",
            "intensity": "low",
        },
    )

    response = client.post(
        "/api/workouts/TEST200/feedback",
        json={"feedback": "Add more cardio and another recovery day."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["updated"] is True
    assert data["feedback"] == "Add more cardio and another recovery day."


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text
