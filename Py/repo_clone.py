# py/repo_clone.py
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

def clone_repo(git_url: str, dest_root: str = None) -> dict:
    """
    Clone a public git repo into a temporary directory and return metadata.
    Returns:
      {
        "repo_dir": "/tmp/abc",
        "name": "repo-name",
        "root": "/tmp/abc/repo-name",
        "readme": "text..." or None
      }
    """
    if dest_root is None:
        dest_root = tempfile.mkdtemp(prefix="codegen_")
    repo_name = git_url.rstrip("/").split("/")[-1].replace(".git","")
    target = os.path.join(dest_root, repo_name)
    try:
        subprocess.check_call(["git", "clone", "--depth", "1", git_url, target])
    except Exception as e:
        shutil.rmtree(dest_root, ignore_errors=True)
        raise

    # find README
    readme_text = None
    for fname in ("README.md","README.rst","README.txt","readme.md"):
        p = os.path.join(target, fname)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                readme_text = fh.read()
            break

    return {"repo_dir": dest_root, "name": repo_name, "root": target, "readme": readme_text}


def generate_file_tree(root_path: str, ignore_dirs=None) -> dict:
    """
    Return structured dict representing file tree.
    """
    if ignore_dirs is None:
        ignore_dirs = {".git","node_modules","venv","__pycache__"}
    root = Path(root_path)
    def walk(p):
        items=[]
        for child in sorted(p.iterdir(), key=lambda x: x.name):
            if child.is_dir():
                if child.name in ignore_dirs:
                    continue
                items.append({"type":"dir","name":child.name,"children":walk(child)})
            else:
                items.append({"type":"file","name":child.name,"path":str(child)})
        return items
    return {"name": root.name, "path": str(root), "children": walk(root)}

def summarize_readme(repo_path):
    import os
    readme_path = os.path.join(repo_path, "README.md")
    if not os.path.exists(readme_path):
        return "No README.md file found."
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    # crude summary: first few lines
    summary = "\n".join(content.splitlines()[:5])
    return summary
