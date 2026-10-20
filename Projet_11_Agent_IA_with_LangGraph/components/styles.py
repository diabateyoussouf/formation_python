import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@1,600&display=swap');

    /* Fond principal sombre */
    .stApp {
        background-color: #0b0f19 !important;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    /* 1. MASQUER UNIQUEMENT LE MENU 3 POINTS ET LE FOOTER (SANS MASQUER LE BOUTON SIDEBAR) */
    #MainMenu, footer, header [data-testid="stToolbar"], [data-testid="stDecoration"] { 
        visibility: hidden !important; 
        display: none !important; 
    }

    [data-testid="stHeader"] {
        background: transparent !important;
        z-index: 999990 !important;
    }

    /* 2. BOUTON HAMBURGER / FLECHE DE SIDEBAR (TOUJOURS VISIBLE ET FIXE) */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999999 !important;
        background-color: #131b2e !important;
        border: 1px solid #1f2c40 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 6px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
    }

    [data-testid="collapsedControl"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Marge supérieure du contenu principal */
    .block-container {
        padding-top: 5.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 98% !important;
    }

    /* Barre latérale (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1f2c40 !important;
    }

    /* 3. HEADER FIXE EN HAUT DE L'ÉCRAN (DESKTOP) */
    div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) {
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        left: 18rem !important; /* Aligné avec la sidebar sur PC */
        z-index: 999999 !important;
        background-color: rgba(11, 15, 25, 0.96) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 10px 1.5rem !important;
        border-bottom: 1px solid #1f2c40 !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8) !important;
    }

    /* 4. ADAPTATION RESPONSIVE MOBILE (< 992px et < 768px) */
    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) {
            left: 0 !important;
        }
    }

    @media (max-width: 768px) {
        /* Alignement du header sur une seule ligne horizontale sur mobile */
        div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 6px !important;
            padding: 8px 8px 8px 3.2rem !important; /* Laisse la place au bouton hamburger à gauche */
        }

        /* Empêcher l'empilement vertical des colonnes du header sur smartphone */
        div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) > div[data-testid="stColumn"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }

        /* La barre de recherche prend tout l'espace disponible */
        div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) > div[data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            min-width: 100px !important;
        }

        /* Masquer le texte "Invité" sur petit écran et ne garder que le badge/avatar */
        .header-user-info {
            display: none !important;
        }

        .header-profile-pill {
            padding: 4px !important;
            border-radius: 50% !important;
        }

        /* Ajustement de la marge haute pour le contenu sous le header sur mobile */
        .block-container {
            padding-top: 4.8rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
    }

    /* --- PILULE PROFIL HEADER --- */
    .user-pill-container {
        display: flex;
        justify-content: flex-end;
        width: 100%;
    }

    .header-profile-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #131b2e;
        border: 1px solid #1f2c40;
        padding: 4px 14px 4px 6px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.25s ease-in-out;
        user-select: none;
    }

    .header-profile-pill:hover {
        border-color: #ff2a75;
        box-shadow: 0 0 12px rgba(255, 42, 117, 0.35);
    }

    .header-avatar-circle {
        background: #ff2a75;
        color: #ffffff;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.75rem;
        flex-shrink: 0;
    }

    .header-user-info {
        text-align: left;
        line-height: 1.15;
    }

    .header-user-name {
        font-size: 0.78rem;
        font-weight: 700;
        color: #ffffff;
        white-space: nowrap;
    }

    .header-user-role {
        font-size: 0.65rem;
        color: #64748b;
        white-space: nowrap;
    }

    /* Superposition transparente du popover interactif */
    div[data-testid="stColumn"]:has(.user-pill-container) {
        position: relative !important;
    }

    div[data-testid="stColumn"]:has(.user-pill-container) div[data-testid="stPopover"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 10 !important;
    }

    div[data-testid="stColumn"]:has(.user-pill-container) div[data-testid="stPopover"] > button {
        width: 100% !important;
        height: 100% !important;
        border: none !important;
        background: transparent !important;
        cursor: pointer !important;
    }

    /* Cartes Glassmorphism & Input du Chat */
    .glass-card {
        background: rgba(19, 27, 46, 0.75);
        border: 1px solid #1f2c40;
        border-radius: 14px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }

    .stChatInput {
        border-radius: 25px !important;
        border: 1px solid #1f2c40 !important;
        background-color: #131b2e !important;
    }
    </style>
    """, unsafe_allow_html=True)