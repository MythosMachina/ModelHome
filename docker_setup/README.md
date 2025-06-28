# Docker Setup Builder

This folder contains a helper script to generate a Docker setup for **MyLora**.
It works on both Windows and Linux by automatically detecting the operating
system.

Running the script will:

1. Clone the MyLora repository into `./app` if it is not already present.
2. Create a `Dockerfile` and `docker-compose.yml` inside the cloned directory.
3. Configure Docker volumes so the SQLite index database and uploaded files are
   stored outside of the container for easy backup.

## Usage

```bash
python builder.py [REPO_URL]
```

The default repository URL points to the main MyLora GitHub repository. After the
files have been created you can start the service with:

```bash
cd app
docker compose up -d
```

The web interface will be available at `http://localhost:5000`.

## Updating

Use `update.py` to pull the latest code and recreate the container while keeping
your data volume:

```bash
python update.py
```

The script stops the running container, renames it with a `_backup` suffix and
starts a freshly built container using the same volumes so no uploads or
database files are lost.
