# Itinerate Backend — Setup Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- pip

---

## 1. Create and activate a virtual environment

```bash
cd backend

python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Create the PostgreSQL database

Open a PostgreSQL shell (`psql`) and run:

```sql
CREATE DATABASE itinerate_db;
CREATE USER itinerate_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE itinerate_db TO itinerate_user;
```

> If you prefer, you can use the default `postgres` superuser and skip
> creating a separate user — just update `.env` accordingly.

## 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your real values:

```
SECRET_KEY=replace-with-a-long-random-string
DEBUG=True

DB_NAME=itinerate_db
DB_USER=itinerate_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

To generate a secure `SECRET_KEY`, run:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. Run database migrations

```bash
python manage.py migrate
```

This creates all tables — Django's built-in auth tables plus
`QuizResult` and `SavedItinerary`.

## 6. Create a superuser (optional)

Gives you access to the Django admin panel at `/admin/`.

```bash
python manage.py createsuperuser
```

## 7. Start the development server

```bash
python manage.py runserver
```

The API is now live at **http://localhost:8000/api/**

---

## API reference

| Method | Endpoint | Auth required | Description |
|--------|----------|:---:|-------------|
| GET | `/api/csrf/` | No | Set CSRF cookie |
| POST | `/api/signup/` | No | Register new user |
| POST | `/api/login/` | No | Log in |
| POST | `/api/logout/` | Yes | Log out |
| GET | `/api/me/` | Yes | Get current user |
| GET | `/api/quiz-results/` | Yes | List quiz results |
| POST | `/api/quiz-results/` | Yes | Save a quiz result |
| GET | `/api/itineraries/` | Yes | List itineraries |
| POST | `/api/itineraries/` | Yes | Save an itinerary |
| GET | `/api/itineraries/<id>/` | Yes | Get one itinerary |
| PUT | `/api/itineraries/<id>/` | Yes | Update an itinerary |
| PATCH | `/api/itineraries/<id>/` | Yes | Partially update |
| DELETE | `/api/itineraries/<id>/` | Yes | Delete an itinerary |

---

## Connecting the frontend

### CSRF token

Django requires a CSRF token on every write request (POST, PUT, PATCH, DELETE)
when the user is logged in. Here is how to handle it in plain JavaScript:

```javascript
// 1. On app load, fetch the CSRF cookie once.
async function initCsrf() {
  await fetch('http://localhost:8000/api/csrf/', {
    credentials: 'include',
  });
}

// 2. Helper to read the cookie value.
function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

// 3. Always pass credentials: 'include' so the browser sends cookies.
//    Always pass X-CSRFToken on write requests.
```

> **Login and signup do not require the CSRF header** — the user has no
> session yet, so CSRF is not enforced.
>
> **Logout and all data endpoints do require it.**

### Example: sign up

```javascript
const res = await fetch('http://localhost:8000/api/signup/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'traveler123',
    email: 'traveler@example.com',
    password: 'securepass123',
  }),
});
const user = await res.json(); // { id, username, email, date_joined }
```

### Example: log in

```javascript
const res = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ username: 'traveler123', password: 'securepass123' }),
});
```

### Example: save a quiz result

```javascript
const res = await fetch('http://localhost:8000/api/quiz-results/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
  },
  credentials: 'include',
  body: JSON.stringify({
    personality_type: 'The Explorer',
    answers: { q1: 'adventure', q2: 'mountains', q3: 'solo' },
  }),
});
```

### Example: save an itinerary

```javascript
const res = await fetch('http://localhost:8000/api/itineraries/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
  },
  credentials: 'include',
  body: JSON.stringify({
    destination: 'Patagonia, Argentina',
    title: '7 Days in Patagonia',
    personality_type: 'The Explorer',
    trip_duration: '7 days',
    itinerary_details: [
      { day: 1, title: 'Arrival', activities: ['Check in', 'Explore town'] },
      { day: 2, title: 'Hiking', activities: ['Torres del Paine trek'] },
    ],
    notes: 'Pack warm layers!',
  }),
});
```

### Example: log out

```javascript
await fetch('http://localhost:8000/api/logout/', {
  method: 'POST',
  headers: { 'X-CSRFToken': getCsrfToken() },
  credentials: 'include',
});
```

---

## Project layout

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── SETUP.md
├── config/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── accounts/            # Auth: signup, login, logout, me
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    └── itineraries/         # Quiz results + saved itineraries
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        └── admin.py
```
