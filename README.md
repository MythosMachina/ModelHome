# LoRA Database Web Interface

This project provides a minimal FastAPI application for organising LoRA files (`.safetensors`) along with preview images.  It allows uploading new LoRA models, automatically extracts their metadata and stores it in a small SQLite based search index.  A simple gallery interface lets you browse the models, search by name or tag and download or remove files.

## Preview
Grid View
![grafik](https://github.com/user-attachments/assets/72b261f7-0fe8-4aff-ab42-82dc8db1584d)

Detail View
![grafik](https://github.com/user-attachments/assets/233b63ac-ca2b-4249-aaa2-f2b991aa25c9)

## Features

- **Upload LoRA files** – multiple `.safetensors` files can be uploaded at once.
- **Upload preview archives** – a ZIP file containing preview images is extracted and matched to the corresponding LoRA by filename.
- **Metadata extraction** – basic metadata is read from each safetensors file and stored in a full text search (FTS5) table.
- **Searchable gallery** – browse all indexed LoRAs in a grid view and filter by query.
- **Detail view** – see all previews, metadata and a download link for a single LoRA.
- **File removal** – delete LoRA files or individual preview images from the interface.
- **Category management** – organise LoRAs into categories and filter the gallery accordingly.
- **Remove categories** – unassign a model from a category directly from the detail page.
- **Find uncategorised models** – a dynamic *No Category* filter lists LoRAs without any category.

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

After starting the service open [http://localhost:5000](http://localhost:5000) in your browser.

### Upload models

The `/upload_wizard` page lets you upload a LoRA file and its previews in one go. The wizard shows the upload progress for both steps and automatically redirects to the detail page once finished.

### Browse and search

The `/grid` page shows all models. Use the search box or category dropdown to filter. Clicking an entry opens a detail page with metadata, previews and a download link.

### Delete files

Select items in the gallery or detail view and press **Remove Selected** to delete them.

### Categories

Create categories from a model's detail page or via the API and assign models to them. The dropdown on `/grid` filters by category.

### Bulk import

`bulk_import.py` can ingest an existing collection without using the web interface.
Run it as

```bash
python bulk_import.py SAFETENSORS_DIR IMAGES_DIR [CATEGORIES_DIR]
```

* **SAFETENSORS_DIR** – directory containing the `.safetensors` files
* **IMAGES_DIR** – directory with subfolders of preview images
* **CATEGORIES_DIR** – optional directory of text files, one per category, listing model filenames

The script copies each model into `loradb/uploads`, extracts its metadata and updates the search index. When a categories directory is provided the models are automatically assigned.

### Category migration

If your existing installation stores categories in `<name>.txt` files inside `loradb/uploads`, run

```bash
python migrate_categories.py
```

Each text file may list categories separated by commas or newlines. The script creates the missing categories and assigns them to `<name>.safetensors`.

---

MIT License
