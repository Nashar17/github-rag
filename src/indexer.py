# src/indexer.py

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from config.settings import Settings as AppSettings


class RepositoryIndexer:
    """
    Responsible for taking raw repository text and turning it
    into a searchable vector index using LlamaIndex + Ollama.

    It handles:
      - Wrapping raw text into a LlamaIndex Document
      - Chunking the document into smaller pieces
      - Embedding each chunk using nomic-embed-text via Ollama
      - Building and storing the VectorStoreIndex in memory

    Usage:
        indexer = RepositoryIndexer()
        indexer.build(content)
        index = indexer.get_index()
    """

    def __init__(self):
        """
        Sets up the LLM and embedding model using settings
        from config/settings.py. Nothing is built yet —
        that happens when build() is called.
        """
        self._index = None  # will hold the VectorStoreIndex after build()
        self._configure_llamaindex()

    def _configure_llamaindex(self):
        """
        Configures LlamaIndex's global settings to use our
        local Ollama LLM and embedding model.

        Settings.llm       → used to GENERATE answers
        Settings.embed_model → used to EMBED text into vectors
        """
        Settings.llm = Ollama(
            model=AppSettings.LLM_MODEL,
            request_timeout=AppSettings.LLM_TIMEOUT
        )

        Settings.embed_model = OllamaEmbedding(
            model_name=AppSettings.EMBED_MODEL
        )

    def build(self, content: str) -> None:
        """
        Takes the raw repo text, chunks it, embeds each chunk,
        and builds the in-memory vector index.

        Args:
            content: The full repo text returned by GitHubIngestor.

        Raises:
            ValueError: If content is empty or None.
            RuntimeError: If index building fails.
        """
        self._validate_content(content)

        try:
            # Step 1: Wrap the text as a LlamaIndex Document
            documents = [Document(text=content)]

            # Step 2: Configure the text splitter (chunker)
            splitter = SentenceSplitter(
                chunk_size=AppSettings.CHUNK_SIZE,
                chunk_overlap=AppSettings.CHUNK_OVERLAP
            )

            # Step 3: Build the index
            # This automatically: chunks → embeds → stores all vectors
            self._index = VectorStoreIndex.from_documents(
                documents,
                transformations=[splitter]
            )

        except Exception as e:
            raise RuntimeError(
                f"Failed to build index.\nReason: {str(e)}"
            )

    def get_index(self) -> VectorStoreIndex:
        """
        Returns the built VectorStoreIndex.

        Raises:
            RuntimeError: If build() has not been called yet.
        """
        if self._index is None:
            raise RuntimeError(
                "Index not built yet. Call build() first."
            )
        return self._index

    def is_ready(self) -> bool:
        """
        Returns True if the index has been built and is
        ready to be queried. Useful for UI state checks.
        """
        return self._index is not None

    def _validate_content(self, content: str):
        """
        Private validation — ensures we don't try to build
        an index from empty content.
        """
        if not content or not content.strip():
            raise ValueError(
                "Content cannot be empty. "
                "Make sure ingestion completed successfully."
            )