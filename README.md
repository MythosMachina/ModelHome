[![MIT License](https://img.shields.io/github/license/AsaTyr2018/MyLora)](LICENSE)
[![Stars](https://img.shields.io/github/stars/AsaTyr2018/MyLora?style=social)](https://github.com/AsaTyr2018/MyLora/stargazers)
[![LoRAs Managed](https://img.shields.io/badge/LoRAs-Unlimited-purple?logo=fastapi)](https://github.com/AsaTyr2018/MyLora)
[![Featured on TurtlesAI](https://img.shields.io/badge/featured%20on-TurtlesAI-blueviolet?logo=readthedocs&logoColor=white)](https://www.turtlesai.com/en/pages-2946/mylora-intelligent-and-comprehensive-management-of)

# MyLora - One site to Rule them all!

MyLora provides a modern web interface to manage LoRA model files (`.safetensors`) alongside their preview images. The application is built with FastAPI and ships with a sleek dark mode interface.

# Proudly featured at TurtlesAI!
Link -> https://www.turtlesai.com/en/pages-2946/mylora-intelligent-and-comprehensive-management-of

## Highlights

- **Upload wizard** – drag & drop a LoRA file and its previews in one go.
- **Automatic metadata extraction** – tags, dimension and other information are parsed from the model files.
- **Searchable gallery** – browse all models, filter by tag or category and download directly.
- **User accounts** – login/logout with role-based permissions and secure session cookies.
- **Guest mode** – visitors are redirected to a public "Model Showcase" with preview-only details.
- **Category management** – create and assign categories with just a few clicks.
- **Bulk category assignment** – select multiple LoRAs in the gallery and add them to a category.
- **Local migration** – scripts are included to import existing collections or migrate old category files.
- **Admin tools** – manage users from the web UI and create the initial admin via `usersetup.py`.
- **Themed error pages** – friendly 404 page and access denied view.
- **Responsive design** – works great on desktop and mobile.

## Coming soon: Plugin support (Delayed)

MyLora is evolving into a modular platform!  
A full plugin system is being developed to allow custom extensions.

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

The service will be available on [http://{serverip}:5000](http://{serverip}:5000).

## Admin User Setup (!Important!)

To set up the first admin user, run the following command in the root folder of the script:

```bash
python3 ./usersetup.py {user} {password}
```

## Pages overview

### Index `/`
Overview of all models and images with quick navigation.

### Models `/models`
List of all uploaded models with search and filter options.

### Model Detail `/models/<filename>`
Detailed information about a selected model including download link and preview images.

### Images `/images`
Overview of all uploaded images with sorting and filtering.

### Image Detail `/images/<image>`
Shows the selected image in high resolution and information about the related model.

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
