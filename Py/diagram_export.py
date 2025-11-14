# py/diagram_export.py
from pathlib import Path
def save_mermaid(mermaid_text: str, outdir: str, fname="ccg.mmd"):
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)
    f = p / fname
    f.write_text(mermaid_text, encoding="utf-8")
    return str(f)
