# main.py
from src.ui import ChatUI

def main():
    """
    Entry point for the GitHub RAG application.
    """
    ui = ChatUI()
    ui.run()


if __name__ == "__main__":
    main()