import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="FlyRank Auth API", version="1.0.0")

security = HTTPBearer()


class AuthBody(BaseModel):
    email: str
    password: str


# --- Auth dependency ---

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        result = supabase.auth.get_user(token)
        if result.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return result.user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --- Auth routes ---

@app.post("/auth/signup", status_code=201)
def signup(body: AuthBody):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_up({"email": body.email, "password": body.password})
        if result.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "created_at": str(result.user.created_at),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(body: AuthBody):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="email and password are required")
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
        if result.session is None:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        return {
            "access_token": result.session.access_token,
            "refresh_token": result.session.refresh_token,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")


@app.post("/auth/logout", status_code=204)
def logout(user=Depends(verify_token)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=204)


# --- Public route ---

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


# --- Protected routes ---

@app.get("/protected/profile")
def profile(user=Depends(verify_token)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": str(user.created_at),
    }


@app.get("/protected/dashboard")
def dashboard(user=Depends(verify_token)):
    return {"message": f"Welcome to your dashboard, {user.email}!"}


# --- Custom OpenAPI: adds BearerAuth lock icon to protected routes ---

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    schema.setdefault("components", {})["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    protected_paths = ["/auth/logout", "/protected/profile", "/protected/dashboard"]
    for path, methods in schema.get("paths", {}).items():
        if path in protected_paths:
            for method in methods.values():
                method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Server running on port {port} and connected to Supabase")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
