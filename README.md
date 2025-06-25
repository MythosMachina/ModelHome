# MyLora - One site to Rule them all!

MyLora provides a modern web interface to manage LoRA model files (`.safetensors`) alongside their preview images. The application is built with FastAPI and ships with a sleek dark mode interface.

## Highlights

- **Upload wizard** – drag & drop a LoRA file and its previews in one go.
- **Automatic metadata extraction** – tags, dimension and other information are parsed from the model files.
- **Searchable gallery** – browse all models, filter by tag or category and download directly.
- **Category management** – create and assign categories with just a few clicks.
- **Local migration** – scripts are included to import existing collections or migrate old category files.
- **Responsive design** – works great on desktop and mobile.

## Quick setup

Run the setup script directly from GitHub:

```bash
curl -sL https://raw.githubusercontent.com/AsaTyr2018/MyLora/main/setup.sh | sudo bash -s install
```

To update or remove an existing installation use:

```bash
sudo ./setup.sh update       # update
sudo ./setup.sh uninstall    # remove
```

The service will be available on [http://localhost:5000](http://localhost:5000).

## Pages overview

### Main site `/`
The landing page shows basic statistics and quick links to the gallery and the upload wizard.

![Main site screenshot](docs/screenshot_main.png)

### Gallery `/grid`
Grid view of all LoRAs with infinite scrolling, search box and category filter. Items link to their detail page.

![Gallery screenshot](docs/screenshot_gallery.png)

### Detail view `/detail/<filename>`
Shows all preview images, extracted metadata and category management options for a single LoRA.

![Detail screenshot](docs/screenshot_detail.png)

### Upload wizard `/upload_wizard`
Guided upload page that first asks for the `.safetensors` file and then its previews. Progress bars indicate upload status and the page redirects to the detail view when done.

![Upload wizard screenshot](docs/screenshot_upload_wizard.png)

## Bulk import
Use `bulk_import.py` to ingest an existing collection:

```bash
python bulk_import.py SAFETENSORS_DIR IMAGES_DIR [CATEGORIES_DIR]
```

## Category migration
Convert old `<name>.txt` files in `loradb/uploads` to the new database format with:

```bash
python migrate_categories.py
```

---

MIT License
