from typing import TypedDict, Optional


class AgentState(TypedDict, total=False):
    # Question / Message de l'utilisateur
    question: str

    # Contexte d'authentification utilisateur (JWT / Session)
    user_email: Optional[str]
    user_role: Optional[str]

    # Décision du routeur : CHAT / RAG / DISPO / RESERVATION / MES_RESERVATIONS / ANNULATION / CALCUL
    decision: str

    # Contexte vectoriel et résultats d'outils
    contexte: Optional[str]
    resultat_outil: Optional[str]

    # Paramètres extraits pour les outils
    nombre_nuits: Optional[int]
    prix_par_nuit: Optional[float]
    type_chambre: Optional[str]
    date_arrivee: Optional[str]
    date_depart: Optional[str]

    # Réponse finale transmise à l'API
    reponse: str