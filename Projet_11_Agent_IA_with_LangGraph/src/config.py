import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Récupération depuis les variables d'environnement (.env) OU les secrets Streamlit
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or st.secrets.get("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY n'est pas définie (ni dans le fichier .env, ni dans Streamlit Secrets)"
    )