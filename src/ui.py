# src/ui.py

import streamlit as st

from config.settings import Settings
from src.ingestion import GitHubIngestor
from src.indexer import RepositoryIndexer
from src.query_engine import RAGQueryEngine


class ChatUI:
    """
    Manages the entire Streamlit user interface for the
    GitHub RAG application.

    Responsibilities:
      - Page layout and configuration
      - Sidebar with repo input and controls
      - Chat message history display
      - Triggering ingestion and indexing pipeline
      - Sending questions and displaying answers

    Usage (from main.py):
        ui = ChatUI()
        ui.run()
    """

    def __init__(self):
        """
        Configures the Streamlit page and initializes
        session state variables if they don't exist yet.
        """
        st.set_page_config(
            page_title=Settings.APP_TITLE,
            page_icon="🤖",
            layout="wide"
        )
        self._init_session_state()

    def _init_session_state(self):
        """
        Initializes session state keys on first run.
        On subsequent reruns these already exist, so the
        'if not in' check protects them from being reset.
        """
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "query_engine" not in st.session_state:
            st.session_state.query_engine = None

        if "repo_indexed" not in st.session_state:
            st.session_state.repo_indexed = False

        if "current_repo" not in st.session_state:
            st.session_state.current_repo = ""

    def _render_sidebar(self) -> tuple[str, bool]:
        """
        Renders the sidebar with repo URL input and the
        ingest button.

        Returns:
            A tuple of (repo_url: str, ingest_clicked: bool)
        """
        with st.sidebar:
            st.title("⚙️ Configuration")
            st.markdown("---")

            st.markdown("### 🤖 Model")
            st.info(f"LLM: `{Settings.LLM_MODEL}`\nEmbeddings: `{Settings.EMBED_MODEL}`")

            st.markdown("### 📦 Repository")
            repo_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/user/repo",
                help="Paste any public GitHub repository URL"
            )

            ingest_clicked = st.button(
                "🚀 Ingest Repository",
                type="primary",
                use_container_width=True
            )

            # Show status if a repo is already indexed
            if st.session_state.repo_indexed:
                st.success(
                    f"✅ Ready!\n\n"
                    f"`{st.session_state.current_repo}`"
                )

            st.markdown("---")
            st.markdown(
                "**How it works:**\n"
                "1. Paste a GitHub URL\n"
                "2. Click Ingest\n"
                "3. Ask anything about the code!"
            )

        return repo_url, ingest_clicked

    def _run_ingestion_pipeline(self, repo_url: str):
        """
        Runs the full pipeline:
          GitHubIngestor → RepositoryIndexer → RAGQueryEngine

        Shows a spinner while working and updates session
        state when done.

        Args:
            repo_url: The GitHub repository URL to ingest.
        """
        with st.spinner("⏳ Fetching repository... this may take a moment."):
            try:
                # Step 1: Ingest
                ingestor = GitHubIngestor(repo_url)
                result = ingestor.fetch()

            except (ValueError, RuntimeError) as e:
                st.error(f"❌ Ingestion failed: {str(e)}")
                return

        with st.spinner("🔍 Chunking and indexing... please wait."):
            try:
                # Step 2: Index
                indexer = RepositoryIndexer()
                indexer.build(result.content)

                # Step 3: Build query engine and store in session
                engine = RAGQueryEngine(indexer.get_index())
                st.session_state.query_engine = engine
                st.session_state.repo_indexed = True
                st.session_state.current_repo = repo_url
                st.session_state.messages = []  # reset chat for new repo

                st.success("✅ Repository indexed! Start asking questions below.")
                st.rerun()

            except (ValueError, RuntimeError) as e:
                st.error(f"❌ Indexing failed: {str(e)}")
                return

    def _render_chat(self):
        """
        Renders the chat history and the chat input box.
        Handles sending questions to the RAGQueryEngine
        and displaying the answers.
        """
        # Display all previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input — only active when repo is indexed
        if st.session_state.repo_indexed:
            placeholder = "Ask anything about the repository..."
        else:
            placeholder = "Ingest a repository first to start chatting"

        user_question = st.chat_input(placeholder)

        if user_question:
            if not st.session_state.repo_indexed:
                st.warning("⚠️ Please ingest a repository first.")
                return

            # Show user message immediately
            st.session_state.messages.append({
                "role": "user",
                "content": user_question
            })
            with st.chat_message("user"):
                st.markdown(user_question)

            # Get answer from query engine
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        answer = st.session_state.query_engine.ask(
                            user_question
                        )
                    except RuntimeError as e:
                        answer = f"❌ Error: {str(e)}"

                st.markdown(answer)

            # Store assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

    def run(self):
        """
        Main entry point for the UI.
        Called from main.py — orchestrates everything.
        """
        # Header
        st.title(f"🤖 {Settings.APP_TITLE}")
        st.caption(Settings.APP_CAPTION)
        st.markdown("---")

        # Sidebar
        repo_url, ingest_clicked = self._render_sidebar()

        # Trigger pipeline if button clicked
        if ingest_clicked:
            if not repo_url:
                st.warning("⚠️ Please enter a GitHub repository URL.")
            else:
                self._run_ingestion_pipeline(repo_url)

        # Chat interface
        self._render_chat()