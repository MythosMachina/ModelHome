from pathlib import Path
from loradb.agents import IndexingAgent


def main() -> None:
    uploads = Path('loradb/uploads')
    indexer = IndexingAgent()
    for txt in uploads.glob('*.txt'):
        stem = txt.stem
        lora_file = uploads / f'{stem}.safetensors'
        if not lora_file.exists():
            continue
        with txt.open('r', encoding='utf-8') as f:
            content = f.read()
        categories = [c.strip() for c in content.replace(',', '\n').splitlines() if c.strip()]
        for cat in categories:
            cid = indexer.create_category(cat)
            indexer.assign_category(lora_file.name, cid)
    print('Migration complete')


if __name__ == '__main__':
    main()
