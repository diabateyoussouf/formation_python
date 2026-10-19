import os
import shutil
import tempfile
import warnings
from dotenv import load_dotenv

os.environ["HF_HUB_DISABLE_SYMLINK_WARNING"] = "1"
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- RÉSOLUTION DYNAMIQUE DES CHEMINS (Docker vs Streamlit Cloud / Local) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Dossier des PDF (fallback dynamique sur le sous-dossier data/documents du projet)
DEFAULT_DOCS_PATH = os.path.join(BASE_DIR, "data", "documents")
DOSSIER_DOCUMENTS = os.getenv("DOCUMENTS_PATH", DEFAULT_DOCS_PATH if os.path.exists(DEFAULT_DOCS_PATH) else "data/documents")

# 2. Dossier ChromaDB :
# - Si CHROMA_PATH existe (Docker Compose), on l'utilise.
# - Sinon (Streamlit Cloud), on bascule sur /tmp/chroma_db pour éviter les erreurs de permission SQLite (os error 13).
if "CHROMA_PATH" in os.environ:
    DOSSIER_CHROMA = os.environ["CHROMA_PATH"]
else:
    DOSSIER_CHROMA = os.path.join(tempfile.gettempdir(), "chroma_db")

# Copie automatique de la base pré-existante du dépôt vers /tmp si disponible
LOCAL_REPO_CHROMA = os.path.join(BASE_DIR, "chroma_db")
if not os.path.exists(DOSSIER_CHROMA) and os.path.exists(LOCAL_REPO_CHROMA) and os.listdir(LOCAL_REPO_CHROMA):
    try:
        shutil.copytree(LOCAL_REPO_CHROMA, DOSSIER_CHROMA)
    except Exception:
        pass

os.makedirs(DOSSIER_CHROMA, exist_ok=True)
_retriever_cache = None


def obtenir_retriever(force_reindex: bool = False):
    global _retriever_cache
    if _retriever_cache is not None and not force_reindex:
        return _retriever_cache

    generateur_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Si une réindexation forcée est demandée, supprimer l'ancienne base Chroma dans /tmp
    if force_reindex and os.path.exists(DOSSIER_CHROMA):
        shutil.rmtree(DOSSIER_CHROMA)

    if os.path.exists(DOSSIER_CHROMA) and os.listdir(DOSSIER_CHROMA):
        base_vectorielle = Chroma(
            persist_directory=DOSSIER_CHROMA,
            embedding_function=generateur_embeddings
        )
    else:
        print("⚡ Ingestion et vectorisation initiale des PDF...")
        if not os.path.exists(DOSSIER_DOCUMENTS):
            os.makedirs(DOSSIER_DOCUMENTS, exist_ok=True)

        loader = PyPDFDirectoryLoader(DOSSIER_DOCUMENTS)
        documents = loader.load()

        # Découpage affiné (600 / 120) pour capturer précisément les petites consignes
        decoupeur = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=120
        )
        morceaux = decoupeur.split_documents(documents)

        base_vectorielle = Chroma.from_documents(
            documents=morceaux,
            embedding=generateur_embeddings,
            persist_directory=DOSSIER_CHROMA
        )

    # Recherche MMR (Maximal Marginal Relevance) avec k=6 pour capter pertinence et diversité
    _retriever_cache = base_vectorielle.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 15}
    )
    return _retriever_cache


def rechercher_contexte(question: str) -> str:
    """Fonction appelée par le nœud executer_rag de LangGraph."""
    retriever = obtenir_retriever()
    documents = retriever.invoke(question)
    
    if not documents:
        return "Aucune information trouvée dans la base documentaire."
        
    return "\n\n---\n\n".join(doc.page_content for doc in documents)