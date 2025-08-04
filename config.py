"""Configuration for paths used by the application."""

from pathlib import Path

# Resolve all paths relative to this config file so running the app from any
# working directory still picks up the correct folders.
BASE_DIR = Path(__file__).resolve().parent

# Directory to store uploaded LoRA files and preview images
UPLOAD_DIR = BASE_DIR / "loradb" / "uploads"

# Directory with static assets such as CSS
STATIC_DIR = BASE_DIR / "loradb" / "static"

# Directory containing Jinja2 templates
TEMPLATE_DIR = BASE_DIR / "loradb" / "templates"

# Location of the SQLite database for users and search index
DB_PATH = Path.home() / ".modelhome" / "index.db"

# Secret key for session cookies
SECRET_KEY = "change_this_secret"
