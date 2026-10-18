import streamlit as st

# 1. Configuration de la page Streamlit (OBLIGATOIREMENT EN PREMIER)
st.set_page_config(page_title="Hôtel Belvédère - Meknès", page_icon="🏨", layout="wide")

import requests
import extra_streamlit_components as stx
from config_frontend import API_AUTH_ME_URL

# 2. GESTION DES COOKIES BROWSER (Persistance au F5)
cookie_manager = stx.CookieManager(key="belvedere_cookie_mgr")
auth_token = cookie_manager.get(cookie="belvedere_token")

# 3. INITIALISATION DE LA SESSION
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Accueil"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "token" not in st.session_state:
    st.session_state["token"] = None

# 4. AUTO-RECONNEXION LORS D'UN F5 (Validation du Token Cookie auprès de FastAPI)
if auth_token and not st.session_state["authenticated"]:
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = requests.get(API_AUTH_ME_URL, headers=headers, timeout=3)
        
        if res.status_code == 200:
            user_info = res.json()
            st.session_state["authenticated"] = True
            st.session_state["token"] = auth_token
            st.session_state["user"] = user_info
            
            # Restaure la vue Dashboard Admin au rechargement si l'admin était connecté
            if st.session_state["current_page"] == "Accueil":
                st.session_state["current_page"] = "Dashboard Admin"
        else:
            # Token expiré (>30 min) ou invalide -> Nettoyage
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["user"] = None
            cookie_manager.delete("belvedere_token")
    except Exception:
        pass

# 5. IMPORTS DES COMPOSANTS ET VUES
from components.styles import load_custom_css
from components.sidebar import render_sidebar
from components.sidebar_admin import render_admin_sidebar
from components.header import render_header

from views.home import render_home_page
from views.chambres import render_chambres_page
from views.reservation import render_reservation_page
from views.services import render_services_page
from views.dashboard import render_dashboard_page

# 6. APPLICATION DU THÈME CSS GLOBAL
load_custom_css()

current_page = st.session_state["current_page"]

# 7. CHOIX DYNAMIQUE DE LA SIDEBAR
if current_page == "Dashboard Admin" and st.session_state["authenticated"]:
    render_admin_sidebar()
else:
    render_sidebar()

# 8. CONTENEUR ISOLÉ POUR LE HEADER FIXE
header_container = st.container()
with header_container:
    render_header()

# 9. ROUTAGE DES VUES PRINCIPALES
if current_page == "Accueil":
    render_home_page()
elif current_page == "Dashboard Admin":
    if st.session_state["authenticated"]:
        render_dashboard_page()
    else:
        st.session_state["current_page"] = "Accueil"
        st.rerun()
elif current_page == "Chambres":
    render_chambres_page()
elif current_page == "Réservation":
    render_reservation_page()
elif current_page == "Services":
    render_services_page()
else:
    render_home_page()