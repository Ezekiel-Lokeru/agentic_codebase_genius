# py/parser_ccg.py
"""
Code Context Graph (CCG) builder for analyzing Python codebases.
Uses tree-sitter for AST parsing (if available), falls back to regex-based parsing.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, List

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None

try:
    from tree_sitter import Language, Parser
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

# Try to initialize tree-sitter if available
PARSER = None
if HAS_TREE_SITTER:
    try:
        # Modern tree-sitter API: Language.build_library() or use pre-built languages
        # For now, we'll skip tree-sitter and use regex fallback to avoid complex binary compilation
        HAS_TREE_SITTER = False
    except Exception as e:
        print(f"[Parser] Tree-sitter initialization failed: {e}")
        HAS_TREE_SITTER = False


def parse_python_file_regex(path: str) -> dict:
    """
    Enhanced regex-based Python parser.
    Extracts functions, classes, calls, inheritance, and imports.
    """
    try:
        code = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[Parser] Could not read {path}: {e}")
        return {"functions": [], "classes": [], "calls": [], "imports": [], "inheritance": []}

    result = {"functions": [], "classes": [], "calls": [], "imports": [], "inheritance": []}

    # ─── Extract function definitions ───
    func_matches = {}
    for match in re.finditer(r"^\s*def\s+(\w+)\s*\(", code, re.MULTILINE):
        func_name = match.group(1)
        func_matches[func_name] = match
        result["functions"].append({"name": func_name, "line": code[:match.start()].count("\n") + 1})

    # ─── Extract class definitions with inheritance ───
    for match in re.finditer(r"^\s*class\s+(\w+)\s*(?:\(([^)]*)\))?", code, re.MULTILINE):
        class_name = match.group(1)
        parent_str = match.group(2)
        
        # Extract parent class (handle multiple inheritance, but take first)
        parent = None
        if parent_str:
            # Extract first parent class name
            parent_match = re.search(r"(\w+)", parent_str)
            if parent_match:
                parent = parent_match.group(1)
        
        result["classes"].append({
            "name": class_name,
            "parent": parent,
            "line": code[:match.start()].count("\n") + 1
        })
        
        # Track inheritance relationship
        if parent and parent not in ['object', 'ABC']:
            result["inheritance"].append({
                "child": class_name,
                "parent": parent
            })

    # ─── Extract function calls within functions ───
    for func_name, func_match in func_matches.items():
        func_start = func_match.end()
        # Find next function or class definition
        next_def = re.search(r"\n\s*(def|class)\s+\w+", code[func_start:])
        if next_def:
            func_end = func_start + next_def.start()
        else:
            func_end = len(code)
        func_body = code[func_start:func_end]
        
        # Find all function calls: name()
        for call_match in re.finditer(r"(\w+)\s*\(", func_body):
            called_func = call_match.group(1)
            # Filter out Python keywords and builtins
            if called_func not in ['if', 'for', 'while', 'with', 'try', 'except', 
                                   'print', 'len', 'range', 'str', 'int', 'dict', 
                                   'list', 'set', 'tuple', 'open', 'isinstance', 'hasattr']:
                result["calls"].append({
                    "caller": func_name,
                    "callee": called_func,
                    "line": code[:func_start + call_match.start()].count("\n") + 1
                })

    # ─── Extract import statements ───
    # Match: import X, from X import Y
    for match in re.finditer(r"^(?:from\s+(\w+)|import\s+(\w+))", code, re.MULTILINE):
        module = match.group(1) or match.group(2)
        result["imports"].append({
            "module": module,
            "line": code[:match.start()].count("\n") + 1
        })

    return result


def parse_python_file(path: str) -> dict:
    """Parse Python file and extract functions/classes."""
    return parse_python_file_regex(path)


def build_ccg_for_files(file_paths: List[str]) -> Optional[dict]:
    """
    Build a Code Context Graph from Python files.
    Returns a dictionary with functions, classes, calls, imports, and inheritance data.
    """
    result = {
        "functions": [],
        "classes": [],
        "calls": [],
        "imports": [],
        "inheritance": []
    }
    
    for p in file_paths:
        try:
            parsed = parse_python_file(p)
            if not parsed:
                continue
            
            # Aggregate all data
            result["functions"].extend(parsed.get("functions", []))
            result["classes"].extend(parsed.get("classes", []))
            result["calls"].extend(parsed.get("calls", []))
            result["imports"].extend(parsed.get("imports", []))
            result["inheritance"].extend(parsed.get("inheritance", []))
        except Exception as e:
            # Silently skip files with parsing errors
            continue

    return result if (result["functions"] or result["classes"]) else None


def ccg_to_mermaid(ccg_dict: Optional[dict], max_nodes: int = 30) -> Optional[str]:
    """
    Convert a CCG dictionary to Mermaid flowchart syntax.
    """
    if ccg_dict is None or not isinstance(ccg_dict, dict):
        return None

    try:
        lines = ["graph TD"]
        count = 0

        # Add classes as nodes
        for cls in ccg_dict.get("classes", [])[:max_nodes]:
            cls_name = cls.get("name", "Unknown")
            lines.append(f'  {cls_name}["📦 {cls_name}"]')
            count += 1
            if count >= max_nodes:
                break

        # Add inheritance relationships
        for rel in ccg_dict.get("inheritance", []):
            child = rel.get("child", "")
            parent = rel.get("parent", "")
            if child and parent:
                lines.append(f'  {child} -->|extends| {parent}')

        # Add some function calls
        calls_by_caller = {}
        for call in ccg_dict.get("calls", []):
            caller = call.get("caller", "")
            callee = call.get("callee", "")
            if caller and callee:
                if caller not in calls_by_caller:
                    calls_by_caller[caller] = []
                calls_by_caller[caller].append(callee)

        # Add top callers
        for caller, callees in list(calls_by_caller.items())[:5]:
            unique_callees = list(set(callees))[:3]
            for callee in unique_callees:
                lines.append(f'  {caller} -->|calls| {callee}')

        return "\n".join(lines)
    except Exception as e:
        return None
