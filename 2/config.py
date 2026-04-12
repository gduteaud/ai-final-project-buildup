"""Configuration settings for the RAG chatbot."""
import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import openrouter_config as _shared

OPENROUTER_API_KEY = _shared.OPENROUTER_API_KEY
OPENROUTER_BASE_URL = _shared.OPENROUTER_BASE_URL
LLM_MODEL = _shared.LLM_MODEL
TEMPERATURE = 1.0
MAX_TOKENS = 500
TOP_P = 1.0
TOP_K = 50
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# Upload Configuration
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "md", "html"]
