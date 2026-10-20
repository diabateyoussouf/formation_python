import os
import re
from typing import Literal
import streamlit as st

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI

from src.db.session import SessionLocal
from src.db.models import ChambreModel

from .state import AgentState
from .rag import rechercher_contexte
from .tools import (
    calculer_facture, 
    verifier_disponibilite, 
    creer_reservation,
    consulter_mes_reservations,
    consulter_et_annuler_reservation
)

# ============================================================
# 1. Initialisation du modèle Mistral
# ============================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    try:
        MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY")
    except Exception:
        MISTRAL_API_KEY = None

llm = ChatMistralAI(
    model="ministral-8b-2512",
    api_key=MISTRAL_API_KEY,
    temperature=0.0
)

# ============================================================
# UTILS : RECHERCHE DYNAMIQUE DE CHAMBRE DEPUIS LA BDD
# ============================================================

def trouver_chambre_depuis_db(question: str, chambres_bdd: list) -> str:
    """Recherche une chambre en BDD de manière 100% dynamique (sans dictionnaire ni stop-words statiques)."""
    if not chambres_bdd or not question:
        return ""

    q_clean = question.lower()

    # 1. Recherche directe : nom complet de la chambre présent dans la question
    for c in chambres_bdd:
        if c.nom.lower() in q_clean:
            return c.nom

    # 2. Détection dynamique des mots fréquents depuis la BDD (ex: "Chambre", "Suite", "Vue")
    total_chambres = len(chambres_bdd)
    frequence_mots = {}
    for c in chambres_bdd:
        for mot in set(c.nom.lower().split()):
            frequence_mots[mot] = frequence_mots.get(mot, 0) + 1

    # Un mot est jugé 'commun' s'il apparaît dans plus de 50% des catégories en BDD
    mots_communs_bdd = {mot for mot, count in frequence_mots.items() if count > (total_chambres / 2)}

    # 3. Comparaison avec les mots distinctifs spécifiques
    meilleure_chambre = ""
    meilleur_score = 0

    for c in chambres_bdd:
        mots_specifiques = [m for m in c.nom.lower().split() if m not in mots_communs_bdd]
        
        # Test direct : présence du mot spécifique dans le message client
        score = sum(1 for mot in mots_specifiques if mot in q_clean)

        if score > meilleur_score:
            meilleur_score = score
            meilleure_chambre = c.nom

    return meilleure_chambre


# ============================================================
# 2. NŒUD : Routeur d'intentions contextualisé
# ============================================================

def analyser_question(state: AgentState):
    question = (state.get("question") or state.get("message") or "").strip()

    system_prompt = SystemMessage(content=(
        "Tu es le classifieur d'intentions de l'Hôtel Le Belvédère à Meknès.\n"
        "Analyse le dernier message du client EN TENANT COMPTE de l'historique.\n\n"
        "RÈGLES STRICTES DE CLASSIFICATION :\n"
        "- DISPO : si le client demande les disponibilités, le catalogue, les prix, OU s'il demande à réserver SANS NOMMER de chambre spécifique.\n"
        "- RESERVATION : UNIQUEMENT si le client exprime la volonté de réserver EN NOMMANT une catégorie de chambre.\n"
        "- MES_RESERVATIONS : consultation des réservations existantes du client.\n"
        "- ANNULATION : volonté d'annuler ou supprimer une réservation.\n"
        "- CALCUL : devis arithmétique explicite (ex: 3 x 150 €).\n"
        "- CHAT : salutations simples, présentations ('je suis Youssouf'), questions d'identité ('comment je m'appelle ?') ou sujets hors-hôtel.\n"
        "- RAG : questions sur les services de l'hôtel (animaux, parking, piscine, petit-déjeuner).\n\n"
        "Réponds UNIQUEMENT par le mot-clé (ex: DISPO)."
    ))

    messages = [system_prompt]
    historique = state.get("messages", [])
    if historique and isinstance(historique, list):
        messages.extend(historique)
    
    if not historique or (historique and getattr(historique[-1], "content", "") != question):
        messages.append(HumanMessage(content=f"Message client : \"{question}\""))

    try:
        resultat = llm.invoke(messages)
        raw_output = str(resultat.content).strip().upper()
    except Exception as e:
        print(f"⚠️ Erreur Mistral Router : {e}")
        raw_output = ""

    valid_intents = {"RAG", "DISPO", "RESERVATION", "MES_RESERVATIONS", "ANNULATION", "CALCUL", "CHAT"}
    words = re.findall(r'[A-Z_]+', raw_output)
    decision = next((word for word in words if word in valid_intents), "DISPO")

    print(f"📊 [Routeur Mistral] Raw: '{raw_output}' -> Decision: '{decision}' (Query: '{question}')")
    return {"decision": decision}


# ============================================================
# 3. NŒUD : RAG (Base de connaissances)
# ============================================================

def executer_rag(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    contexte = rechercher_contexte(question)
    return {"contexte": contexte}


# ============================================================
# 4. NŒUD : CALCUL DE FACTURE
# ============================================================

def executer_calcul(state: AgentState):
    question = state.get("question") or state.get("message") or ""

    match_nuits = re.search(r"(\d+)\s*nuit", question.lower())
    match_prix = re.search(r"(\d+(?:[.,]\d+)?)\s*€", question.lower())

    if not match_prix:
        resultat_dispo = verifier_disponibilite("")
        return {
            "resultat_outil": resultat_dispo,
            "reponse": resultat_dispo,
            "decision": "DISPO"
        }

    nombre_nuits = int(match_nuits.group(1)) if match_nuits else 1
    prix_par_nuit = float(match_prix.group(1).replace(",", "."))

    resultat = calculer_facture(nombre_nuits, prix_par_nuit)

    return {
        "nombre_nuits": nombre_nuits,
        "prix_par_nuit": prix_par_nuit,
        "resultat_outil": resultat
    }


# ============================================================
# 5. NŒUD : DISPONIBILITÉ ET TARIFS (100% DYNAMIQUE BDD)
# ============================================================

def executer_disponibilite(state: AgentState):
    question = (state.get("question") or state.get("message") or "").strip()

    db = SessionLocal()
    try:
        chambres_bdd = db.query(ChambreModel).all()
        nom_chambre = trouver_chambre_depuis_db(question, chambres_bdd)
    finally:
        db.close()

    resultat = verifier_disponibilite(nom_chambre)

    return {
        "type_chambre": nom_chambre if nom_chambre else "Catalogue complet",
        "resultat_outil": resultat
    }


# ============================================================
# 6. NŒUD : CRÉATION DE RÉSERVATION (100% DYNAMIQUE BDD)
# ============================================================

def executer_creation_reservation(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    user_email = state.get("user_email")

    db = SessionLocal()
    try:
        chambres_bdd = db.query(ChambreModel).all()
        chambre_cible = trouver_chambre_depuis_db(question, chambres_bdd)
    finally:
        db.close()

    # Si aucune chambre de la BDD n'a été spécifiée dans le message
    if not chambre_cible:
        catalogue = verifier_disponibilite("")
        msg_demande = (
            "Pour effectuer votre réservation, veuillez me préciser la chambre souhaitée.\n\n"
            f"{catalogue}\n\n"
            "👉 *Dites par exemple : « Je souhaite réserver la Chambre Deluxe Vue Piscine »*"
        )
        return {
            "resultat_outil": msg_demande,
            "reponse": msg_demande,
            "decision": "DISPO"
        }

    resultat = creer_reservation(type_chambre=chambre_cible, user_email=user_email)

    return {
        "resultat_outil": resultat,
        "reponse": resultat,
        "decision": "RESERVATION"
    }


# ============================================================
# 7. NŒUD : DOSSIER CLIENT (MES RÉSERVATIONS)
# ============================================================

def executer_mes_reservations(state: AgentState):
    user_email = state.get("user_email")
    resultat = consulter_mes_reservations(user_email=user_email)

    return {
        "resultat_outil": resultat,
        "reponse": resultat,
        "decision": "MES_RESERVATIONS"
    }


# ============================================================
# 8. NŒUD : ANNULATION
# ============================================================

def executer_annulation(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    user_email = state.get("user_email")
    user_role = state.get("user_role")

    resultat = consulter_et_annuler_reservation(
        question=question,
        user_email=user_email,
        user_role=user_role
    )

    return {
        "resultat_outil": resultat,
        "reponse": resultat,
        "decision": "ANNULATION"
    }


# ============================================================
# 9. NŒUD : CHAT GÉNÉRAL
# ============================================================

def executer_chat(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    user_email = state.get("user_email")
    status_str = f"Client connecté ({user_email})" if user_email else "Client non connecté."

    system_prompt = SystemMessage(content=f"""Tu es l'assistant de réception officiel de l'Hôtel Le Belvédère à Meknès.
Statut actuel : {status_str}

1. MÉMOIRE ET IDENTITÉ CLIENT :
- Utilise l'historique de la discussion.
- Si le client a donné son nom (ex: "je suis Diabaté Youssouf"), salue-le poliment avec son nom.
- Ne génère AUCUN crochet comme [Nom du client].

2. GARDE-FOU STRICT :
- Réponds UNIQUEMENT aux questions sur l'hôtel.
- Refuse poliment tout sujet hors-hôtel (sports, musique, politique).""")

    messages_payload = [system_prompt]
    historique = state.get("messages", [])
    if historique and isinstance(historique, list):
        messages_payload.extend(historique)

    if not historique or (historique and getattr(historique[-1], "content", "") != question):
        messages_payload.append(HumanMessage(content=question))

    resultat = llm.invoke(messages_payload)

    return {
        "resultat_outil": resultat.content,
        "reponse": resultat.content,
        "decision": "CHAT"
    }


# ============================================================
# 10. NŒUD : GÉNÉRATION DE RÉPONSE FIABILISÉE
# ============================================================

def generer_reponse(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    decision = state["decision"]

    if decision in ["RESERVATION", "ANNULATION", "MES_RESERVATIONS", "CALCUL"]:
        return {"reponse": state.get("resultat_outil", "")}

    if decision == "CHAT":
        return {"reponse": state.get("resultat_outil", "")}

    contexte = state.get("contexte", "")
    resultat_outil = state.get("resultat_outil", "")
    donnees = contexte if decision == "RAG" else resultat_outil

    system_prompt = SystemMessage(content="""Tu es la réceptionniste virtuelle de l'Hôtel Le Belvédère.

CONSIGNES STRICTES :
1. Salue le client chaleureusement en utilisant son prénom/nom s'il l'a donné dans la discussion.
2. Présente les données ci-dessous de manière élégante et polie.
3. INTERDICTION STRICTE de modifier la liste des chambres, d'inventer des types de chambres non cités ou de changer les stocks et tarifs.
4. N'utilise JAMAIS de texte de remplacement avec des crochets.""")

    messages_payload = [system_prompt]
    historique = state.get("messages", [])
    if historique and isinstance(historique, list):
        messages_payload.extend(historique)

    prompt_final = f"Message du client : \"{question}\"\n\nDonnées exactes de l'hôtel :\n{donnees}"
    messages_payload.append(HumanMessage(content=prompt_final))

    try:
        resultat = llm.invoke(messages_payload)
        return {"reponse": resultat.content}
    except Exception:
        return {"reponse": resultat_outil}


# ============================================================
# 11. ROUTEUR & GRAPHE
# ============================================================

def router(state: AgentState):
    decision = state["decision"]

    mapping = {
        "RESERVATION": "creation_reservation",
        "MES_RESERVATIONS": "mes_reservations",
        "ANNULATION": "annulation",
        "DISPO": "disponibilite",
        "CALCUL": "calcul",
        "CHAT": "chat"
    }
    return mapping.get(decision, "rag")


workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyser_question)
workflow.add_node("rag", executer_rag)
workflow.add_node("calcul", executer_calcul)
workflow.add_node("disponibilite", executer_disponibilite)
workflow.add_node("creation_reservation", executer_creation_reservation)
workflow.add_node("mes_reservations", executer_mes_reservations)
workflow.add_node("annulation", executer_annulation)
workflow.add_node("chat", executer_chat)
workflow.add_node("reponse", generer_reponse)

workflow.add_edge(START, "analyse")

workflow.add_conditional_edges(
    "analyse",
    router,
    {
        "rag": "rag",
        "calcul": "calcul",
        "disponibilite": "disponibilite",
        "creation_reservation": "creation_reservation",
        "mes_reservations": "mes_reservations",
        "annulation": "annulation",
        "chat": "chat"
    }
)

workflow.add_edge("rag", "reponse")
workflow.add_edge("calcul", "reponse")
workflow.add_edge("disponibilite", "reponse")
workflow.add_edge("creation_reservation", "reponse")
workflow.add_edge("mes_reservations", "reponse")
workflow.add_edge("annulation", "reponse")
workflow.add_edge("chat", "reponse")
workflow.add_edge("reponse", END)

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)