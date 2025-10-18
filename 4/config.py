"""Configuration settings for the RAG chatbot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Embedding Configuration (required for embeddings)
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")

# Model Configuration
# OpenRouter model names: see https://openrouter.ai/models for options
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct:free")
TEMPERATURE = 1.0
MAX_TOKENS = 500

# Embedding Configuration
# Default to Jina's embedding model for retrieval
EMBEDDING_MODEL = "jina-embeddings-v3"
EMBEDDING_TASK = "text-matching"

# Processing Configuration
COLLECTION_NAME = "documents"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Configuration
TOP_K_RESULTS = 5

# Upload Configuration
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "md", "html"]

