# LoRA Database Web Interface

This project provides a minimal FastAPI application for organising LoRA files (`.safetensors`) along with preview images.  It allows uploading new LoRA models, automatically extracts their metadata and stores it in a small SQLite based search index.  A simple gallery interface lets you browse the models, search by name or tag and download or remove files.

## Preview
![grafik](https://github.com/user-attachments/assets/7dee8a00-085b-40f0-a545-9d171833e69b)

## Features

- **Upload LoRA files** – multiple `.safetensors` files can be uploaded at once.
- **Upload preview archives** – a ZIP file containing preview images is extracted and matched to the corresponding LoRA by filename.
- **Metadata extraction** – basic metadata is read from each safetensors file and stored in a full text search (FTS5) table.
- **Searchable gallery** – browse all indexed LoRAs in a grid view and filter by query.
- **Detail view** – see all previews, metadata and a download link for a single LoRA.
- **File removal** – delete LoRA files or individual preview images from the interface.
- **Category management** – organise LoRAs into categories and filter the gallery accordingly.

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

Run the setup script directly from GitHub:

```bash
curl -sL https://raw.githubusercontent.com/AsaTyr2018/MyLora/main/setup.sh | sudo bash -s install
```

If you cloned the repository manually run:

```bash
sudo ./setup.sh install      # install
sudo ./setup.sh update       # update
sudo ./setup.sh uninstall    # remove
```

After installation the interface is available on [http://localhost:5000](http://localhost:5000).

## Usage

- **Upload models**: open `/upload` and select one or more `.safetensors` files.  Each file is stored in `loradb/uploads` and indexed automatically.
- **Upload previews**: open `/upload_previews` to upload a ZIP containing images.  Files named `mylora.png`, `mylora_1.png`, ... will be placed next to `mylora.safetensors` and shown in the gallery.
- **Browse and search**: the `/grid` page lists all indexed LoRAs. Use the search box to filter by filename or tags.
- **Detail view**: click a LoRA in the gallery to view all previews and metadata.  A download button is provided to retrieve the original file.
- **Delete files**: tick the checkboxes in the gallery or detail view and press *Remove Selected* to delete the chosen files.
- **Categories**: add categories via the API or detail page and use the dropdown on the gallery page to filter.

### Bulk import

Use `bulk_import.py` to ingest an existing collection of LoRA files and preview
images. The script expects two directories: one containing all `.safetensors`
files and another holding subfolders with the corresponding preview images. An
optional third directory may contain category text files (one file per
category, lines listing model filenames). Run

```bash
python bulk_import.py /path/to/safetensors /path/to/images /path/to/categories
```

Every model will be copied into `loradb/uploads`, its metadata extracted and
added to the search index. When a categories directory is supplied, the models
are automatically assigned to the listed categories.

### Category migration

Existing installations can populate the new category tables based on text files
located next to each LoRA file. Run

```bash
python migrate_categories.py
```

Each `<name>.txt` file should contain a comma or newline separated list of
categories which will be created and assigned to `<name>.safetensors`.

The web pages use Bootstrap via a CDN and are rendered with Jinja2 templates.  The application keeps all data locally on disk in the `loradb` directory.

---

MIT License
