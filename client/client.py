"""Lazy LoRA downloader client.

This small helper mirrors remote `.safetensors` files as 0-byte placeholders.
When an application opens a placeholder, the file is fetched from the MyLora
server and stored locally until it has not been accessed for a while.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Dict, Optional

import httpx
from inotify_simple import INotify, flags

try:
    import tomllib
except ModuleNotFoundError:  # Python <3.11 fallback
    import tomli as tomllib

CONFIG_PATH = Path(__file__).with_name("config.toml")


class LazyDownloader:
    """Monitor placeholder files and download them on demand."""

    def __init__(
        self,
        server_url: str,
        data_dir: Path,
        expire_seconds: int = 60,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.data_dir = data_dir
        self.expire_seconds = expire_seconds
        self.username = username or ""
        self.password = password or ""
        self.access_times: Dict[Path, float] = {}
        self.inotify = INotify()
        # `inotify_simple` does not provide a combined CLOSE flag, so listen to
        # both close events explicitly
        close_flags = flags.CLOSE_WRITE | flags.CLOSE_NOWRITE
        self.inotify.add_watch(str(self.data_dir), flags.OPEN | close_flags)
        self.client = httpx.Client(follow_redirects=False)

    def ensure_placeholders(self) -> None:
        resp = self.client.get(f"{self.server_url}/search", params={"query": "*"})
        resp.raise_for_status()
        for entry in resp.json():
            path = self.data_dir / entry["filename"]
            path.touch(exist_ok=True)

    def download(self, name: str) -> None:
        url = f"{self.server_url}/uploads/{name}"
        resp = self.client.get(url)
        resp.raise_for_status()
        (self.data_dir / name).write_bytes(resp.content)

    def cleanup(self) -> None:
        now = time.time()
        for path, ts in list(self.access_times.items()):
            if (
                now - ts > self.expire_seconds
                and path.exists()
                and path.stat().st_size > 0
            ):
                path.unlink(missing_ok=True)
                path.touch()
                del self.access_times[path]

    def run(self) -> None:
        if self.username and self.password:
            resp = self.client.post(
                f"{self.server_url}/login",
                data={"username": self.username, "password": self.password},
            )
            # Successful login issues a 303 redirect to "/". Treat this as
            # success instead of raising an exception when ``follow_redirects``
            # is disabled.
            if resp.status_code != 303:
                resp.raise_for_status()
        self.ensure_placeholders()
        while True:
            for event in self.inotify.read(timeout=1000):
                path = self.data_dir / event.name
                if event.mask & flags.OPEN:
                    if path.stat().st_size == 0:
                        self.download(event.name)
                    self.access_times[path] = time.time()
                elif event.mask & (flags.CLOSE_WRITE | flags.CLOSE_NOWRITE):
                    self.access_times[path] = time.time()
            self.cleanup()


def load_config() -> tuple[str, Path, str, str]:
    with CONFIG_PATH.open("rb") as fh:
        cfg = tomllib.load(fh)
    server_url = cfg.get("server_url", "http://127.0.0.1:9090")
    data_dir = Path(cfg.get("data_dir", "./lora_mount"))
    username = cfg.get("username", "")
    password = cfg.get("password", "")
    data_dir.mkdir(parents=True, exist_ok=True)
    return server_url, data_dir, username, password


def main() -> None:
    server, data_dir, username, password = load_config()
    downloader = LazyDownloader(server, data_dir, username=username, password=password)
    thread = threading.Thread(target=downloader.run, daemon=True)
    thread.start()
    print(f"Listening for accesses in {data_dir} (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == "__main__":
    main()
