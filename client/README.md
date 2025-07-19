# MyLora Lazy Client

This utility mirrors LoRA files from a running MyLora instance. It creates
0-byte placeholder files that are replaced with the real `.safetensors` on
first access.

## Configuration

Edit `config.toml`:

```toml
server_url = "http://127.0.0.1:5000"  # URL of your MyLora server
data_dir = "./lora_mount"              # Directory for placeholders and downloads
```

## Usage

```
python client.py
```

A watcher thread listens for file open events in `data_dir`. When a placeholder
is opened it downloads the real file from `server_url`. After 60 seconds of
inactivity the file is removed and a placeholder is recreated.
