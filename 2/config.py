"""Configuration settings for the RAG chatbot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model Configuration
# OpenRouter model names: see https://openrouter.ai/models for options
LLM_MODEL = "meta-llama/llama-4-maverick:free"
TEMPERATURE = 1.0
MAX_TOKENS = 500
TOP_P = 1.0
TOP_K = 50
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# Upload Configuration
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "md", "html"]

