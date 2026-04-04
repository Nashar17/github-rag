# src/ingestion.py

import subprocess
import tempfile
import shutil
import concurrent.futures
from dataclasses import dataclass
from gitingest import ingest


@dataclass
class IngestionResult:
    """
    Holds the result of ingesting a GitHub repository.
    """
    summary: str
    tree: str
    content: str


class GitHubIngestor:
    """
    Fetches and parses a GitHub repository into raw text.

    Strategy:
      1. Clone the repo locally using git (no async issues)
      2. Run gitingest on the local folder (also no async issues)
      3. Clean up the temp folder

    Usage:
        ingestor = GitHubIngestor("https://github.com/user/repo")
        result = ingestor.fetch()
    """

    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self._result = None

    def fetch(self) -> IngestionResult:
        """
        Clones the repo locally then ingests it with gitingest.
        All operations are synchronous — no async conflicts.
        """
        self._validate_url()
        print(f"DEBUG — fetching: '{self.repo_url}'")

        # Create a temporary folder to clone into
        tmp_dir = tempfile.mkdtemp(prefix="github_rag_")
        print(f"DEBUG — temp dir: {tmp_dir}")

        try:
            # Step 1: Clone the repo using git directly
            self._git_clone(tmp_dir)

            # Step 2: Run gitingest on the local folder
            # This path uses NO async subprocess — it reads files directly
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(ingest, tmp_dir)
                summary, tree, content = future.result(timeout=120)

            print("DEBUG — ingestion complete!")
            self._result = IngestionResult(
                summary=summary,
                tree=tree,
                content=content
            )
            return self._result

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Git clone failed.\n"
                f"Command: {e.cmd}\n"
                f"Error: {e.stderr}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to ingest repository.\n"
                f"Reason: {type(e).__name__}: {str(e)}"
            )
        finally:
            # Always clean up the temp folder, even if an error occurred
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print("DEBUG — temp dir cleaned up")

    def _git_clone(self, target_dir: str):
        """
        Clones the GitHub repo into target_dir using git.
        Uses subprocess.run which is purely synchronous —
        no event loop involved at all.
        """
        print(f"DEBUG — cloning into: {target_dir}")
        subprocess.run(
            [
                "git", "clone",
                "--depth=1",        # only latest commit (faster)
                "--single-branch",  # only default branch
                self.repo_url,
                target_dir
            ],
            check=True,             # raises CalledProcessError if git fails
            capture_output=True,    # captures stdout/stderr
            text=True               # returns strings not bytes
        )
        print("DEBUG — clone complete!")

    def get_result(self) -> IngestionResult:
        """Returns last fetched result without re-fetching."""
        if self._result is None:
            raise RuntimeError("No result available. Call fetch() first.")
        return self._result

    def _validate_url(self):
        """Cleans and validates the URL."""
        self.repo_url = self.repo_url.strip().strip("_").strip("*").strip()
        if not self.repo_url:
            raise ValueError("URL cannot be empty.")
        if "github.com" not in self.repo_url:
            raise ValueError("Not a GitHub URL.")