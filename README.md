# 🤖 GitHub RAG

Chat with any GitHub repository using local AI — no API keys, no cloud, 100% free.

## What it does
Paste any public GitHub repository URL, and ask questions about the codebase in plain English.

## Tech Stack
- **GitIngest** — parses GitHub repos into text
- **LlamaIndex** — chunking, embedding, and retrieval
- **Ollama** — runs LLMs locally (llama3.2 + nomic-embed-text)
- **Streamlit** — chat UI

## Project Structure
```
github-rag/
├── src/
│   ├── ingestion.py       # Fetches and parses GitHub repos
│   ├── indexer.py         # Chunks, embeds, builds vector index
│   ├── query_engine.py    # Queries the index
│   └── ui.py              # Streamlit chat interface
├── config/
│   └── settings.py        # All configuration in one place
├── main.py                # Entry point
└── requirements.txt
```

## How to Run

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Make sure Ollama is running with required models**
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

**3. Run the app**
```bash
streamlit run main.py
```

👨‍💻 Author
Mohamed El-Nashar