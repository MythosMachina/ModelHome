from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import config
from loradb.api import router as api_router

app = FastAPI(title="LoRA Database")

app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

UPLOAD_DIR = Path(config.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def index():
    return "<h1>LoRA Database</h1><p>Upload endpoint: /upload</p><p><a href='/grid'>View Gallery</a></p>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
