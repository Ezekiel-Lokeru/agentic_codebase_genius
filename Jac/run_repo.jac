# Minimal runner to clone a repo via Python helpers and return metadata
walker cli {
    can run_url(url: str) -> dict {
        py = py_module("py.repo_clone");
        info = py.clone_repo(url, null);
        tree = py.generate_file_tree(info["root"]);
        info["file_tree"] = tree;
        info["readme_summary"] = py.summarize_readme(info.get("root" , ""));
        return info;
    }
}
