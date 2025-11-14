# jac/agents.jac
"""Codebase Genius - Jac Agents"""

# NOTE: py_module style may differ by Jac runtime. This is illustrative.
# If your Jac environment uses different bridging, adapt calls to subprocess/python wrappers.

# Globals for coordination
glob pipeline_state: dict = {};
glob outputs_root: str = "./outputs";

# Supervisor walker
walker CodeGenius {
    can start_with_url(url: str) {
        print("Supervisor: Starting pipeline for", url);
        # Validate URL quick check
        if not url.startswith("http") {
            print("Supervisor: Invalid URL");
            return "INVALID_URL";
        }
        # Ask RepoMapper to clone and map
        repo_info = repo_mapper.clone_and_map(url);
        if repo_info == None {
            print("Supervisor: Clone failed");
            return "CLONE_FAILED";
        }
        pipeline_state["repo"] = repo_info;
        # Make a plan
        plan = self.plan(repo_info);
        pipeline_state["plan"] = plan;
        # Analyze iteratively
        for item in plan["priority_files"] {
            analyzer_result = code_analyzer.analyze_file(item);
            # store partial results
            if not pipeline_state.get("analysis"): pipeline_state["analysis"] = [];
            pipeline_state["analysis"].append(analyzer_result);
        }
        # After iterative analysis, generate docs
        doc_path = doc_genie.generate_docs(repo_info, pipeline_state["analysis"]);
        print("Supervisor: Documentation generated:", doc_path);
        return doc_path;
    }

    can plan(repo_info: dict) -> dict {
        # naive plan: pick top-level py files and main files first
        root = repo_info["root"];
        children = repo_info["file_tree"]["children"];
        priority=[];
        # search for files named main.py, app.py, __main__.py, or top-level .py files
        def collect(files):
            for f in files {
                if f["type"] == "file" and f["name"].endswith(".py") {
                    if f["name"] in ["main.py","app.py","__main__.py"] {
                        priority.append(f["path"]);
                    }
                } elif f["type"] == "dir" {
                    collect(f["children"]);
                }
            }
        }
        collect(children);
        # if none found, pick first 5 py files
        if len(priority) == 0 {
            # flatten
            py_list = [];
            def flat(files){
                for f in files {
                    if f["type"] == "file" and f["name"].endswith(".py") {
                        py_list.append(f["path"]);
                    } elif f["type"] == "dir" {
                        flat(f["children"]);
                    }
                }
            }
            flat(children);
            priority = py_list[:5];
        }
        return {"priority_files": priority, "repo": repo_info["name"]};
    }
}

# Repo Mapper agent interface (calls python)
walker repo_mapper {
    can clone_and_map(url: str) -> dict {
        # call python clone helper
        py = py_module("py.repo_clone");
        info = py.clone_repo(url, null);
        # produce file tree
        tree = py.generate_file_tree(info["root"]);
        info["file_tree"] = tree;
        # summarise README via a simple heuristic: first 4 paragraphs, or ask an LLM later
        info["readme_summary"] = self.summarise_readme(info.get("readme", ""));
        return info;
    }

    can summarise_readme(readme: str) -> str {
        if readme == "" or readme == null {
            return "No README found.";
        }
        # simple truncation summary placeholder; can be replaced with byLLM summarizer
        lines = readme.split("\n\n");
        return lines[:3].join("\n\n");
    }
}

# Code Analyzer agent (drives parser_ccg)
walker code_analyzer {
    can analyze_file(path: str) -> dict {
        py = py_module("py.parser_ccg");
        try {
            # collect ccg for this file only
            ccg = py.parse_python_file(path);
            # optional: build graph for current module
            return {"file": path, "parsed": ccg};
        } catch err {
            print("Analyzer: parse error", err);
            return {"file": path, "error": str(err)};
        }
    }
    can build_ccg(file_paths: list[str]) -> dict {
        py = py_module("py.parser_ccg");
        G = py.build_ccg_for_files(file_paths);
        mermaid = py.ccg_to_mermaid(G);
        return {"graph": G, "mermaid": mermaid};
    }
    # query API example: which functions call X -> delegated to python graph queries
}

# DocGenie: produce final markdown doc
walker doc_genie {
    can generate_docs(repo_info: dict, analyses: list[dict]) -> str {
        outdir = f"{outputs_root}/{repo_info['name']}";
        # build markdown content
        md = [];
        md.append(f"# {repo_info['name']} - Auto generated docs\n");
        # overview from readme summary
        md.append("## Overview\n");
        md.append(repo_info.get("readme_summary","No README available."));
        md.append("\n\n## File map\n");
        md.append(self.format_file_tree(repo_info["file_tree"]));
        md.append("\n\n## Analysis\n");
        for a in analyses {
            if a.get("error") {
                md.append(f"### {a['file']} - parse error\n```\n{a['error']}\n```\n");
            } else {
                md.append(f"### {a['file']}\n");
                parsed = a["parsed"];
                if parsed.get("functions") {
                    md.append("**Functions:**\n");
                    for f in parsed["functions"] {
                        md.append(f"- `{f['name']}` (line {f['start'][0]+1})\n");
                    }
                }
                if parsed.get("classes") {
                    md.append("**Classes:**\n");
                    for c in parsed["classes"] {
                        md.append(f"- `{c['name']}` (line {c['start'][0]+1})\n");
                    }
                }
            }
        }
        # build combined CCG mermaid diagram for top files
        paths = [a["file"] for a in analyses if not a.get("error")];
        py = py_module("py.parser_ccg");
        comb = py.build_ccg_for_files(paths);
        mermaid = py.ccg_to_mermaid(comb);
        md.append("\n\n## Code Context Graph\n");
        md.append("```mermaid\n");
        md.append(mermaid);
        md.append("\n```\n");

        # write to disk
        import os;
        os.makedirs(outdir, exist_ok=True);
        outpath = os.path.join(outdir, "docs.md");
        with open(outpath, "w", encoding="utf-8") as fh {
            fh.write("\n".join(md));
        }
        # also save mermaid separately
        py_module("py.diagram_export").save_mermaid(mermaid, outdir);
        return outpath;
    }

    can format_file_tree(tree: dict) -> str {
        def recurse(node, depth=0) {
            s = "  " * depth + "- " + node["name"] + "\n";
            if node.get("children") {
                for c in node["children"] {
                    if c["type"] == "dir" {
                        s += recurse(c, depth+1);
                    } else {
                        s += "  " * (depth+1) + "- " + c["name"] + "\n";
                    }
                }
            }
            return s;
        }
        return recurse(tree);
    }
}

# API walker entrypoint (simulate HTTP entry)
walker api {
    can submit(url: str) {
        # spawn supervisor and return the doc path (blocking in this example)
        sup = spawn CodeGenius();
        res = sup.start_with_url(url);
        return res;
    }
}
