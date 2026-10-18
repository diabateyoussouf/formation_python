import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8005/api/v1").rstrip("/")

API_AUTH_URL = f"{API_BASE_URL}/auth/"
API_AUTH_ME_URL = f"{API_AUTH_URL}me/"
API_RESERVATIONS_URL = f"{API_BASE_URL}/reservations/"
API_CHAMBRES_URL = f"{API_BASE_URL}/chambres/"
API_SERVICES_URL = f"{API_BASE_URL}/services/"
API_CHAT_URL = f"{API_BASE_URL}/chat/"
