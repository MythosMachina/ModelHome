import os
import platform
import subprocess
from pathlib import Path
import shutil

DEFAULT_REPO = "https://github.com/AsaTyr2018/MyLora.git"
APP_DIR = Path("app")

def run(cmd: list[str]):
    subprocess.check_call(cmd)

def detect_os() -> str:
    system = platform.system().lower()
    if 'windows' in system:
        return 'windows'
    return 'linux'

def clone_repo(repo: str) -> Path:
    if APP_DIR.exists():
        print(f"Using existing repo in {APP_DIR}")
        return APP_DIR
    run(["git", "clone", repo, str(APP_DIR)])
    return APP_DIR

def create_dockerfile(path: Path):
    df = path / "Dockerfile"
    if df.exists():
        return
    df.write_text(
        """
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD [\"python\", \"main.py\"]
"""
    )


def create_compose(path: Path):
    compose = path / "docker-compose.yml"
    if compose.exists():
        return
    compose.write_text(
        """
version: '3'
services:
  mylora:
    build: .
    ports:
      - '5000:5000'
    volumes:
      - ./loradb/uploads:/app/loradb/uploads
      - ./loradb/search_index:/app/loradb/search_index
"""
    )

def main(repo: str = DEFAULT_REPO):
    os_type = detect_os()
    print(f"Detected OS: {os_type}")
    path = clone_repo(repo)
    create_dockerfile(path)
    create_compose(path)
    print("Docker setup files created. Run 'docker compose up' to start.")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Build Docker setup for MyLora")
    parser.add_argument("repo", nargs="?", default=DEFAULT_REPO, help="Repository to clone")
    args = parser.parse_args()
    main(args.repo)
