import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL: str = os.environ.get("API_BASE_URL", "http://localhost:5000")
API_TIMEOUT: float = float(os.environ.get("API_TIMEOUT", "5"))
CLIENT_HOST: str = os.environ.get("CLIENT_HOST", "127.0.0.1")  # 0.0.0.0 dans le conteneur Docker
CLIENT_PORT: int = int(os.environ.get("CLIENT_PORT", "5001"))
CLIENT_DEBUG: bool = os.environ.get("CLIENT_DEBUG", "false").lower() == "true"
# Nécessaire aux messages flash (session signée). À définir dans .env.
SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-only-change-me")