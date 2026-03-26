# FlightCRM

Minimal CRM for flight ticket sales agents. Manage customers, track orders, handle follow-up tasks, and query business data via AI chat.

## Tech Stack

- **Backend**: Python Flask REST API
- **Frontend**: Static HTML/CSS/JS (no frameworks)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Railway (2 services: backend + frontend)

## Project Structure

```
backend/
  app.py              # Flask entry point
  config.py           # Environment config
  db.py               # PostgreSQL connection pool
  seed.py             # Sample data seeder
  routes/             # API endpoints (customers, orders, tasks, chat)
  services/           # Business logic layer
frontend/
  index.html          # Customers list + dashboard
  customer.html       # Customer detail (orders + tasks)
  chat.html           # AI chat assistant
  css/styles.css      # Design system
  js/                 # API client + page logic
schema.sql            # Database schema
```

## Setup

### 1. Database

Create a Supabase project and run `schema.sql` in the SQL Editor.

### 2. Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY
pip install -r requirements.txt
python seed.py          # Load sample data
python -m backend.app   # Start dev server on port 5000
```

### 3. Frontend

Open `frontend/index.html` in a browser, or serve with any static file server:

```bash
cd frontend
python -m http.server 3000
```

## API Endpoints

### Customers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | List all (filter: `?status=new`) |
| GET | `/customers/late` | Overdue follow-ups |
| GET | `/customers/:id` | Single customer |
| POST | `/customers` | Create |
| PUT | `/customers/:id` | Update |
| DELETE | `/customers/:id` | Delete |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/:id/orders` | List by customer |
| POST | `/customers/:id/orders` | Create |
| PUT | `/orders/:id` | Update |
| DELETE | `/orders/:id` | Delete |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/:id/tasks` | List by customer |
| POST | `/customers/:id/tasks` | Create |
| PUT | `/tasks/:id` | Update |
| DELETE | `/tasks/:id` | Delete |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | `{ "message": "..." }` returns AI answer |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `OPENAI_API_KEY` | No | Enables AI chat feature |
| `ALLOWED_ORIGINS` | No | CORS origins (default: `*`) |

## Deploy to Railway

**Backend service** (from `backend/` directory):
- Buildpack: Python
- Start command: `gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 2`
- Set env vars: `DATABASE_URL`, `OPENAI_API_KEY`, `ALLOWED_ORIGINS`

**Frontend service** (from `frontend/` directory):
- Builder: Dockerfile
- Set env var: `API_BASE_URL` = backend service URL
