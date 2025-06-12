# LoRA Database Web Interface

This project provides a minimal FastAPI application for organising LoRA files (`.safetensors`) along with preview images.  It allows uploading new LoRA models, automatically extracts their metadata and stores it in a small SQLite based search index.  A simple gallery interface lets you browse the models, search by name or tag and download or remove files.

## Features

- **Upload LoRA files** – multiple `.safetensors` files can be uploaded at once.
- **Upload preview archives** – a ZIP file containing preview images is extracted and matched to the corresponding LoRA by filename.
- **Metadata extraction** – basic metadata is read from each safetensors file and stored in a full text search (FTS5) table.
- **Searchable gallery** – browse all indexed LoRAs in a grid view and filter by query.
- **Detail view** – see all previews, metadata and a download link for a single LoRA.
- **File removal** – delete LoRA files or individual preview images from the interface.

## Project layout

```
loradb/
├── agents/            # upload, metadata and search logic
├── api/               # FastAPI routes
├── static/            # CSS for the HTML templates
├── templates/         # Jinja2 templates for the web pages
├── uploads/           # stored LoRA files and preview images
└── search_index/      # SQLite database for the search index
main.py                # application entry point
config.py              # path configuration used by the app
requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository and change into the project folder:

   ```bash
   git clone https://github.com/AsaTyr2018/MyLora.git
   cd MyLora
   ```

2. Create a virtual environment (optional but recommended) and install the dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the web application:

   ```bash
   python main.py
   ```

   The interface is available on [http://localhost:5000](http://localhost:5000).

## Usage

- **Upload models**: open `/upload` and select one or more `.safetensors` files.  Each file is stored in `loradb/uploads` and indexed automatically.
- **Upload previews**: open `/upload_previews` to upload a ZIP containing images.  Files named `mylora.png`, `mylora_1.png`, ... will be placed next to `mylora.safetensors` and shown in the gallery.
- **Browse and search**: the `/grid` page lists all indexed LoRAs. Use the search box to filter by filename or tags.
- **Detail view**: click a LoRA in the gallery to view all previews and metadata.  A download button is provided to retrieve the original file.
- **Delete files**: tick the checkboxes in the gallery or detail view and press *Remove Selected* to delete the chosen files.

The web pages use Bootstrap via a CDN and are rendered with Jinja2 templates.  The application keeps all data locally on disk in the `loradb` directory.

---

MIT License
