import random
import re
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

import config

from ..agents.frontend_agent import FrontendAgent
from ..agents.indexing_agent import IndexingAgent
from ..agents.metadata_extractor_agent import MetadataExtractorAgent
from ..agents.uploader_agent import UploaderAgent

router = APIRouter()

uploader = UploaderAgent()
extractor = MetadataExtractorAgent()
indexer = IndexingAgent()
frontend = FrontendAgent(Path(uploader.upload_dir), Path(config.TEMPLATE_DIR))
uploader.frontend = frontend

# Regular expression for valid LoRA filenames. Only allow alphanumerics,
# dashes and underscores ending with the ``.safetensors`` extension. This
# prevents path traversal and protocol injections in redirect URLs.
_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.-]+\.safetensors$", re.ASCII)


def _validate_filename(filename: str) -> str:
    """Return ``filename`` if it looks safe, otherwise raise ``HTTPException``."""
    cleaned = Path(filename).name
    if cleaned != filename or cleaned.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not _SAFE_FILENAME_RE.fullmatch(cleaned):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return cleaned


@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Render HTML form for file uploads."""
    user = request.state.user
    return frontend.env.get_template("upload.html").render(title="Upload", user=user)


@router.get("/upload_wizard", response_class=HTMLResponse)
async def upload_wizard_form(request: Request):
    """Combined upload form for LoRA and previews."""
    user = request.state.user
    return frontend.env.get_template("upload_wizard.html").render(
        title="Upload Wizard", user=user
    )


@router.post("/upload")
async def upload(request: Request, files: list[UploadFile] = File(...)):
    try:
        saved_paths = uploader.save_files(files)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    results = []
    for path in saved_paths:
        meta = extractor.extract(Path(path))
        indexer.add_metadata(meta)
        results.append(meta)
    # HTML uploads redirect to gallery
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/grid", status_code=303)
    return results


@router.get("/upload_previews", response_class=HTMLResponse)
async def upload_previews_form(request: Request, lora: str | None = None):
    """Form for uploading preview images or zip files.

    If ``lora`` is provided, the form will target that specific LoRA and allow
    uploading additional preview images. Otherwise a generic upload form for a
    preview ZIP is shown.
    """
    template = frontend.env.get_template("upload_previews.html")
    return template.render(title="Upload Previews", lora=lora, user=request.state.user)


@router.post("/upload_previews")
async def upload_previews(
    request: Request,
    files: list[UploadFile] = File(...),
    lora: str | None = Form(None),
):
    if len(files) == 1 and files[0].filename.lower().endswith(".zip") and lora is None:
        stem = Path(files[0].filename).stem
        uploader.save_preview_zip(files[0])
    else:
        if not lora:
            return {"error": "missing lora"}
        stem = lora
        uploader.save_preview_files(stem, files)
    frontend.refresh_preview_cache(stem)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/grid", status_code=303)
    return {"status": "ok"}


@router.get("/search")
async def search(query: str, limit: int | None = None, offset: int = 0):
    return indexer.search(query, limit=limit, offset=offset)


@router.get("/grid_data")
async def grid_data(
    q: str = "*", category: int | None = None, offset: int = 0, limit: int = 50
):
    if not q:
        q = "*"
    if category is not None:
        entries = indexer.search_by_category(category, q, limit=limit, offset=offset)
    else:
        entries = indexer.search(q, limit=limit, offset=offset)
    for e in entries:
        e["categories"] = indexer.get_categories_for(e["filename"])
        stem = Path(e.get("filename", "")).stem
        previews = frontend._find_previews(stem)
        e["preview_url"] = random.choice(previews) if previews else None
    return entries


@router.get("/showcase", response_class=HTMLResponse)
async def showcase(request: Request):
    """Public showcase page listing models in the "Public viewing" category."""
    public_id = indexer.create_category("Public viewing")
    entries = indexer.search_by_category(public_id, limit=100)
    return frontend.render_showcase(entries, user=request.state.user)


@router.get("/showcase_detail/{filename}", response_class=HTMLResponse)
async def showcase_detail(request: Request, filename: str):
    """Guest accessible detail view for ``filename``."""
    results = indexer.search(f'"{filename}"')
    entry = results[0] if results else {"filename": filename}
    return frontend.render_showcase_detail(entry, user=request.state.user)


@router.get("/categories")
async def list_categories():
    return indexer.list_categories()


@router.post("/categories")
async def create_category(request: Request, name: str = Form(...)):
    """Create a new category and optionally redirect for HTML forms."""
    cid = indexer.create_category(name)
    if "text/html" in request.headers.get("accept", ""):
        referer = request.headers.get("referer", "/grid")
        return RedirectResponse(url=referer, status_code=303)
    return {"id": cid}


@router.post("/assign_category")
async def assign_category(
    request: Request, filename: str = Form(...), category_id: int = Form(...)
):
    fname = _validate_filename(filename)
    indexer.assign_category(fname, category_id)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url=f"/detail/{fname}", status_code=303)
    return {"status": "ok"}


@router.post("/unassign_category")
async def unassign_category(
    request: Request, filename: str = Form(...), category_id: int = Form(...)
):
    """Remove ``filename`` from the given ``category_id``."""
    fname = _validate_filename(filename)
    indexer.unassign_category(fname, category_id)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url=f"/detail/{fname}", status_code=303)
    return {"status": "ok"}


@router.post("/assign_categories")
async def assign_categories(
    request: Request,
    files: list[str] = Form(...),
    category_id: int | None = Form(None),
    new_category: str | None = Form(None),
):
    if new_category:
        cid = indexer.create_category(new_category)
    elif category_id is not None:
        cid = category_id
    else:
        raise HTTPException(status_code=400, detail="missing category")
    cleaned = [_validate_filename(f) for f in files]
    for fname in cleaned:
        indexer.assign_category(fname, cid)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/grid", status_code=303)
    return {"status": "ok"}


@router.post("/bulk_assign", response_class=HTMLResponse)
async def bulk_assign(request: Request):
    form = await request.form()
    files = form.getlist("files")
    categories = indexer.list_categories()
    return frontend.render_bulk_assign(files, categories, user=request.state.user)


@router.get("/category_admin", response_class=HTMLResponse)
async def category_admin(request: Request):
    """Display the category administration page."""
    categories = indexer.list_categories_with_counts()
    return frontend.render_category_admin(categories, user=request.state.user)


@router.post("/delete_category")
async def delete_category(request: Request, category_id: int = Form(...)):
    indexer.delete_category(category_id)
    if "text/html" in request.headers.get("accept", ""):
        referer = request.headers.get("referer", "/category_admin")
        return RedirectResponse(url=referer, status_code=303)
    return {"status": "ok"}


@router.get("/grid", response_class=HTMLResponse)
async def grid(request: Request):
    query = request.query_params.get("q", "*")
    if not query:
        query = "*"
    category = request.query_params.get("category")
    limit = int(request.query_params.get("limit", 50))
    offset = int(request.query_params.get("offset", 0))
    categories = indexer.list_categories()
    if category:
        entries = indexer.search_by_category(
            int(category), query, limit=limit, offset=offset
        )
    else:
        entries = indexer.search(query, limit=limit, offset=offset)
    for e in entries:
        e["categories"] = indexer.get_categories_for(e["filename"])
    return frontend.render_grid(
        entries,
        query=query if query != "*" else "",
        categories=categories,
        selected_category=category or "",
        limit=limit,
        user=request.state.user,
    )


@router.get("/detail/{filename}", response_class=HTMLResponse)
async def detail(request: Request, filename: str):
    file_path = Path(uploader.upload_dir) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="not found")
    results = indexer.search(f'"{filename}"')
    entry = results[0] if results else {"filename": filename}
    meta = extractor.extract(file_path)
    entry["metadata"] = meta
    entry["categories"] = indexer.get_categories_with_ids(filename)
    categories = indexer.list_categories()
    return frontend.render_detail(entry, categories=categories, user=request.state.user)


@router.post("/delete")
async def delete_files(request: Request):
    """Delete selected LoRA or preview files."""
    form = await request.form()
    files = form.getlist("files")
    deleted = []
    for fname in files:
        if fname.endswith(".safetensors"):
            uploader.delete_lora(fname)
            indexer.remove_metadata(fname)
        else:
            uploader.delete_preview(fname)
        frontend.invalidate_preview_cache(Path(fname).stem)
        deleted.append(fname)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/grid", status_code=303)
    return {"deleted": deleted}


@router.get("/admin/users", response_class=HTMLResponse)
async def user_admin(request: Request):
    auth = request.app.state.auth
    users = auth.list_users()
    return frontend.render_user_admin(users, user=request.state.user)


@router.post("/admin/users/add")
async def add_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
):
    auth = request.app.state.auth
    auth.create_user(username, password, role)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/admin/users", status_code=303)
    return {"status": "ok"}


@router.post("/admin/users/delete")
async def delete_user(request: Request, username: str = Form(...)):
    auth = request.app.state.auth
    auth.delete_user(username)
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/admin/users", status_code=303)
    return {"status": "ok"}
