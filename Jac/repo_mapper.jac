"""RepoMapper agent for Codebase Genius"""

# Import Python helper functions
import py.repo_clone { clone_repo, generate_file_tree, summarize_readme }

# Node to store repository metadata
node RepoInfo:
    has name: str
    has root_path: str
    has summary: str
    has file_tree: dict

# Walker to perform repo mapping
walker RepoMapper:
    has repo_url: str
    can start entry {
        try:
            print(f"Cloning repo: {self.repo_url}")
            repo_info = clone_repo(self.repo_url)
            print("Clone complete")

            print("Generating file tree...")
            file_tree = generate_file_tree(repo_info["root"])

            print("Summarizing README...")
            summary = summarize_readme(repo_info["root"])

            print("Creating RepoInfo node...")
            info = spawn node::RepoInfo(
                name=repo_info["name"],
                root_path=repo_info["root"],
                summary=summary,
                file_tree=file_tree
            )

            print("Repo mapping complete!")
            report info

        except Exception as e:
            print("Error:", str(e))
            report {"error": str(e)}
    }
