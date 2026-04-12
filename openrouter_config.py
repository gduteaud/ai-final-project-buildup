"""OpenRouter credentials and model names — set once via the project root `.env`.

Lesson apps import these through their local `config.py`. Copy `.env.example` to
`.env` in this same directory (next to `docker-compose.yml`).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

LLM_MODEL = "google/gemma-4-31b-it"
EMBEDDING_MODEL = "openai/text-embedding-3-small"
