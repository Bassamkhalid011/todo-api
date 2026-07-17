# Task API

> A production-style REST API for managing tasks — built with FastAPI & PostgreSQL.

---

## What is this?

A full CRUD API that lets you create, read, update, and delete tasks.
Built as part of the **FlyRank Backend Engineering Track — Week 2**.

Tasks are stored in **PostgreSQL** running in Docker.
Data persists across restarts.

---

## Architecture

This project uses a layered architecture — Repository Pattern:

| Layer | Responsibility |
|-------|---------------|
| **Routes** | HTTP only — request/response |
| **Service** | Business logic — validation rules |
| **Repository** | Data storage — PostgreSQL or Memory |

Swapping from in-memory to PostgreSQL required changing **only one line** in `main.py`.
Service and routes were completely unchanged — that's the architecture proving itself.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| FastAPI | Web framework |
| Pydantic | Data validation |
| Uvicorn | ASGI server |
| PostgreSQL | Database |
| Docker | Containerization |
| psycopg2 | PostgreSQL driver |

---

## How to Run

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/task-api.git
cd task-api
```

**2. Setup environment**
```bash
cp .env.example .env
```

**3. Start everything with one command**
```bash
docker compose up
```

App runs on: `http://127.0.0.1:8000`

---

## API Endpoints

| Method | Path | Description | Status Code |
|--------|------|-------------|-------------|
| `GET` | `/` | API information | `200` |
| `GET` | `/health` | Server health check | `200` |
| `GET` | `/tasks` | Get all tasks | `200` |
| `GET` | `/tasks/{id}` | Get a single task by ID | `200` |
| `POST` | `/tasks` | Create a new task | `201` |
| `PUT` | `/tasks/{id}` | Update an existing task | `200` |
| `DELETE` | `/tasks/{id}` | Delete a task | `204` |

---

## Example Request & Response

```bash
curl -i http://127.0.0.1:8000/tasks
```
```
HTTP/1.1 200 OK
content-type: application/json

[{"id":1,"title":"Buy milk","done":false}]
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | Deleted — no content returned |
| `400` | Bad Request — invalid input |
| `404` | Not Found — task doesn't exist |

---

## Validation Rules

- `title` is required for POST and PUT
- Empty or blank titles are rejected with `400 Bad Request`
- Unknown task IDs return `404 Not Found`

---

## Persistence Proof

1. Started the app with `docker compose up`
2. Created tasks via POST `/tasks`
3. Stopped containers with `CTRL+C`
4. Restarted with `docker compose up`
5. GET `/tasks` returned the same tasks ✅

Data survives full container + app restart.

---

## Interactive Docs (Swagger UI)

FastAPI generates interactive documentation automatically.

👉 Visit: `http://127.0.0.1:8000/docs`

![Swagger UI](swagger.png)

---

## Project Structure

```
task-api/
├── main.py              # FastAPI app + routes
├── models.py            # Pydantic models
├── service.py           # Business logic
├── repository/
│   ├── base.py          # Abstract interface
│   ├── memory.py        # In-memory implementation
│   └── postgres.py      # PostgreSQL implementation
├── init.sql             # Table creation
├── docker-compose.yml   # App + DB together
├── requirements.txt     # Dependencies
├── .env                 # Secrets (gitignored)
└── .env.example         # Template for .env
```

---

## Author

**Bassam Khalid**  
FlyRank Backend Engineering Track — Week 2