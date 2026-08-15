"""Integration tests: API endpoints (auth, times, qibla, locations, cities)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_serves_spa(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Waqt" in r.text


def test_times_endpoint_default(client):
    r = client.get(
        "/api/times", params={"latitude": 24.8607, "longitude": 67.0011}
    )
    assert r.status_code == 200
    data = r.json()
    assert set(data["times"]) == {"fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"}
    assert data["method_name"] == "University of Karachi"
    assert data["timezone"] == "Asia/Karachi"


def test_times_invalid_latitude(client):
    r = client.get("/api/times", params={"latitude": 1234, "longitude": 0})
    assert r.status_code == 422


def test_times_invalid_timezone(client):
    r = client.get(
        "/api/times",
        params={"latitude": 24.86, "longitude": 67.0, "timezone": "Not/AZone"},
    )
    assert r.status_code == 422


def test_month_endpoint(client):
    r = client.get(
        "/api/times/month",
        params={"year": 2026, "month": 8, "latitude": 24.86, "longitude": 67.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["days"]) == 31
    assert "fajr" in data["days"][0]["times"]


def test_qibla_endpoint(client):
    r = client.get("/api/qibla", params={"latitude": 24.8607, "longitude": 67.0011})
    assert r.status_code == 200
    data = r.json()
    assert 260 <= data["bearing_degrees"] <= 270
    assert data["bearing_cardinal"] in ("W", "NW", "SW")


def test_methods_endpoint(client):
    r = client.get("/api/methods")
    assert r.status_code == 200
    methods = r.json()
    assert len(methods) >= 15
    assert methods[0]["name"] == "University of Karachi"


def test_cities_search(client):
    r = client.get("/api/cities", params={"query": "karachi"})
    assert r.status_code == 200
    cities = r.json()
    assert any(c["name"] == "Karachi" for c in cities)


def test_register_login_flow(client):
    r = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
    )
    assert r.status_code == 201
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()

    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_register_duplicate_email(client):
    payload = {"name": "A User", "email": "dup@example.com", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"name": "A", "email": "wrong@example.com", "password": "password123"},
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "nope"},
    )
    assert r.status_code == 401


def test_locations_crud(client):
    # unauthenticated -> 401
    assert client.get("/api/locations").status_code == 401

    token = client.post(
        "/api/auth/register",
        json={"name": "Loc", "email": "loc@example.com", "password": "password123"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/api/locations",
        headers=headers,
        json={"name": "Home", "latitude": 24.86, "longitude": 67.0, "timezone": "Asia/Karachi"},
    )
    assert r.status_code == 201
    loc_id = r.json()["id"]

    r = client.get("/api/locations", headers=headers)
    assert len(r.json()) == 1

    # duplicate name -> 409
    r = client.post(
        "/api/locations",
        headers=headers,
        json={"name": "Home", "latitude": 31.5, "longitude": 74.3, "timezone": "Asia/Karachi"},
    )
    assert r.status_code == 409

    # delete
    r = client.delete(f"/api/locations/{loc_id}", headers=headers)
    assert r.status_code == 204
    assert client.get("/api/locations", headers=headers).json() == []


def test_rate_limit_auth(client):
    for i in range(6):
        r = client.post(
            "/api/auth/register",
            json={"name": f"U{i}", "email": f"u{i}@example.com", "password": "password123"},
        )
    # 6th register within the 5/min limit window should be limited
    assert r.status_code == 429
