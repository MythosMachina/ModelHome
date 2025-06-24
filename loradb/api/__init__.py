from fastapi import APIRouter, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
import random

import config

from ..agents.uploader_agent import UploaderAgent
from ..agents.metadata_extractor_agent import MetadataExtractorAgent
from ..agents.indexing_agent import IndexingAgent
from ..agents.frontend_agent import FrontendAgent

router = APIRouter()

uploader = UploaderAgent()
extractor = MetadataExtractorAgent()
indexer = IndexingAgent()
frontend = FrontendAgent(Path(uploader.upload_dir), Path(config.TEMPLATE_DIR))


@router.get('/upload', response_class=HTMLResponse)
async def upload_form():
    """Render HTML form for file uploads."""
    return frontend.env.get_template('upload.html').render(title='Upload')

@router.post('/upload')
async def upload(request: Request, files: list[UploadFile] = File(...)):
    saved_paths = uploader.save_files(files)
    results = []
    for path in saved_paths:
        meta = extractor.extract(Path(path))
        indexer.add_metadata(meta)
        results.append(meta)
    # HTML uploads redirect to gallery
    if 'text/html' in request.headers.get('accept', ''):
        return RedirectResponse(url='/grid', status_code=303)
    return results


@router.get('/upload_previews', response_class=HTMLResponse)
async def upload_previews_form():
    """Form for uploading preview zip files."""
    return frontend.env.get_template('upload_previews.html').render(title='Upload Previews')


@router.post('/upload_previews')
async def upload_previews(request: Request, file: UploadFile = File(...)):
    uploader.save_preview_zip(file)
    if 'text/html' in request.headers.get('accept', ''):
        return RedirectResponse(url='/grid', status_code=303)
    return {"status": "ok"}

@router.get('/search')
async def search(query: str, limit: int | None = None, offset: int = 0):
    return indexer.search(query, limit=limit, offset=offset)

@router.get('/grid_data')
async def grid_data(q: str = '*', category: int | None = None, offset: int = 0, limit: int = 50):
    if not q:
        q = '*'
    if category:
        entries = indexer.search_by_category(category, q, limit=limit, offset=offset)
    else:
        entries = indexer.search(q, limit=limit, offset=offset)
    for e in entries:
        e['categories'] = indexer.get_categories_for(e['filename'])
        stem = Path(e.get('filename', '')).stem
        previews = frontend._find_previews(stem)
        e['preview_url'] = random.choice(previews) if previews else None
    return entries


@router.get('/categories')
async def list_categories():
    return indexer.list_categories()


@router.post('/categories')
async def create_category(name: str = Form(...)):
    cid = indexer.create_category(name)
    return {'id': cid}


@router.post('/assign_category')
async def assign_category(request: Request, filename: str = Form(...), category_id: int = Form(...)):
    indexer.assign_category(filename, category_id)
    if 'text/html' in request.headers.get('accept', ''):
        return RedirectResponse(url=f'/detail/{filename}', status_code=303)
    return {'status': 'ok'}

@router.get('/grid', response_class=HTMLResponse)
async def grid(request: Request):
    query = request.query_params.get('q', '*')
    if not query:
        query = '*'
    category = request.query_params.get('category')
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    categories = indexer.list_categories()
    if category:
        entries = indexer.search_by_category(int(category), query, limit=limit, offset=offset)
    else:
        entries = indexer.search(query, limit=limit, offset=offset)
    for e in entries:
        e['categories'] = indexer.get_categories_for(e['filename'])
    return frontend.render_grid(
        entries,
        query=query if query != '*' else '',
        categories=categories,
        selected_category=category or '',
        limit=limit,
    )


@router.get('/detail/{filename}', response_class=HTMLResponse)
async def detail(filename: str):
    results = indexer.search(f'"{filename}"')
    entry = results[0] if results else {"filename": filename}
    meta = extractor.extract(Path(uploader.upload_dir) / filename)
    entry["metadata"] = meta
    entry["categories"] = indexer.get_categories_for(filename)
    categories = indexer.list_categories()
    return frontend.render_detail(entry, categories=categories)


@router.post('/delete')
async def delete_files(request: Request):
    """Delete selected LoRA or preview files."""
    form = await request.form()
    files = form.getlist('files')
    deleted = []
    for fname in files:
        if fname.endswith('.safetensors'):
            uploader.delete_lora(fname)
            indexer.remove_metadata(fname)
        else:
            uploader.delete_preview(fname)
        deleted.append(fname)
    if 'text/html' in request.headers.get('accept', ''):
        return RedirectResponse(url='/grid', status_code=303)
    return {'deleted': deleted}
