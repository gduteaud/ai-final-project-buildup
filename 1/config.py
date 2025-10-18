# Config files are a convenient way to manage all configuration settings for our app in one place
# This typically includes environment variables as well as other, non-environment-specific, non-sensitive settings

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Embeddings Configuration
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")

# Model Configuration
# OpenRouter model names: see https://openrouter.ai/models for options
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct:free")
TEMPERATURE = 1.0
MAX_TOKENS = 500

# Upload Configuration
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "md", "html"]
