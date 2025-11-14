# Py/orchestrator.py - Codebase Genius Orchestrator
# Coordinates multi-agent pipeline: RepoMapper -> CodeAnalyzer -> DocGenie

import os
import json
from typing import Optional
from Py import repo_clone, parser_ccg, diagram_export

class Orchestrator:
    """
    Main orchestrator for the Codebase Genius pipeline.
    Coordinates repository mapping, code analysis, and documentation generation.
    """

    def __init__(self, output_root: str = "./outputs"):
        self.output_root = output_root
        os.makedirs(output_root, exist_ok=True)

    def run(self, repo_url: str, verbose: bool = True) -> dict:
        """
        Execute the full pipeline: clone, analyze, generate docs.
        
        Returns:
            dict: Result with keys 'success', 'repo_name', 'root', 'docs_path', 'error' (if any)
        """
        try:
            if verbose:
                print(f"\n[Orchestrator] Starting pipeline for {repo_url}")

            # Step 1: Repository Mapping (Repo Mapper)
            if verbose:
                print("[RepoMapper] Cloning and mapping repository...")
            repo_info = repo_clone.clone_repo(repo_url, None)
            repo_name = repo_info["name"]
            repo_root = repo_info["root"]

            file_tree = repo_clone.generate_file_tree(repo_root)
            readme_summary = repo_clone.summarize_readme(repo_root)

            repo_info["file_tree"] = file_tree
            repo_info["readme_summary"] = readme_summary

            if verbose:
                print(f"  ✓ Cloned to {repo_root}")
                print(f"  ✓ File tree built: {len(file_tree.get('children', []))} top-level items")
                print(f"  ✓ README summary extracted")

            # Step 2: Code Analysis (Code Analyzer)
            if verbose:
                print("[CodeAnalyzer] Building Code Context Graph...")
            # Collect ALL Python files for deep analysis (removed 10-file limit)
            py_files = self._collect_python_files(file_tree, repo_root, limit=None)
            
            ccg = None
            ccg_mermaid = None
            if py_files:
                try:
                    ccg = parser_ccg.build_ccg_for_files(py_files)
                    ccg_mermaid = parser_ccg.ccg_to_mermaid(ccg)
                    if verbose:
                        print(f"  ✓ CCG built from {len(py_files)} Python files")
                except Exception as e:
                    import traceback
                    if verbose:
                        print(f"  ⚠ CCG build error: {e}")
                        traceback.print_exc()
                    ccg = None
                    ccg_mermaid = None
            else:
                if verbose:
                    print("  ⚠ No Python files found in repository")

            # Step 3: Documentation Generation (DocGenie)
            if verbose:
                print("[DocGenie] Generating documentation...")
            docs_path = self._generate_docs(repo_name, repo_info, ccg, ccg_mermaid)
            if verbose:
                print(f"  ✓ Documentation saved to {docs_path}")

            return {
                "success": True,
                "repo_name": repo_name,
                "root": repo_root,
                "docs_path": docs_path,
                "repo_info": repo_info,
            }

        except Exception as e:
            if verbose:
                print(f"  ✗ Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url,
            }

    def _collect_python_files(self, tree: dict, repo_root: str, limit: Optional[int] = 10) -> list:
        """
        Recursively collect Python file paths from the tree, limited to first `limit` files.
        If limit is None, collects ALL Python files.
        """
        py_files = []

        def walk(node, depth=0):
            if limit is not None and len(py_files) >= limit:
                return
            if isinstance(node, dict):
                # Handle file nodes
                if node.get("type") == "file":
                    if node.get("name", "").endswith(".py"):
                        path = node.get("path", os.path.join(repo_root, node.get("name", "")))
                        py_files.append(path)
                # Handle directory nodes or root
                elif node.get("type") == "dir" or "children" in node:
                    children = node.get("children", [])
                    for child in children:
                        walk(child, depth + 1)

        walk(tree)
        return py_files

    def _generate_docs(self, repo_name: str, repo_info: dict, ccg: Optional[dict], ccg_mermaid: Optional[str]) -> str:
        """
        Generate comprehensive markdown documentation with CCG analysis.
        Includes Overview, Installation, Architecture, API Reference, and Code Context Graph.
        """
        output_dir = os.path.join(self.output_root, repo_name)
        os.makedirs(output_dir, exist_ok=True)
        docs_path = os.path.join(output_dir, "docs.md")

        md_lines = []

        # ─── Header ───
        md_lines.append(f"# {repo_name} - Auto-Generated Documentation\n")

        # ─── Overview Section ───
        md_lines.append("## Overview\n")
        readme_summary = repo_info.get("readme_summary", "No README available.")
        md_lines.append(f"{readme_summary}\n")

        # ─── Installation Section (NEW) ───
        md_lines.append("## Installation\n")
        repo_root = repo_info.get("root", ".")
        req_path = os.path.join(repo_root, "requirements.txt")
        if os.path.exists(req_path):
            try:
                with open(req_path, 'r') as f:
                    reqs = f.read().strip().split('\n')[:5]  # First 5 requirements
                md_lines.append("```bash\npip install -r requirements.txt\n```\n")
                md_lines.append("**Key dependencies:**\n")
                for req in reqs:
                    if req.strip() and not req.startswith('#'):
                        md_lines.append(f"- {req}\n")
            except:
                md_lines.append(f"```bash\npip install {repo_name.lower()}\n```\n")
        else:
            md_lines.append(f"```bash\npip install {repo_name.lower()}\n```\n")

        # ─── File Structure Section ───
        md_lines.append("## Repository Structure\n")
        file_tree = repo_info.get("file_tree", {})
        tree_str = self._format_file_tree(file_tree)
        md_lines.append(f"```\n{tree_str}\n```\n")

        # ─── Architecture Section (NEW - Uses CCG) ───
        if ccg:
            md_lines.append("## Architecture\n\n")
            
            # Extract classes (key components)
            classes = ccg.get("classes", [])
            if classes:
                md_lines.append("### Key Components\n")
                for cls in classes[:10]:  # Top 10 classes
                    parent_str = f" (extends {cls['parent']})" if cls.get('parent') else ""
                    md_lines.append(f"- **{cls['name']}{parent_str}**: Core component\n")
                md_lines.append("")

            # Extract relationships
            inheritance = ccg.get("inheritance", [])
            if inheritance:
                md_lines.append("### Class Hierarchy\n")
                for rel in inheritance[:10]:
                    md_lines.append(f"- `{rel['child']}` extends `{rel['parent']}`\n")
                md_lines.append("")

            # Extract imports (dependencies)
            imports = ccg.get("imports", [])
            if imports:
                unique_imports = list(set([imp["module"] for imp in imports[:10]]))
                if unique_imports and unique_imports[0] != repo_name.lower():
                    md_lines.append("### Module Dependencies\n")
                    for imp in unique_imports[:10]:
                        md_lines.append(f"- `{imp}`\n")
                    md_lines.append("")

        # ─── API Reference Section (NEW - Uses CCG) ───
        if ccg:
            functions = ccg.get("functions", [])
            if functions:
                md_lines.append("## API Reference\n\n")
                md_lines.append("### Key Functions\n")
                for func in functions[:15]:  # Top 15 functions
                    md_lines.append(f"- `{func['name']}`\n")
                md_lines.append("")

        # ─── Function Calls (NEW - Uses CCG) ───
        if ccg:
            calls = ccg.get("calls", [])
            if calls:
                # Group calls by caller
                calls_by_caller = {}
                for call in calls:
                    caller = call["caller"]
                    callee = call["callee"]
                    if caller not in calls_by_caller:
                        calls_by_caller[caller] = []
                    calls_by_caller[caller].append(callee)
                
                if calls_by_caller:
                    md_lines.append("## Call Graph (Main Interactions)\n\n")
                    for caller, callees in list(calls_by_caller.items())[:8]:  # Top 8 functions
                        unique_callees = list(set(callees))[:5]  # Top 5 unique calls
                        md_lines.append(f"- **{caller}** calls: {', '.join(unique_callees)}\n")
                    md_lines.append("")

        # ─── Code Context Graph (Mermaid) ───
        if ccg_mermaid:
            md_lines.append("## Code Context Graph (Module Diagram)\n")
            md_lines.append("```mermaid\n")
            md_lines.append(ccg_mermaid)
            md_lines.append("\n```\n")

        # ─── Metadata Section ───
        md_lines.append("## Metadata\n")
        md_lines.append(f"- **Repository Name**: {repo_name}\n")
        md_lines.append(f"- **Root Path**: {repo_info.get('root', 'N/A')}\n")
        md_lines.append(f"- **Generated at**: {repo_info.get('repo_dir', 'N/A')}\n")
        
        # Add CCG stats
        if ccg:
            md_lines.append(f"- **Functions Analyzed**: {len(ccg.get('functions', []))}\n")
            md_lines.append(f"- **Classes Analyzed**: {len(ccg.get('classes', []))}\n")
            md_lines.append(f"- **Function Calls Tracked**: {len(ccg.get('calls', []))}\n")

        # Write to file
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return docs_path

    def _format_file_tree(self, tree: dict, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        """
        Format a file tree dict as a string (simple tree view).
        """
        if current_depth >= max_depth:
            return ""

        lines = []
        name = tree.get("name", "root")
        if current_depth == 0:
            lines.append(name + "/")
        else:
            lines.append(prefix + name + ("/" if tree.get("type") == "dir" else ""))

        if tree.get("type") == "dir" and tree.get("children"):
            children = tree["children"]
            for i, child in enumerate(children[:20]):  # Limit displayed children
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                lines.append(self._format_file_tree(child, child_prefix, max_depth, current_depth + 1))

        return "\n".join(filter(None, lines))
