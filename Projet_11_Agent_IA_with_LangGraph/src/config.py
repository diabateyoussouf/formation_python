import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# 1. Chargement du fichier .env
load_dotenv()

# 2. Récupération sécurisée de la clé API Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    try:
        MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY")
    except Exception:
        MISTRAL_API_KEY = None

if not MISTRAL_API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY n'est pas définie (ni dans .env, ni dans Streamlit Secrets)"
    )

# Injection explicite dans l'environnement système pour FastAPI et LangChain
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY


# ============================================================
# 3. Gestion SQLite (Dossier /tmp/ pour Streamlit Cloud)
# ============================================================
# Racine du projet (dossier parent de src/)
ROOT_DIR = Path(__file__).resolve().parent.parent

ORIGINAL_DB_PATH = ROOT_DIR / "hotel_belvedere.db"
TMP_DB_PATH = Path("/tmp/hotel_belvedere.db")

# Copie vers /tmp/ si pas encore faite
if not TMP_DB_PATH.exists() and ORIGINAL_DB_PATH.exists():
    shutil.copyfile(ORIGINAL_DB_PATH, TMP_DB_PATH)

# Sélection du chemin inscriptible
FINAL_DB_PATH = TMP_DB_PATH if TMP_DB_PATH.exists() else ORIGINAL_DB_PATH
DATABASE_URL = f"sqlite:///{FINAL_DB_PATH}"