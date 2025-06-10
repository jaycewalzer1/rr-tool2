import requests
import json

BASE_URL = "http://localhost:80"  # EC2 forwards port 80 to Docker port 5000

def test_server_alive():
    r = requests.get(BASE_URL, timeout=5)
    assert r.status_code == 200
    assert "Welcome" in r.text or "<html" in r.text
    print("✅ Server is up and returned homepage")

def test_404_handling():
    r = requests.get(f"{BASE_URL}/nonexistent")
    assert r.status_code == 404
    print("✅ 404 test passed")

def test_static_file():
    r = requests.get(f"{BASE_URL}/static/css/style.css")  # adjust path
    assert r.status_code in [200, 304]
    assert "text/css" in r.headers["Content-Type"]
    print("✅ Static CSS served correctly")

def test_json_api():
    r = requests.get(f"{BASE_URL}/api/status")  # example route
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    data = r.json()
    assert "status" in data and data["status"] == "ok"
    print("✅ API status endpoint passed")

def test_post_endpoint():
    payload = {"input": "test"}
    r = requests.post(f"{BASE_URL}/api/echo", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("input") == "test"
    print("✅ POST request passed")

def test_signup():
    payload = {
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "StrongPass123!"
    }
    r = requests.post(f"{BASE_URL}/signup", data=payload)
    assert r.status_code in [200, 302]
    print("✅ Signup route reachable")

def test_login_form_loads():
    r = requests.get(f"{BASE_URL}/login")
    assert r.status_code == 200
    assert "<form" in r.text
    print("✅ Login form loads")

def test_login_with_bad_creds():
    payload = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    r = requests.post(f"{BASE_URL}/login", data=payload)
    assert r.status_code in [200, 401, 403]
    assert "Invalid" in r.text or "error" in r.text.lower()
    print("✅ Invalid login correctly rejected")

def test_dashboard_redirect_without_login():
    r = requests.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    assert r.status_code in [302, 401, 403]
    print("✅ Protected route redirects or denies without login")

def test_cors_headers():
    r = requests.options(f"{BASE_URL}/api/echo")
    assert "Access-Control-Allow-Origin" in r.headers or r.status_code == 405
    print("✅ CORS headers present (or method protected)")

def test_content_type_headers():
    r = requests.get(BASE_URL)
    assert "text/html" in r.headers["Content-Type"]
    print("✅ Content-Type headers valid for homepage")

def test_method_not_allowed():
    r = requests.put(BASE_URL)
    assert r.status_code in [405, 404]
    print("✅ Method not allowed handled correctly")

def test_long_input_handling():
    long_input = "x" * 10000
    r = requests.post(f"{BASE_URL}/api/echo", json={"input": long_input})
    assert r.status_code == 200
    assert r.json().get("input") == long_input
    print("✅ Long input handled properly")

def test_missing_field():
    r = requests.post(f"{BASE_URL}/signup", data={})
    assert r.status_code in [200, 400]
    assert "required" in r.text.lower() or "error" in r.text.lower()
    print("✅ Missing field test passed")

def test_rate_limiting_simulation():
    for _ in range(5):
        r = requests.get(BASE_URL)
    assert r.status_code == 200
    print("✅ Server handles repeated requests (no crash)")

