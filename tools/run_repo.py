import sys
import os
# Ensure project root is on sys.path so local `Py` and `py` packages are importable
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
from Py import repo_clone
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/run_repo.py <git_url>")
        sys.exit(2)
    url = sys.argv[1]
    print(f"Cloning {url}...")
    info = repo_clone.clone_repo(url)
    print("Clone complete. Repo info:")
    # limit printing size
    out = {"name": info.get("name"), "root": info.get("root"), "readme": (info.get("readme") or '')[:800]}
    print(json.dumps(out, indent=2))
    print("Generating file tree (top-level children)...")
    tree = repo_clone.generate_file_tree(info["root"])
    # print top-level file/dir names
    children = tree.get("children", [])
    print(f"Top-level items ({len(children)}):")
    for c in children[:50]:
        print(f" - {c['type']}: {c['name']}")
    print("README summary:\n")
    summary = repo_clone.summarize_readme(info["root"])
    print(summary)

if __name__ == '__main__':
    main()
