import streamlit as st

def get_initials(name: str) -> str:
    """Extrait les initiales à partir du nom complet."""
    if not name:
        return "👤"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    return name[:2].upper()

def render_sidebar():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Accueil"

    # --- EXTRACTION DYNAMIQUE DE LA SESSION ---
    user = st.session_state.get("user")
    user_email = st.session_state.get("user_email")
    token = st.session_state.get("token")
    
    is_logged_in = bool(token and user_email)

    if is_logged_in:
        user_info = user if isinstance(user, dict) else {}
        nom_display = user_info.get("nom_complet") or user_info.get("nom") or user_email.split("@")[0].capitalize()
        role_raw = str(user_info.get("role") or st.session_state.get("user_role") or "client").lower()
        is_admin = (role_raw == "admin")
        role_title = "Administrateur" if is_admin else "Client"
        initiales = get_initials(nom_display)
        status_html = '<div style="font-size: 0.7rem; color: #10b981; margin-top: 2px;">🟢 En ligne</div>'
    else:
        is_admin = False
        nom_display = "Invité"
        role_title = "Non connecté"
        initiales = "🔑"
        status_html = '<div style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">⚪ Non connecté</div>'

    with st.sidebar:
        # En-tête Logo Rose
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <div style="background: rgba(255, 42, 117, 0.15); border-radius: 12px; padding: 8px; font-size: 1.5rem;">🏨</div>
                <div>
                    <h3 style="margin: 0; color: #ffffff; font-size: 1.15rem; font-weight: 800; letter-spacing: 0.5px;">Hôtel Le Belvédère</h3>
                    <p style="margin: 0; color: #ff2a75; font-size: 0.75rem; font-weight: 600;">Meknès</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Carte Profil Dynamique
        st.markdown(f"""
            <div style="background: rgba(19, 27, 46, 0.85); border: 1px solid #1f2c40; border-radius: 14px; padding: 12px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
                <div style="background: linear-gradient(135deg, #ff2a75, #e91e63); color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem;">
                    {initiales}
                </div>
                <div>
                    <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff;">{nom_display}</div>
                    <div style="font-size: 0.72rem; color: #64748b;">{role_title}</div>
                    {status_html}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Navigation Principale
        st.markdown("<p style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>MENU</p>", unsafe_allow_html=True)

        menu_items = [
            ("🏠 Vue globale", "Accueil"),
            ("📅 Réservations", "Réservation"),
            ("🛏️ Chambres & Stocks", "Chambres"),
            ("🧠 Monitoring IA", "Dashboard Admin" if is_admin else "Services")
        ]

        for label, page_key in menu_items:
            is_active = (st.session_state.current_page == page_key)
            
            if is_active:
                st.markdown(f"""
                    <div style="background: linear-gradient(90deg, rgba(255, 42, 117, 0.25) 0%, rgba(255, 42, 117, 0.05) 100%); 
                                border-left: 4px solid #ff2a75; padding: 10px 14px; border-radius: 0 10px 10px 0; color: #ffffff; font-weight: 700; margin-bottom: 8px;">
                        {label}
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(label, key=f"sb_nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Bouton Voir le site client
        if st.button("↗️ Voir le site client", key="btn_view_client_site", use_container_width=True):
            st.session_state.current_page = "Accueil"
            st.rerun()

        st.markdown("""
            <div style="margin-top: 30px; border-top: 1px solid #1f2c40; padding-top: 15px; font-size: 0.85rem; color: #64748b;">
                <p style="margin: 6px 0; cursor: pointer;">⚙️ Paramètres</p>
                <p style="margin: 6px 0; cursor: pointer;">❓ Aide</p>
            </div>
            <div style="background: url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&q=80') center/cover;
                        border-radius: 12px; padding: 12px; margin-top: 20px; position: relative; overflow: hidden; min-height: 110px; display: flex; align-items: flex-end;">
                <div style="background: rgba(13, 19, 34, 0.88); padding: 8px 12px; border-radius: 8px; width: 100%; backdrop-filter: blur(4px);">
                    <p style="margin: 0; color: #ff2a75; font-size: 0.8rem; font-weight: 700;">📍 Meknès, Maroc</p>
                    <p style="margin: 0; color: #cbd5e1; font-size: 0.68rem; font-style: italic;">Une expérience unique au cœur de la ville impériale</p>
                </div>
            </div>
        """, unsafe_allow_html=True)