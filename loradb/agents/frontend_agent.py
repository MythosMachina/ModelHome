from pathlib import Path
from typing import List, Dict


class FrontendAgent:
    """Render simple HTML views for the LoRA gallery."""

    def __init__(self, uploads_dir: Path) -> None:
        self.uploads_dir = uploads_dir

    def render_grid(self, entries: List[Dict[str, str]]) -> str:
        cells = []
        for e in entries:
            name = e.get("name") or e.get("filename")
            cells.append(
                f"<div class='cell'><p>{name}</p></div>"
            )
        grid_html = """
        <html><head><style>
        body{background:#111;color:#eee;font-family:sans-serif}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
        .cell{background:#222;padding:10px;border-radius:5px;text-align:center}
        </style></head><body>
        <h1>LoRA Gallery</h1>
        <div class='grid'>
        """
        grid_html += "\n".join(cells)
        grid_html += "</div></body></html>"
        return grid_html
