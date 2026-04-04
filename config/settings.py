# config/settings.py

class Settings:
    """
    Central configuration for the GitHub RAG application.
    All settings are defined here so you only need to change
    things in one place.
    """

    # ── Ollama LLM ──────────────────────────────────────────
    # The model used to ANSWER your questions
    LLM_MODEL = "llama3.2:1b"

    # How long to wait for Ollama to respond (in seconds)
    # Large repos may need more time
    LLM_TIMEOUT = 120.0

    # ── Embedding Model ──────────────────────────────────────
    # The model used to convert text chunks into vectors
    # This runs through Ollama locally
    EMBED_MODEL = "nomic-embed-text"

    # ── Chunking Settings ────────────────────────────────────
    # How many tokens per chunk when splitting the repo text
    CHUNK_SIZE = 512

    # How many tokens overlap between consecutive chunks
    # Overlap helps avoid losing context at chunk boundaries
    CHUNK_OVERLAP = 50

    # ── Retrieval Settings ───────────────────────────────────
    # How many chunks to retrieve for each question
    # Higher = more context but slower
    SIMILARITY_TOP_K = 5

    # ── Streamlit UI ─────────────────────────────────────────
    APP_TITLE = "GitHub RAG"
    APP_CAPTION = "Chat with any GitHub repository using local AI"