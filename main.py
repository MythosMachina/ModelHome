import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from starlette.middleware.sessions import SessionMiddleware

import config
from loradb.api import indexer
from loradb.api import router as api_router
from loradb.auth import AuthManager

app = FastAPI(title="LoRA Database")
app.state.auth = AuthManager()

app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")

UPLOAD_DIR = Path(config.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR))

app.include_router(api_router)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth = request.app.state.auth
    user = None
    if request.session.get("user_id"):
        user = auth.get_user_by_id(request.session["user_id"])
    request.state.user = user
    if os.environ.get("TESTING"):
        return await call_next(request)
    path = request.url.path
    if (
        path in {"/login", "/logout"}
        or path.startswith("/static")
        or path.startswith("/uploads")
    ):
        return await call_next(request)
    if not user:
        return RedirectResponse(url="/login")
    admin_paths = [
        "/upload",
        "/upload_wizard",
        "/upload_previews",
        "/categories",
        "/assign_category",
        "/unassign_category",
        "/assign_categories",
        "/bulk_assign",
        "/category_admin",
        "/delete_category",
        "/delete",
        "/admin/users",
    ]
    if any(path.startswith(p) for p in admin_paths) and user.get("role") != "admin":
        return HTMLResponse("Forbidden", status_code=403)
    return await call_next(request)


# Add session support after registering the auth middleware so it runs earlier
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    template = env.get_template("dashboard.html")
    stats = {
        "lora_count": indexer.lora_count(),
        "preview_count": indexer.preview_count(),
        "category_count": indexer.category_count(),
        "storage_volume": indexer.storage_volume(),
        "top_categories": indexer.top_categories(limit=20),
    }
    recent_categories = indexer.recent_categories(limit=5)
    recent_loras = indexer.recent_loras(limit=5)
    return template.render(
        title="Dashboard",
        stats=stats,
        recent_categories=recent_categories,
        recent_loras=recent_loras,
        user=request.state.user,
    )


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    template = env.get_template("login.html")
    return template.render(title="Login", error="", user=None)


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    auth = request.app.state.auth
    if auth.verify_user(username, password):
        user = auth.get_user(username)
        request.session["user_id"] = user["id"]
        return RedirectResponse(url="/", status_code=303)
    template = env.get_template("login.html")
    return template.render(title="Login", error="Invalid credentials", user=None)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
