# Demo Authentication App (Testing Suite)

A structured full-stack demo application designed for practicing **Unit Testing**, **API Testing**, and **UI Testing** using Python and Pytest.

---

## 📁 Project Structure

```
demo_auth_app/
├── app/
│   ├── __init__.py
│   ├── config.py              # App settings & directory paths
│   ├── main.py                # FastAPI app & HTML page routing
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic schemas & validators
│   │   ├── service.py         # Business logic: hashing, password validation, auth
│   │   ├── storage.py         # In-memory thread-safe user repository
│   │   └── routes.py          # API endpoints (/api/register, /api/login, /api/me, /api/logout)
│   ├── static/
│   │   ├── css/style.css      # Modern responsive styling
│   │   └── js/
│   │       ├── auth.js        # Register & Login form handlers
│   │       └── dashboard.js   # Protected dashboard logic & logout
│   └── templates/
│       ├── login.html         # Login page with data-testid attributes
│       ├── register.html      # Register page with data-testid attributes
│       └── dashboard.html     # Authenticated user dashboard
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Fixtures (clean storage, API TestClient, Live UI Server)
│   ├── unit/                  # 1. UNIT TESTING (Isolated business logic)
│   │   ├── __init__.py
│   │   ├── test_validators.py
│   │   └── test_user_service.py
│   ├── api/                   # 2. API TESTING (HTTP endpoints, status codes, schemas)
│   │   ├── __init__.py
│   │   ├── test_api_register.py
│   │   ├── test_api_login.py
│   │   └── test_api_protected.py
│   └── ui/                    # 3. UI TESTING (End-to-End browser tests with Playwright)
│       ├── __init__.py
│       ├── test_ui_register.py
│       ├── test_ui_login.py
│       └── test_ui_dashboard.py
├── pytest.ini                 # Pytest configuration & test markers
├── requirements.txt           # Dependencies
└── run.py                     # Script to run the app manually
```

---

## 🚀 Running the Demo Application

Start the web server locally:

```powershell
cd demo_auth_app
python run.py
```

Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

- Register: `http://127.0.0.1:8000/register`
- Login: `http://127.0.0.1:8000/login`
- Protected Dashboard: `http://127.0.0.1:8000/dashboard`
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

---

## 🧪 Running the Tests

From the `demo_auth_app` directory:

### 1. Run All Tests
```powershell
pytest
```

### 2. Run Only Unit Tests
Unit tests verify business logic (hashing, email/password validation, duplicate prevention) in isolation without a web server:
```powershell
pytest -m unit
```
Or directly by path:
```powershell
pytest tests/unit
```

### 3. Run Only API Tests
API tests verify HTTP response codes (201, 200, 400, 401, 422), JSON payloads, session cookies, and authentication headers:
```powershell
pytest -m api
```
Or directly by path:
```powershell
pytest tests/api
```

### 4. Run Only UI Browser Tests (Playwright)
UI tests launch a headless Chromium browser, navigate pages, fill forms, check DOM error alerts, test redirection, and simulate real user journeys:
```powershell
pytest -m ui
```
Or directly by path:
```powershell
pytest tests/ui
```

#### Run UI Tests with a Visible Browser (Headed mode)
To watch the browser interact in real-time on your screen:
```powershell
pytest tests/ui --headed
```

