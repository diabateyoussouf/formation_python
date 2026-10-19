import os
import shutil
import warnings
from dotenv import load_dotenv

os.environ["HF_HUB_DISABLE_SYMLINK_WARNING"] = "1"
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

#DOSSIER_DOCUMENTS = "data/documents"
#DOSSIER_CHROMA = "chroma_db"

# Chemins internes au conteneur Docker (définis par WORKING DIR /app et les volumes)
DOSSIER_DOCUMENTS = os.getenv("DOCUMENTS_PATH", "/app/data/documents")
DOSSIER_CHROMA = os.getenv("CHROMA_PATH", "/app/chroma_db")
_retriever_cache = None

def obtenir_retriever(force_reindex: bool = False):
    global _retriever_cache
    if _retriever_cache is not None and not force_reindex:
        return _retriever_cache

    generateur_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Si une réindexation forcée est demandée, supprimer l'ancienne base Chroma
    if force_reindex and os.path.exists(DOSSIER_CHROMA):
        shutil.rmtree(DOSSIER_CHROMA)

    if os.path.exists(DOSSIER_CHROMA) and os.listdir(DOSSIER_CHROMA):
        base_vectorielle = Chroma(
            persist_directory=DOSSIER_CHROMA,
            embedding_function=generateur_embeddings
        )
    else:
        print("⚡ Ingestion et vectorisation initiale des PDF...")
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