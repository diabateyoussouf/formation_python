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
# 2. NŒUD : Routeur d'intentions contextualisé
# ============================================================

def analyser_question(state: AgentState):
    question = (state.get("question") or state.get("message") or "").strip()

    system_prompt = SystemMessage(content=(
        "Tu es le classifieur d'intentions de l'Hôtel Le Belvédère à Meknès.\n"
        "Analyse le dernier message du client EN TENANT COMPTE de l'historique de la conversation.\n\n"
        "Réponds STRICTEMENT avec l'un des mots suivants :\n"
        "- DISPO : si le client demande les chambres libres, les prix, les tarifs, OU S'IL FOURNIT SES DATES/PRÉCISIONS suite à une question sur les disponibilités.\n"
        "- RESERVATION : si le client dit 'je veux réserver', 'je prends', 'réservez-moi', 'je veux une [nom de chambre]'.\n"
        "- MES_RESERVATIONS : consultation du dossier ou des réservations existantes.\n"
        "- ANNULATION : volonté EXPLICITE d'annuler ou supprimer une réservation.\n"
        "- CALCUL : calcul d'un montant arithmétique explicite (ex: 3 x 150 €).\n"
        "- CHAT : salutations simples sans demande de chambre ('bonjour', 'comment allez-vous'), présentations ('je m'appelle X'), questions sur l'identité ('qui suis-je ?') ou sujets hors-hôtel.\n"
        "- RAG : questions sur les services (animaux, parking, piscine, petit-déjeuner, horaire).\n\n"
        "RÈGLE D'OR : Si le message contient à la fois une salutation ET une demande de chambre/prix, choisis DISPO ou RESERVATION, PAS CHAT !\n"
        "Réponds uniquement le mot-clé (ex: DISPO)."
    ))

    # Construction du contexte pour que le routeur comprenne les suites de discussion
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
# 5. NŒUD : DISPONIBILITÉ ET TARIFS
# ============================================================

def executer_disponibilite(state: AgentState):
    question = (state.get("question") or state.get("message") or "").lower()

    db = SessionLocal()
    try:
        chambres_bdd = db.query(ChambreModel).all()
        noms_chambres = [c.nom for c in chambres_bdd]
    finally:
        db.close()

    nom_chambre = ""
    for nom in noms_chambres:
        if nom.lower() in question:
            nom_chambre = nom
            break

    if not nom_chambre:
        termes_specifiques = {
            "patio": "Chambre Supérieure Vue Patio",
            "piscine": "Chambre Deluxe Vue Piscine",
            "jardin": "Suite Royale Vue Jardin",
            "panorama": "Vue Panaroma",
            "panaroma": "Vue Panaroma",
            "atlas": "Suite Executive Atlas",
            "medina": "Suite Familiale Médina"
        }
        for terme, nom_associe in termes_specifiques.items():
            if terme in question:
                nom_chambre = nom_associe
                break

    resultat = verifier_disponibilite(nom_chambre)

    return {
        "type_chambre": nom_chambre if nom_chambre else "Catalogue complet",
        "resultat_outil": resultat
    }


# ============================================================
# 6. NŒUD : CRÉATION DE RÉSERVATION
# ============================================================

def executer_creation_reservation(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    user_email = state.get("user_email")
    q_lower = question.lower()

    db = SessionLocal()
    try:
        chambres_bdd = db.query(ChambreModel).all()
        noms_chambres = [c.nom for c in chambres_bdd]
    finally:
        db.close()

    chambre_cible = ""
    for nom in noms_chambres:
        if nom.lower() in q_lower:
            chambre_cible = nom
            break

    if not chambre_cible:
        termes = {
            "patio": "Chambre Supérieure Vue Patio",
            "piscine": "Chambre Deluxe Vue Piscine",
            "jardin": "Suite Royale Vue Jardin",
            "panorama": "Vue Panaroma",
            "atlas": "Suite Executive Atlas"
        }
        for key, val in termes.items():
            if key in q_lower:
                chambre_cible = val
                break

    if not chambre_cible and noms_chambres:
        chambre_cible = noms_chambres[0]

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
# 10. NŒUD : GÉNÉRATION DE RÉPONSE FIABILISÉE (SANS HALLUCINATIONS)
# ============================================================

def generer_reponse(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    decision = state["decision"]

    # Pour les outils métiers (RESERVATION, ANNULATION, MES_RESERVATIONS, CALCUL), 
    # on renvoie directement le résultat exact généré par la base de données/l'outil
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