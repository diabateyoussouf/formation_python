import streamlit as st
import requests

from components.dashboard.kpi_cards import render_kpi_cards
from components.dashboard.charts import (
    render_revenue_trend_chart,
    render_room_distribution_chart
)
from components.dashboard.room_management import render_room_management
from components.dashboard.reservation_management import render_reservation_management
from components.dashboard.ai_monitoring import render_ai_monitoring_page
from config_frontend import API_RESERVATIONS_URL, API_CHAMBRES_URL, API_CHAT_URL


def _safe_fetch_json(url: str, headers: dict = None, default=None):
    """Effectue une requête GET sécurisée sans bloquer le rendu en cas d'échec."""
    try:
        response = requests.get(url, headers=headers or {}, timeout=4)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return default if default is not None else ([] if isinstance(default, list) else {})


def render_dashboard_page():
    # --- 1. CONTRÔLE D'ACCÈS SÉCURISÉ (RBAC) ---
    user = st.session_state.get("user") or {}
    token = st.session_state.get("token")
    user_role = str(user.get("role") or st.session_state.get("user_role") or "").lower()

    if not token or user_role != "admin":
        st.error("⛔ Accès refusé. Console strictement réservée aux administrateurs.")
        st.stop()

    headers = {"Authorization": f"Bearer {token}"}
    section = st.session_state.get("admin_section", "Vue globale")

    # --- 2. RÉCUPÉRATION ISOLÉE DES DONNÉES ANALYTICS & BDD ---
    stats_data = _safe_fetch_json(
        f"{API_RESERVATIONS_URL}/analytics/stats", 
        headers=headers, 
        default={}
    )
    
    monthly_data = _safe_fetch_json(
        f"{API_RESERVATIONS_URL}/analytics/monthly-revenue", 
        headers=headers, 
        default=[]
    )
    
    room_revenue_data = _safe_fetch_json(
        f"{API_RESERVATIONS_URL}/analytics/revenue-by-room", 
        headers=headers, 
        default=[]
    )
    
    rag_data = _safe_fetch_json(
        f"{API_RESERVATIONS_URL}/analytics/rag-roi", 
        headers=headers, 
        default={}
    )

    reservations = _safe_fetch_json(
        f"{API_RESERVATIONS_URL}/", 
        headers=headers, 
        default=[]
    )
    
    chambres = _safe_fetch_json(
        f"{API_CHAMBRES_URL}/", 
        headers=headers, 
        default=[]
    )

    # --- 3. CALCULS DYNAMIQUES DE STOCKS & OCCUPATION ---
    stock_total = sum([c.get("stock", 0) for c in chambres]) if chambres else 0
    total_reservations = stats_data.get("total_reservations", len(reservations))
    capacite_totale = stock_total + total_reservations
    
    taux_occupation = (
        int((total_reservations / capacite_totale) * 100) 
        if capacite_totale > 0 else 0
    )

    # --- SOUS-VUE 1 : VUE GLOBALE & ANALYTICS ---
    if section == "Vue globale":
        st.markdown("""
            <div style="margin-bottom: 25px;">
                <p style="color: #ff2a75; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;">
                    — TABLEAU DE BORD ADMINISTRATEUR
                </p>
                <h1 style="color: #ffffff; font-size: 2.2rem; font-weight: 700; margin: 0 0 10px 0;">
                    Vue globale & Performance KPI
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Chiffre d'affaires en temps réel, taux d'occupation, panier moyen et ventilation par chambre.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Cartes KPI dynamiques
        render_kpi_cards(stats_data, stock_total, taux_occupation)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphiques dynamiques
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            render_revenue_trend_chart(monthly_data)
        with col_chart2:
            render_room_distribution_chart(room_revenue_data)

        # --- 4. MODULE INTERACTIF : ASSISTANT IA CHAT ---
        st.markdown("<hr style='border: 0.5px solid #1e293b; margin: 35px 0 25px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #ffffff; font-size: 1.4rem; font-weight: 600; margin-bottom: 20px;'>💬 Poser une question à l'Assistant IA</h3>", unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        # Rendu de l'historique des messages
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Envoi et réponse en temps réel
        if prompt := st.chat_input("Posez votre question à l'Assistant IA..."):
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            payload = {
                "session_id": "sess_123456",
                "message": prompt,
                "user_email": user.get("email", "youssouf@email.com"),
                "user_role": user_role
            }

            with st.chat_message("assistant"):
                try:
                    res = requests.post(API_CHAT_URL, json=payload, headers=headers, timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        bot_response = data.get("response", "Aucune réponse retournée.")
                        st.markdown(bot_response)
                        st.session_state["messages"].append({"role": "assistant", "content": bot_response})
                    else:
                        st.error(f"Erreur serveur API ({res.status_code})")
                except Exception as e:
                    st.error(f"Erreur de connexion au backend : {e}")

    # --- SOUS-VUE 2 : RÉSERVATIONS (CRUD + FILTRES) ---
    elif section == "Réservations":
        render_reservation_management(reservations, headers)

    # --- SOUS-VUE 3 : CHAMBRES & STOCKS (CRUD) ---
    elif section == "Chambres & Stocks":
        render_room_management(chambres, headers)

    # --- SOUS-VUE 4 : MONITORING IA & PERFORMANCE RAG ---
    elif section == "Monitoring IA":
        render_ai_monitoring_page(rag_data)