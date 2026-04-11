# Config files are a convenient way to manage all configuration settings for our app in one place
# This typically includes environment variables as well as other, non-environment-specific, non-sensitive settings

import os
# Example: Load environment variables from a .env file if needed
# from dotenv import load_dotenv
# load_dotenv()

# Generic configuration settings for your Streamlit app
APP_NAME = "My Streamlit App"
DEBUG_MODE = True
DEFAULT_LANGUAGE = "en"
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "md", "html"]

# Example: Custom API endpoint (not LLM-specific)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com/v1")

# Example: Feature flags
ENABLE_UPLOADS = True
MAX_UPLOAD_SIZE_MB = 10
