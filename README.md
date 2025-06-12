# LoRA Database Interface

A web-based management platform for LoRA files (.safetensors) with preview support, metadata extraction, and advanced search features.

---

## ✨ Features

* ⬆️ **Bulk Upload** of `.safetensors` LoRA files and preview images
* 🌐 **Dark Mode Interface** in modern grid gallery design
* ⚙️ **Automatic Metadata Extraction** including training tags
* ⚡ **Search by Name and Tags**, powered by indexed metadata
* 🎭 **Grid View** of LoRAs with randomized preview thumbnails
* 🔍 **Individual LoRA View** with:

  * Gallery of all previews
  * Metadata summary
  * Direct download link
* 📋 **Structured API-ready backend** (Flask/FastAPI compatible)

---

## 📃 Project Structure

```
/loradb
|-- /uploads                # Uploaded safetensors and preview images
|-- /static                 # Static frontend assets
|-- /templates              # Jinja2 or frontend framework views
|-- /api                    # REST API endpoints
|-- /agents                 # Logic for upload, metadata, indexing
|-- /search_index           # Tag/Name search database
|-- main.py                 # Webserver entrypoint
|-- config.py               # Config and environment variables
|-- requirements.txt        # Python dependencies
```

---

## ⚡ Quick Start

```bash
# 1. Clone Repository
$ git clone https://github.com/AsaTyr2018/MyLora.git
$ cd MyLora

# 2. Install Dependencies
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# 3. Run Web Interface
$ python main.py
```

Default port: `http://ServerIP:5000`

---

## 🔐 Example: LoRA Grid View

Displays all uploaded LoRA models in a grid. Each cell includes:

* Random preview image
* LoRA name
* Click opens detailed page

![Example Grid](docs/grid-example.png)

---

## 🧰 Built With

* **Python** (Flask or FastAPI)
* **SQLite / ElasticSearch** for indexing
* **TailwindCSS / Vue / React** frontend (Dark Mode)
* **Pillow / Safetensors** for metadata extraction

---

## ✈ Roadmap

* [ ] Planning
* [ ] Upload + Metadata Extraction
* [ ] Grid Gallery with Dark Mode
* [ ] Tag- & Name-Based Search
* [ ] REST API Access
* [ ] User Management & Favorites
* [ ] Drag-and-Drop Upload with Progress Bar

---

## 📄 License

MIT License

---

