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

    /* Masquer le header natif Streamlit */
    header, #MainMenu, footer { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    /* Marge supérieure pour que le contenu ne glisse pas SOUS le header fixe */
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

    /* --- FIXATION STRICTE DU HEADER EN HAUT DE L'ÉCRAN --- */
    div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) {
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        left: 18rem !important; /* Marge alignée avec la sidebar */
        z-index: 999999 !important;
        background-color: rgba(11, 15, 25, 0.96) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 12px 2rem !important;
        border-bottom: 1px solid #1f2c40 !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8) !important;
    }

    /* Ajustement responsive si la sidebar est réduite/masquée */
    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"]:has(input[key="header_search_input"]) {
            left: 0 !important;
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