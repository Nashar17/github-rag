# src/ingestion.py

import concurrent.futures
from dataclasses import dataclass
from gitingest import ingest


@dataclass
class IngestionResult:
    """
    A simple container that holds the 3 things
    GitIngest returns.
    """
    summary: str
    tree: str
    content: str


class GitHubIngestor:
    """
    Responsible for fetching and parsing a GitHub repository
    into raw text using GitIngest.

    Runs GitIngest in a separate thread to avoid conflicts
    with Streamlit's event loop on Windows.

    Usage:
        ingestor = GitHubIngestor("https://github.com/user/repo")
        result = ingestor.fetch()
        print(result.content)
    """

    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self._result = None

    def fetch(self) -> IngestionResult:
        """
        Fetches the repository by running GitIngest in a
        separate thread — completely isolated from Streamlit's
        event loop.
        """
        self._validate_url()
        print(f"DEBUG — fetching: '{self.repo_url}'")

        try:
            # Run ingest() in its own thread so it creates
            # its own clean event loop, isolated from Streamlit
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(ingest, self.repo_url)
                summary, tree, content = future.result(timeout=120)

            self._result = IngestionResult(
                summary=summary,
                tree=tree,
                content=content
            )
            return self._result

        except concurrent.futures.TimeoutError:
            raise RuntimeError(
                "Ingestion timed out after 120 seconds. "
                "The repository may be too large. Try a smaller repo."
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to ingest repository '{self.repo_url}'.\n"
                f"Reason: {type(e).__name__}: {str(e)}"
            )

    def get_result(self) -> IngestionResult:
        """Returns last fetched result without re-fetching."""
        if self._result is None:
            raise RuntimeError("No result available. Call fetch() first.")
        return self._result

    def _validate_url(self):
        """Cleans and validates the URL."""
        self.repo_url = self.repo_url.strip().strip("_").strip("*").strip()

        if not self.repo_url:
            raise ValueError("Repository URL cannot be empty.")

        if "github.com" not in self.repo_url:
            raise ValueError(
                f"'{self.repo_url}' does not look like a GitHub URL."
            )