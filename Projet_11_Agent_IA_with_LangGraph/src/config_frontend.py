import os

# URL de base nettoyée :
# 1. Dans Docker Compose : la variable d'environnement API_BASE_URL est injectée (ex: http://backend:8005/api/v1)
# 2. Sur Streamlit Cloud / Local : retombe par défaut sur http://127.0.0.1:8000/api/v1 (démarre Uvicorn en arrière-plan)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")

# Suffixes d'authentification nettoyés (sans slash final)
API_AUTH_URL = f"{API_BASE_URL}/auth"
API_AUTH_LOGIN_URL = f"{API_AUTH_URL}/login"
API_AUTH_REGISTER_URL = f"{API_AUTH_URL}/register"
API_AUTH_ME_URL = f"{API_AUTH_URL}/me"

# Autres endpoints
API_RESERVATIONS_URL = f"{API_BASE_URL}/reservations"
API_CHAMBRES_URL = f"{API_BASE_URL}/chambres"
API_SERVICES_URL = f"{API_BASE_URL}/services"
API_CHAT_URL = f"{API_BASE_URL}/chat"