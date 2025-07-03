from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import config
from loradb.api import router as api_router, indexer

app = FastAPI(title="LoRA Database")

app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")

UPLOAD_DIR = Path(config.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR))

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
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
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
