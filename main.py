import os
from pathlib import Path

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import config
from loradb.api import indexer, extractor, frontend
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
    elif request.cookies.get("remember_user_id"):
        uid = request.cookies.get("remember_user_id")
        if uid and uid.isdigit():
            user = auth.get_user_by_id(int(uid))
            if user:
                request.session["user_id"] = user["id"]
    if not user:
        user = {"username": "guest", "role": "guest"}
    request.state.user = user
    if os.environ.get("TESTING"):
        return await call_next(request)
    path = request.url.path
    if (
        path.startswith("/static")
        or path.startswith("/uploads")
        or path.startswith("/login")
        or path == "/showcase"
        or path.startswith("/showcase_detail")
        or path == "/"
        or path.startswith("/models")
        or path.startswith("/images")
    ):
        return await call_next(request)
    if user.get("role") == "guest":
        return RedirectResponse(url="/showcase")
    admin_paths = [
        "/upload",
        "/upload_wizard",
        "/upload_previews",
        "/categories",
        "/assign_category",
        "/unassign_category",
        "/assign_categories",
        "/bulk_assign",
        "/delete_category",
        "/delete",
        "/admin/users",
    ]
    if any(path.startswith(p) for p in admin_paths) and user.get("role") != "admin":
        template = env.get_template("access_denied.html")
        return HTMLResponse(template.render(title="Access Denied", user=user), status_code=403)
    return await call_next(request)


# Add session support after registering the auth middleware so it runs earlier
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and "text/html" in request.headers.get("accept", ""):
        template = env.get_template("404.html")
        return HTMLResponse(
            template.render(title="File Not Found", user=request.state.user),
            status_code=404,
        )
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = env.get_template("index.html")
    return template.render(
        title="Index",
        model_count=indexer.lora_count(),
        image_count=indexer.preview_count(),
        user=request.state.user,
    )


@app.get("/models", response_class=HTMLResponse)
async def model_index(request: Request):
    template = env.get_template("modelindex.html")
    models = indexer.recent_loras(limit=1000)
    return template.render(title="Models", models=models, user=request.state.user)


@app.get("/models/{filename}", response_class=HTMLResponse)
async def model_detail(request: Request, filename: str):
    entry = indexer.get_entry(filename)
    if not entry:
        raise HTTPException(status_code=404, detail="not found")
    file_path = Path(config.UPLOAD_DIR) / filename
    if file_path.exists():
        entry["metadata"] = extractor.extract(file_path)
    previews = frontend._find_previews(Path(filename).stem)
    template = env.get_template("modeldetail.html")
    return template.render(
        title=entry.get("name") or filename,
        model=entry,
        previews=previews,
        user=request.state.user,
    )


@app.get("/images", response_class=HTMLResponse)
async def image_index(request: Request):
    uploads = Path(config.UPLOAD_DIR)
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif"]
    images = []
    for pat in patterns:
        images.extend([p.name for p in uploads.glob(pat)])
    template = env.get_template("imageindex.html")
    return template.render(title="Images", images=sorted(images), user=request.state.user)


@app.get("/images/{image}", response_class=HTMLResponse)
async def image_detail(request: Request, image: str):
    file_path = Path(config.UPLOAD_DIR) / image
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="not found")
    stem = Path(image).stem.split("_")[0]
    model_entry = indexer.get_entry(f"{stem}.safetensors")
    template = env.get_template("imagedetail.html")
    return template.render(
        title=image,
        image=image,
        model=model_entry,
        user=request.state.user,
    )


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    template = env.get_template("login.html")
    return template.render(title="Login", error="", user=None)


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    save_account: str | None = Form(None),
):
    auth = request.app.state.auth
    if auth.verify_user(username, password):
        user = auth.get_user(username)
        request.session["user_id"] = user["id"]
        response = RedirectResponse(url="/", status_code=303)
        if save_account:
            response.set_cookie(
                "remember_user_id",
                str(user["id"]),
                max_age=60 * 60 * 24 * 7,
                httponly=True,
            )
        else:
            response.delete_cookie("remember_user_id")
        return response
    template = env.get_template("login.html")
    return template.render(title="Login", error="Invalid credentials", user=None)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("remember_user_id")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9090)
