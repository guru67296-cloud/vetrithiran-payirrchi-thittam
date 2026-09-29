# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application that generates personalized 7-day workout plans and nutrition/recovery tips with Google Gemini. Users can submit feedback and regenerate an updated plan. An admin page lists stored users and plans.

## Architecture

- Frontend: HTML5, Jinja2, CSS, small JavaScript helpers
- Backend: FastAPI + Uvicorn
- Validation: Pydantic
- Database: SQLite + SQLAlchemy ORM
- AI: Google Gemini through the current `google-genai` Python SDK
- Testing: pytest + FastAPI TestClient
- Configuration: `.env`

The original documentation mentions Gemini 1.5 Pro and Gemini Flash. Those model names are historical. This implementation keeps the two logical AI roles (`workout` and `tip`) but makes the actual model names configurable with environment variables. The defaults are current, configurable Gemini models.

## 1. Requirements

- Python 3.11+ recommended
- A Google Gemini API key
- VS Code (recommended)
- Internet access for Gemini API calls

## 2. Windows setup in VS Code

Open the project folder in VS Code and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Edit `.env` and set:

```env
GEMINI_API_KEY=your_real_key_here
```

## 3. Run

```powershell
uvicorn app.main:app --reload
```

Open:

- Web app: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin dashboard: http://127.0.0.1:8000/view-all-users

## 4. Run tests

```powershell
pytest -q
```

The tests use the application's deterministic fallback AI mode and do not require a real Gemini key.

## 5. API endpoints

### Health

`GET /api/health`

### Generate a plan

`POST /api/workouts`

JSON:

```json
{
  "user_id": "FB1001",
  "name": "Alex",
  "age": 25,
  "weight": 70,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### Update a plan

`POST /api/workouts/{user_id}/feedback`

JSON:

```json
{
  "feedback": "Add more cardio and one extra rest day."
}
```

### Get user

`GET /api/users/{user_id}`

### Get all users

`GET /api/users`

## 6. AI configuration

`.env` supports:

```env
GEMINI_API_KEY=...
GEMINI_WORKOUT_MODEL=gemini-2.5-flash
GEMINI_TIP_MODEL=gemini-2.5-flash
AI_FALLBACK_ENABLED=true
```

If `GEMINI_API_KEY` is absent and fallback is enabled, the app still runs with deterministic demo responses. This is useful for frontend development and tests. For actual AI-generated plans, configure a valid key.

## 7. Fitness safety

FitBuddy is a wellness planning tool, not a medical service. Generated content includes a safety note and avoids diagnosis, medication advice, extreme dieting, or unsafe exercise prescriptions. Users with injuries, medical conditions, pregnancy, or other special circumstances should consult an appropriately qualified professional.

## 8. Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── workout_generator.py
│   │   ├── nutrition_generator.py
│   │   └── plan_updater.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── result.html
│   │   └── all_users.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 9. Git

```powershell
git init
git add .
git commit -m "Initial FitBuddy application"
```

Do not commit `.env`, the SQLite database, or `.venv`.
