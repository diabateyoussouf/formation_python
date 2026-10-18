import os

from dotenv import load_dotenv


load_dotenv()


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY n'est pas définie dans le fichier .env"
    )