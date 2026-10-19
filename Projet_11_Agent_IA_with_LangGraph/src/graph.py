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


# ============================================================
# 1. Initialisation du modèle Mistral
# ============================================================

# Récupère la clé depuis les variables d'environnement OU les secrets Streamlit
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or st.secrets.get("MISTRAL_API_KEY")

llm = ChatMistralAI(
    model="ministral-8b-2512",
    api_key=MISTRAL_API_KEY,
    temperature=0.0
)
# ============================================================
# 2. NŒUD : Routeur d'intentions LLM avec Mistral
# ============================================================

def analyser_question(state: AgentState):
    question = (state.get("question") or state.get("message") or "").strip()

    messages = [
        SystemMessage(content=(
            "Tu es le classifieur d'intentions officiel de l'Hôtel Le Belvédère à Meknès.\n"
            "Analyse le message du client et réponds STRICTEMENT avec le nom d'une seule catégorie parmi :\n"
            "- DISPO : demande de disponibilités, chambres libres, catalogue des prix, tarif d'une nuit ou coût par chambre (ex: 'combien coûte une nuit ?', 'quel est le prix d'une chambre ?').\n"
            "- RESERVATION : volonté explicite de réserver ou bloquer une chambre.\n"
            "- MES_RESERVATIONS : consulter ses propres réservations enregistrées ou son dossier.\n"
            "- ANNULATION : volonté d'annuler ou supprimer un séjour.\n"
            "- CALCUL : UNIQUEMENT pour effectuer la multiplication/devis d'un montant total lorsque le client demande une opération arithmétique explicite (ex: 'combien font 4 nuits à 150 € ?', 'calcule le total pour 3 nuits').\n"
            "- CHAT : salutations, politesses, vœux d'accueil.\n"
            "- RAG : questions d'information sur les services de l'hôtel (animaux, chiens, petit-déjeuner, horaires, piscine, parking).\n\n"
            "CONSIGNE : Réponds UNIQUEMENT le nom de la catégorie (ex: RAG)."
        )),
        HumanMessage(content="Puis-je venir avec un petit chien et le petit-déjeuner est-il inclus ?"),
        AIMessage(content="RAG"),
        HumanMessage(content="Avez-vous une chambre disponible pour le mois prochain ?"),
        AIMessage(content="DISPO"),
        HumanMessage(content="Le prix d'une nuit"),
        AIMessage(content="DISPO"),
        HumanMessage(content="une chambre coûte combien par nuit ?"),
        AIMessage(content="DISPO"),
        HumanMessage(content="Je souhaite réserver la Suite Royale"),
        AIMessage(content="RESERVATION"),
        HumanMessage(content="Combien coûtent 4 nuits à 150 € ?"),
        AIMessage(content="CALCUL"),
        HumanMessage(content=f"Message client : \"{question}\"")
    ]

    try:
        resultat = llm.invoke(messages)
        raw_output = str(resultat.content).strip().upper()
    except Exception as e:
        print(f"⚠️ Erreur Mistral Router : {e}")
        raw_output = ""

    valid_intents = {"RAG", "DISPO", "RESERVATION", "MES_RESERVATIONS", "ANNULATION", "CALCUL", "CHAT"}
    
    words = re.findall(r'[A-Z_]+', raw_output)
    decision = next((word for word in words if word in valid_intents), "RAG")

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
# 4. NŒUD : CALCUL DE FACTURE (AVEC FALLBACK DYNAMIQUE)
# ============================================================

def executer_calcul(state: AgentState):
    question = state.get("question") or state.get("message") or ""

    match_nuits = re.search(r"(\d+)\s*nuit", question.lower())
    match_prix = re.search(r"(\d+(?:[.,]\d+)?)\s*€", question.lower())

    # Si aucun prix en € n'est fourni dans la question, basculer intelligemment vers le catalogue DISPO
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
            "jardin": "Suite Royale Vue Jardin",
            "panorama": "Vue Panaroma",
            "panaroma": "Vue Panaroma"
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
        if "panorama" in q_lower or "panaroma" in q_lower:
            for nom in noms_chambres:
                if "pan" in nom.lower():
                    chambre_cible = nom
                    break
        elif "jardin" in q_lower or "suite" in q_lower or "royale" in q_lower:
            for nom in noms_chambres:
                if "jardin" in nom.lower() or "suite" in nom.lower():
                    chambre_cible = nom
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

    status_str = f"Client connecté : {user_email}" if user_email else "Client non connecté."

    prompt = f"""Tu es l'assistant de réception de l'Hôtel Le Belvédère à Meknès.
Réponds de manière chaleureuse, professionnelle et concise au client.

Contexte client : {status_str}
Message du client : "{question}"
"""
    message = HumanMessage(content=prompt)
    resultat = llm.invoke([message])

    return {
        "resultat_outil": resultat.content,
        "reponse": resultat.content,
        "decision": "CHAT"
    }


# ============================================================
# 10. NŒUD : GÉNÉRATION DE RÉPONSE
# ============================================================

def generer_reponse(state: AgentState):
    question = state.get("question") or state.get("message") or ""
    decision = state["decision"]

    contexte = state.get("contexte", "")
    resultat_outil = state.get("resultat_outil", "")

    if decision == "RAG":
        prompt = f"""Tu es l'assistant officiel de l'Hôtel Le Belvédère à Meknès.

Réponds précisément et de façon courtoise à la question du client en consultant le contexte officiel ci-dessous.
Si le client souhaite réserver, indique-lui qu'il peut préciser la chambre souhaitée.

Contexte officiel :
{contexte}

Question du client :
{question}
"""
        message = HumanMessage(content=prompt)
        resultat = llm.invoke([message])

        return {"reponse": resultat.content}
    else:
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