# src/query_engine.py

from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.core.query_engine import BaseQueryEngine

from config.settings import Settings


class RAGQueryEngine:
    """
    Wraps LlamaIndex's query engine to provide a clean,
    simple interface for querying the indexed repository.

    It takes a built VectorStoreIndex and exposes one
    method: ask() — which handles everything internally.

    Usage:
        engine = RAGQueryEngine(index)
        answer = engine.ask("What does this repo do?")
        print(answer)
    """

    def __init__(self, index: VectorStoreIndex):
        """
        Args:
            index: A built VectorStoreIndex from RepositoryIndexer.

        Raises:
            ValueError: If index is None.
        """
        if index is None:
            raise ValueError(
                "Index cannot be None. "
                "Build the index using RepositoryIndexer first."
            )

        self._index = index
        self._engine: BaseQueryEngine = self._build_engine()

    def _build_engine(self) -> BaseQueryEngine:
        """
        Creates the LlamaIndex query engine with a custom prompt
        that tells the LLM to answer strictly from the repo content.
        """
        from llama_index.core import PromptTemplate

        qa_prompt = PromptTemplate(
            "You are a helpful assistant that answers questions about "
            "a GitHub repository.\n\n"
            "Use ONLY the following context from the repository to answer. "
            "If the answer is not in the context, say "
            "'I could not find that information in this repository.'\n\n"
            "Context:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n\n"
            "Question: {query_str}\n\n"
            "Answer: "
        )

        engine = self._index.as_query_engine(
            similarity_top_k=Settings.SIMILARITY_TOP_K
        )
        engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt})
        return engine


    def ask(self, question: str) -> str:
        """
        Takes a natural language question, retrieves the most
        relevant chunks from the index, and returns the LLM's
        answer as a plain string.

        Args:
            question: The user's question about the repository.

        Returns:
            The LLM's answer as a string.

        Raises:
            ValueError: If question is empty.
            RuntimeError: If the query fails.
        """
        self._validate_question(question)

        try:
            response = self._engine.query(question)
            return str(response)

        except Exception as e:
            raise RuntimeError(
                f"Query failed.\nReason: {str(e)}"
            )

    def _validate_question(self, question: str):
        """
        Private validation — ensures the question is not empty
        before sending it to the LLM.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
