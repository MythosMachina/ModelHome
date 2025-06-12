from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path

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

@router.get('/search')
async def search(query: str):
    return indexer.search(query)

@router.get('/grid', response_class=HTMLResponse)
async def grid():
    entries = indexer.search('*')
    return frontend.render_grid(entries)


@router.get('/detail/{filename}', response_class=HTMLResponse)
async def detail(filename: str):
    results = indexer.search(f'"{filename}"')
    entry = results[0] if results else {"filename": filename}
    meta = extractor.extract(Path(uploader.upload_dir) / filename)
    entry["metadata"] = meta
    return frontend.render_detail(entry)
