import streamlit as st
import requests

from src.config_frontend import API_SERVICES_URL

def get_fallback_services():
    """Données de secours enrichies si l'API REST backend est momentanément indisponible."""
    return [
        {
            "icon": "🏊‍♂️",
            "titre": "Piscine & Spa Thermal",
            "description": "Accès au Spa Les Thermes du Lac avec sauna, hammam traditionnel et jacuzzi panoramique.",
            "tag": "Inclus résidents",
            "tag_color": "green",
        },
        {
            "icon": "🍴",
            "titre": "Restaurant Gastronomique",
            "description": "Cuisine marocaine raffinée et internationale. Menu dégustation du chef et service en chambre 24/7.",
            "tag": "Sur réservation",
            "tag_color": "pink",
        },
        {
            "icon": "🚗",
            "titre": "Parking Privé & Bornes VIP",
            "description": "Parking privé couvert et surveillé avec 4 bornes de recharge électrique rapides gratuites.",
            "tag": "Service Valet",
            "tag_color": "blue",
        },
        {
            "icon": "📶",
            "titre": "Wi-Fi Fibre 500 Mbps",
            "description": "Connexion très haut débit illimitée et sécurisée accessible dans l'ensemble de l'établissement.",
            "tag": "Gratuit 24/7",
            "tag_color": "green",
        },
        {
            "icon": "🧺",
            "titre": "Blanchisserie & Pressing",
            "description": "Service de nettoyage à sec, repassage express et collecte quotidienne directement en chambre.",
            "tag": "À la demande",
            "tag_color": "blue",
        },
        {
            "icon": "🍸",
            "titre": "Lounge Bar & Terrasse",
            "description": "Cocktails créatifs, sélection de grands crus et vue panoramique sur les remparts impériaux de Meknès.",
            "tag": "Accès Libre",
            "tag_color": "pink",
        },
    ]


def render_services_page():
    # --- 1. STYLES CSS DÉDIÉS AUX SERVICES GLASSMORPHISM ---
    st.markdown(
        """
    <style>
    /* Carte Glassmorphic Service */
    .service-glass-card {
        background: #0d1322;
        border: 1px solid #1f2c40;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 190px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .service-glass-card:hover {
        border-color: rgba(255, 42, 117, 0.5);
        box-shadow: 0 8px 25px rgba(255, 42, 117, 0.2);
        transform: translateY(-4px);
    }

    /* Boîte d'icône Cyber Néon */
    .service-icon-box {
        width: 48px;
        height: 48px;
        background: rgba(255, 42, 117, 0.12);
        border: 1px solid rgba(255, 42, 117, 0.3);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }

    /* Badges de statut des services */
    .tag-badge-green {
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .tag-badge-pink {
        background: rgba(255, 42, 117, 0.12);
        color: #ff2a75;
        border: 1px solid rgba(255, 42, 117, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .tag-badge-blue {
        background: rgba(59, 130, 246, 0.12);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- 2. BANNIÈRE HERO PRINCIPALE ---
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, rgba(11, 15, 25, 0.95) 35%, rgba(11, 15, 25, 0.45) 100%), 
                    url('https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1400&q=80') center/cover;
                    border-radius: 16px; padding: 28px 32px; margin-bottom: 28px; border: 1px solid #1f2c40;">
            <span style="color: #ff2a75; font-size: 0.72rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">
                PRESTATIONS HAUT DE GAMME
            </span>
            <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 6px 0 8px 0;">
                ⭐ Nos Services & Équipements <span style="color: #ff2a75;">Exclusifs</span>
            </h1>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; max-width: 620px; line-height: 1.45;">
                Profitez d'un séjour d'exception grâce à nos installations modernes, notre spa de relaxation et nos prestations de conciergerie sur mesure au cœur de Meknès.
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- 3. REQUÊTE API REST FASTAPI ---
    try:
        response = requests.get(API_SERVICES_URL, timeout=5)
        if response.status_code == 200 and response.json():
            services_data = response.json()
        else:
            services_data = get_fallback_services()
    except requests.exceptions.RequestException:
        services_data = get_fallback_services()

    # --- 4. GRILLE RESPONSIVE 3 COLONNES ---
    cols = st.columns(3, gap="medium")
    for idx, service in enumerate(services_data):
        icon = service.get("icon", "⭐")
        titre = service.get("titre") or service.get("nom", "Service VIP")
        desc = service.get(
            "description",
            "Prestation haut de gamme réservée aux clients de l'établissement.",
        )

        tag_text = service.get("tag", "Service Client")
        tag_color = service.get("tag_color", "pink")

        badge_class = (
            f"tag-badge-{tag_color}"
            if tag_color in ["green", "pink", "blue"]
            else "tag-badge-pink"
        )

        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="service-glass-card">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                            <div class="service-icon-box">{icon}</div>
                            <span class="{badge_class}">{tag_text}</span>
                        </div>
                        <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.12rem; font-weight: 700;">{titre}</h3>
                        <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5; margin: 0;">{desc}</p>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )