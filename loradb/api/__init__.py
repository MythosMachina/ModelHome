from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from ..agents.uploader_agent import UploaderAgent
from ..agents.metadata_extractor_agent import MetadataExtractorAgent
from ..agents.indexing_agent import IndexingAgent

router = APIRouter()

uploader = UploaderAgent()
extractor = MetadataExtractorAgent()
indexer = IndexingAgent()

@router.post('/upload')
async def upload(file: UploadFile = File(...)):
    path = uploader.save_file(file.filename, file.file)
    metadata = extractor.extract(Path(path))
    indexer.add_metadata(metadata)
    return metadata

@router.get('/search')
async def search(query: str):
    return indexer.search(query)
