from typing import Dict, List

class IndexingAgent:
    """Maintain search index for LoRA metadata."""

    def __init__(self):
        self.entries: List[Dict[str, str]] = []

    def add_metadata(self, data: Dict[str, str]) -> None:
        self.entries.append(data)

    def search(self, query: str) -> List[Dict[str, str]]:
        return [e for e in self.entries if query.lower() in e.get("filename", "").lower()]
