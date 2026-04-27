import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
JAVA_BACKEND_URL = os.getenv("JAVA_BACKEND_URL", "http://localhost:7002")
INTERNAL_API_SECRET = os.getenv("INTERNAL_API_SECRET", "estecharat_ai_secret_key_2026")
