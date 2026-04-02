# main.py

import asyncio
import sys
from src.ui import ChatUI


def _configure_event_loop():
    """
    Windows + Python 3.13 requires SelectorEventLoop for
    async compatibility with libraries like gitingest.
    This must be set before any async code runs.
    """
    if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )


def main():
    """
    Entry point for the GitHub RAG application.
    """
    _configure_event_loop()
    ui = ChatUI()
    ui.run()


if __name__ == "__main__":
    main()