# src/ingestion.py

import asyncio
from gitingest import ingest_async
from dataclasses import dataclass


@dataclass
class IngestionResult:
    """
    A simple container that holds the 3 things
    GitIngest returns. Using a dataclass means we get
    a clean object instead of juggling 3 loose variables.
    """
    summary: str
    tree: str
    content: str


class GitHubIngestor:
    """
    Responsible for fetching and parsing a GitHub repository
    into raw text using GitIngest.

    Usage:
        ingestor = GitHubIngestor("https://github.com/user/repo")
        result = ingestor.fetch()
        print(result.content)
    """

    def __init__(self, repo_url: str):
        """
        Args:
            repo_url: The full GitHub repository URL.
        """
        self.repo_url = repo_url
        self._result = None

    def fetch(self) -> IngestionResult:
        """
        Fetches the repository and returns an IngestionResult.
        Uses asyncio to handle gitingest's async internals
        safely inside Streamlit's environment.
        """
        self._validate_url()
        print(f"DEBUG — cleaned URL: '{self.repo_url}'")

        try:
            # gitingest uses async internally — we run it safely
            # by creating a fresh event loop ourselves
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                summary, tree, content = loop.run_until_complete(
                    ingest_async(self.repo_url)
                )
            finally:
                loop.close()

            self._result = IngestionResult(
                summary=summary,
                tree=tree,
                content=content
            )
            return self._result

        except Exception as e:
            raise RuntimeError(
                f"Failed to ingest repository '{self.repo_url}'.\n"
                f"Reason: {type(e).__name__}: {str(e)}"
            )

    def get_result(self) -> IngestionResult:
        """
        Returns the last fetched result without re-fetching.
        Raises RuntimeError if fetch() hasn't been called yet.
        """
        if self._result is None:
            raise RuntimeError(
                "No result available. Call fetch() first."
            )
        return self._result

    def _validate_url(self):
        """
        Private — cleans and validates the URL before any
        network calls.
        """
        # Strip whitespace and markdown formatting characters
        self.repo_url = self.repo_url.strip().strip("_").strip("*").strip()

        if not self.repo_url:
            raise ValueError("Repository URL cannot be empty.")

        if "github.com" not in self.repo_url:
            raise ValueError(
                f"'{self.repo_url}' does not look like a GitHub URL. "
                "Please provide a URL containing 'github.com'."
            )