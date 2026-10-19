import streamlit as st

def get_initials(name: str) -> str:
    """Extrait les initiales du nom complet."""
    if not name:
        return "YD"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return name[:2].upper()

def render_admin_sidebar():
    user = st.session_state.get("user", {})
    nom_admin = user.get("nom_complet", "Youssouf Diabaté")
    role_admin = user.get("role", "admin").capitalize()
    if role_admin.lower() in ["admin", "administrateur"]:
        role_admin = "Administrateur"

    initiales = get_initials(nom_admin)

    with st.sidebar:
        # 1. En-tête Logo
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px; padding-top: 10px;">
                <div style="font-size: 2.2rem; color: #f43f5e; margin-bottom: 5px;">🏰</div>
                <h3 style="margin: 0; color: #ffffff; font-size: 1.15rem; font-weight: 700; letter-spacing: -0.5px;">Hôtel Le Belvédère</h3>
                <p style="margin: 2px 0 0 0; color: #64748b; font-size: 0.75rem; font-weight: 500;">Meknès</p>
            </div>
        """, unsafe_allow_html=True)

        # 2. Carte Utilisateur / Profil
        st.markdown(f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: #f43f5e; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem;">
                        {initiales}
                    </div>
                    <div>
                        <div style="color: #ffffff; font-weight: 600; font-size: 0.85rem; line-height: 1.2;">{nom_admin}</div>
                        <div style="color: #94a3b8; font-size: 0.72rem;">{role_admin}</div>
                    </div>
                </div>
                <span style="color: #94a3b8; font-size: 0.8rem;">˅</span>
            </div>
        """, unsafe_allow_html=True)

        # 3. Items du Menu Navigation
        nav_items = [
            ("🏠  Vue globale", "Vue globale"),
            ("📅  Réservations", "Réservations"),
            ("🛏️  Chambres & Stocks", "Chambres & Stocks"),
            ("🧠  Monitoring IA", "Monitoring IA")
        ]

        if "admin_section" not in st.session_state:
            st.session_state.admin_section = "Vue globale"

        for label, section_key in nav_items:
            is_active = (st.session_state.admin_section == section_key)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"admin_nav_{section_key}", type=btn_type, use_container_width=True):
                st.session_state.admin_section = section_key
                st.rerun()

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # 4. Bouton Revenir au site client
        if st.button("🚪 Revenir au site client  ❯", key="btn_exit_admin", use_container_width=True):
            st.session_state.current_page = "Accueil"
            st.rerun()

        # 5. Pied de page du Sidebar
        st.markdown("""
            <div style="margin-top: 60px; border-top: 1px solid #1e293b; padding-top: 15px;">
                <div style="padding: 8px 0; color: #94a3b8; font-size: 0.85rem; display: flex; align-items: center; gap: 10px; cursor: pointer;">
                    ⚙️ <span>Paramètres</span>
                </div>
                <div style="padding: 8px 0; color: #94a3b8; font-size: 0.85rem; display: flex; align-items: center; gap: 10px; cursor: pointer;">
                    ❓ <span>Aide</span>
                </div>
            </div>
        """, unsafe_allow_html=True)