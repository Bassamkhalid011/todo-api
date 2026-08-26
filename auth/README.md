# FlyRank Auth API — W4 Assignment A4

A secure REST API built with **FastAPI** and **Supabase Auth**. Users can sign up, log in, and log out. Protected routes verify JWTs issued by Supabase — no password hashing written by hand.

## What is this?

This is the Week 4 auth assignment for the FlyRank Backend Engineering Internship.  
It implements sign-up, login, logout, and JWT-protected routes using Supabase as the Identity Provider.

---

## Setup

1. **Navigate to the auth folder**
   ```bash
   cd auth
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your Supabase credentials:
   ```bash
   cp .env.example .env
   ```
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_KEY=your_anon_key
   PORT=8000
   ```
   Get these from **Supabase Dashboard → Settings → API**.

4. **Disable email confirmation** (for local testing only)

   Go to **Authentication → Sign In / Providers → Email** and turn **"Confirm email" off**.

---

## Run

```bash
uvicorn main:app --reload --port 8000
```

Server: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

## API Reference

| Method | Route | Auth Required | Description | Status Code |
|--------|-------|:---:|-------------|:---:|
| POST | `/auth/signup` | No | Register a new user | 201 |
| POST | `/auth/login` | No | Login — returns access + refresh token | 200 |
| POST | `/auth/logout` | **Yes** | End the user's session | 204 |
| GET | `/public/info` | No | Public endpoint, open to all | 200 |
| GET | `/protected/profile` | **Yes** | Returns user id, email, created_at | 200 |
| GET | `/protected/dashboard` | **Yes** | Welcome message with user email | 200 |

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK — request succeeded |
| 201 | Created — new user registered |
| 204 | No Content — logout successful |
| 400 | Bad Request — missing email or password |
| 401 | Unauthorized — missing, invalid, or expired token |

**401 vs 403:** `401` = "I don't know who you are" (no valid token). `403` = "I know who you are, but you're not allowed." This API uses 401 for all auth failures.

---

## Swagger UI — Bearer Auth

1. Go to `http://localhost:8000/docs`
2. Call `POST /auth/login` to get an `access_token`
3. Click the **Authorize 🔒** button at the top right
4. Paste your token and click **Authorize**
5. Routes with a lock icon now work from the browser

---

## Architecture

All logic lives in `auth/main.py`:

- `verify_token` — FastAPI `Depends()` function that extracts and verifies the Bearer token via `supabase.auth.get_user()`. Applied to all protected routes — written once, reused everywhere.
- `custom_openapi()` — adds the `BearerAuth` security scheme so Swagger shows the lock icon on protected routes.

```
auth/
├── main.py          # All routes + verify_token dependency + Swagger config
├── requirements.txt
├── .env.example     # Key names with placeholder values (safe to commit)
└── README.md
```
