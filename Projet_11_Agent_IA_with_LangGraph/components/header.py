import streamlit as st
import requests
import extra_streamlit_components as stx

from src.config_frontend import API_AUTH_URL


def get_initials(name: str) -> str:
    """Extrait les initiales à partir du nom complet."""
    if not name:
        return "YD"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    return name[:2].upper()


def render_header():
    # Instanciation du gestionnaire de cookies
    cookie_manager = stx.CookieManager(key="header_cookie_mgr")

    # --- 1. SYNCHRONISATION DE LA SESSION ---
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.token and st.session_state.user:
        user_info = st.session_state.user if isinstance(st.session_state.user, dict) else {}
        current_email = user_info.get("email") or st.session_state.get("user_email")
        
        if current_email:
            st.session_state["user_email"] = current_email
            st.session_state["user_role"] = str(user_info.get("role") or st.session_state.get("user_role") or "client").lower()
            st.session_state["authenticated"] = True
        else:
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.authenticated = False

    is_logged_in = bool(st.session_state.token and st.session_state.get("user_email"))

    # Extractions dynamiques pour l'affichage
    if is_logged_in:
        user_info = st.session_state.user or {}
        nom = user_info.get("nom_complet") or user_info.get("nom") or st.session_state.get("user_email", "youssouf@example.com").split("@")[0].capitalize()
        role_raw = str(user_info.get("role") or st.session_state.get("user_role") or "client").lower()
        role = "Administrateur" if role_raw == "admin" else "Client"
        initiales = get_initials(nom)
    else:
        nom = "Invité"
        role = "Se connecter"
        initiales = "🔑"
        role_raw = "client"

    # --- 2. DISPOSITION DE LA BARRE SUPÉRIEURE (COLONNES OPTIMISÉES) ---
    col_search, col_bell, col_theme, col_user = st.columns([3.5, 0.5, 0.5, 2.0], vertical_alignment="center")

    # Barre de recherche universelle
    with col_search:
        search_val = st.text_input(
            "Recherche",
            placeholder="🔍 Rechercher une réservation, un client, une chambre...",
            label_visibility="collapsed",
            key="header_search_input"
        )
        if search_val:
            st.session_state["selected_question"] = search_val
            st.session_state["current_page"] = "Accueil"
            st.rerun()

    # Cloche de notification (Badge 3) - DIMENSIONS FIXES 36x36px
    with col_bell:
        st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center;">
                <div style="position: relative; background: #131b2e; border: 1px solid #1f2c40; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0;">
                    🔔
                    <span style="position: absolute; top: -2px; right: -2px; background: #ff2a75; color: white; border-radius: 50%; width: 16px; height: 16px; font-size: 0.65rem; display: flex; align-items: center; justify-content: center; font-weight: bold;">3</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Switch Mode Sombre - DIMENSIONS FIXES 36x36px
    with col_theme:
        st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center;">
                <div style="background: #131b2e; border: 1px solid #1f2c40; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0;">
                    🌙
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- 3. BLOC UTILISATEUR DYNAMIQUE (MAQUETTE + INTERACTIF) ---
    with col_user:
        # A. Visuel profil
        st.markdown(f"""
            <div class="user-pill-container">
                <div class="header-profile-pill">
                    <div class="header-avatar-circle">{initiales}</div>
                    <div class="header-user-info">
                        <div class="header-user-name">{nom}</div>
                        <div class="header-user-role">{role}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # B. Couche popover transparente capturant le clic
        with st.popover("", use_container_width=True):
            if is_logged_in:
                st.markdown(f"### {nom}")
                st.caption(f"📧 `{st.session_state.get('user_email')}`")
                
                badge_bg = "#ff2a75" if role_raw == "admin" else "#3b82f6"
                st.markdown(
                    f"<span style='background:{badge_bg}; color:white; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:bold;'>{role}</span>", 
                    unsafe_allow_html=True
                )
                st.divider()

                if role_raw == "admin":
                    if st.button("📊 Dashboard Admin", key="hdr_dash_btn", use_container_width=True):
                        st.session_state.current_page = "Dashboard Admin"
                        st.rerun()
                    st.divider()

                # Déconnexion sécurisée (Session + Purge Cookie Browser)
                if st.button("🚪 Se déconnecter", key="hdr_logout_btn", use_container_width=True):
                    st.session_state.token = None
                    st.session_state.user = None
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.session_state.authenticated = False
                    st.session_state.current_page = "Accueil"
                    try:
                        cookie_manager.delete("belvedere_token", key="hdr_del_token")
                    except Exception:
                        pass
                    st.rerun()

            else:
                tab_login, tab_register = st.tabs(["Connexion", "Inscription"])

                with tab_login:
                    email = st.text_input("E-mail", key="hdr_l_email")
                    password = st.text_input("Mot de passe", type="password", key="hdr_l_pass")

                    if st.button("Valider la connexion", key="hdr_l_btn", use_container_width=True):
                        if email and password:
                            try:
                                clean_email = email.strip().lower()
                                payload = {"username": clean_email, "password": password}
                                res = requests.post(f"{API_AUTH_URL}/login", data=payload, timeout=5)

                                if res.status_code == 200:
                                    data = res.json()
                                    token = data.get("access_token")
                                    st.session_state.token = token
                                    st.session_state.authenticated = True

                                    headers = {"Authorization": f"Bearer {token}"}
                                    me_res = requests.get(f"{API_AUTH_URL}/me", headers=headers, timeout=5)

                                    user_data = me_res.json() if me_res.status_code == 200 else {}
                                    user_data["email"] = clean_email
                                    user_data["role"] = user_data.get("role") or data.get("role", "client")

                                    st.session_state.user = user_data
                                    st.session_state["user_email"] = clean_email
                                    st.session_state["user_role"] = str(user_data["role"]).lower()

                                    # Sauvegarde du Cookie de session (30 minutes = 1800s)
                                    try:
                                        cookie_manager.set("belvedere_token", token, key="hdr_set_token", max_age=1800)
                                    except Exception:
                                        pass

                                    if st.session_state["user_role"] == "admin":
                                        st.session_state.current_page = "Dashboard Admin"

                                    st.rerun()
                                else:
                                    st.error("Identifiants incorrects.")
                            except requests.exceptions.RequestException:
                                st.error("Serveur API indisponible sur http://127.0.0.1:8005.")

                with tab_register:
                    reg_nom = st.text_input("Nom complet", key="hdr_r_nom")
                    reg_email = st.text_input("E-mail", key="hdr_r_email")
                    reg_pass = st.text_input("Mot de passe", type="password", key="hdr_r_pass")

                    if st.button("S'inscrire", key="hdr_r_btn", use_container_width=True):
                        if reg_nom and reg_email and reg_pass:
                            try:
                                payload = {
                                    "nom_complet": reg_nom,
                                    "email": reg_email.strip().lower(),
                                    "password": reg_pass,
                                    "role": "client"
                                }
                                res = requests.post(f"{API_AUTH_URL}/register", json=payload, timeout=5)

                                if res.status_code == 201:
                                    st.success("Compte créé avec succès ! Vous pouvez vous connecter.")
                                else:
                                    st.error(res.json().get("detail", "Erreur lors de l'inscription."))
                            except requests.exceptions.RequestException:
                                st.error("Serveur API indisponible.")