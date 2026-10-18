import streamlit as st
import requests

from src.config_frontend import API_CHAMBRES_URL as API_URL

def get_equip_icon(equip_name: str) -> str:
    """Associe une icône explicite à chaque équipement."""
    name_lower = equip_name.lower()
    if "wi-fi" in name_lower or "wifi" in name_lower:
        return "📶"
    elif "jacuzzi" in name_lower or "bain" in name_lower:
        return "🛁"
    elif "mini" in name_lower or "bar" in name_lower:
        return "🍸"
    elif "clim" in name_lower:
        return "❄️"
    elif "tv" in name_lower or "écran" in name_lower:
        return "📺"
    elif "piscine" in name_lower:
        return "🏊"
    return "✨"

def render_chambres_page():
    # --- 1. INJECTION DU STYLING CSS CYBER-LUXE ---
    st.markdown("""
    <style>
    /* Carte Glassmorphic Chambre */
    .room-card-wrapper {
        background: #0d1322;
        border: 1px solid #1f2c40;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: all 0.3s ease;
    }
    .room-card-wrapper:hover {
        border-color: rgba(255, 42, 117, 0.5);
        box-shadow: 0 8px 25px rgba(255, 42, 117, 0.15);
    }

    /* Pilules de caractéristiques & équipements */
    .pill-spec {
        background: #131b2e;
        border: 1px solid #1f2c40;
        color: #94a3b8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Boutons Streamlit personnalisés */
    div[data-testid="stColumn"] button:disabled {
        background-color: #1a2235 !important;
        color: #64748b !important;
        border: 1px solid #1f2c40 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stColumn"] button:not(:disabled) {
        background: linear-gradient(135deg, #ff2a75 0%, #e91e63 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255, 42, 117, 0.4) !important;
        transition: all 0.25s ease-in-out !important;
    }
    div[data-testid="stColumn"] button:not(:disabled):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 42, 117, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. HERO BANNER PRINCIPAL ---
    st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(11, 15, 25, 0.95) 35%, rgba(11, 15, 25, 0.4) 100%), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1400&q=80') center/cover;
                    border-radius: 16px; padding: 28px 32px; margin-bottom: 28px; border: 1px solid #1f2c40;">
            <span style="color: #ff2a75; font-size: 0.72rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">
                CATALOGUE D'HÉBERGEMENT
            </span>
            <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 6px 0 8px 0;">
                Nos Chambres & Suites de <span style="color: #ff2a75;">Luxe</span>
            </h1>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; max-width: 580px; line-height: 1.4;">
                Découvrez notre sélection exclusive d'hébergements au cœur de la ville impériale de Meknès.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- 3. REQUÊTE FASTAPI ---
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            chambres_db = response.json()
        else:
            st.error(f"Erreur HTTP {response.status_code} lors du chargement des chambres.")
            return
    except requests.exceptions.RequestException:
        st.error("⚠️ Impossible de contacter le serveur backend sur http://127.0.0.1:8005.")
        return

    if not chambres_db:
        st.info("Aucune chambre disponible dans la base de données.")
        return

    # --- 4. LISTE DES CARTES DE CHAMBRES ---
    for chambre in chambres_db:
        stock = chambre.get("stock", 0)
        is_available = stock > 0
        btn_disabled = not is_available

        # Images & Badges sur l'image
        image_url = chambre.get("image_url") or "https://images.unsplash.com/photo-1611892440504-42a792e24d32"
        nom_chambre = chambre.get("nom", "Chambre Deluxe")
        
        if "suite" in nom_chambre.lower():
            tag_badge = "👑 Suite de Luxe"
        elif "vue" in nom_chambre.lower() or "panor" in nom_chambre.lower():
            tag_badge = "⛰️ Vue Panoramique"
        else:
            tag_badge = "🛏️ Chambre Premium"

        # Traitement des équipements
        equipements_raw = chambre.get("equipements", "")
        if isinstance(equipements_raw, str):
            equipements_list = [eq.strip() for eq in equipements_raw.split(",") if eq.strip()]
        else:
            equipements_list = equipements_raw or []

        equip_pills = "".join([
            f'<span class="pill-spec">{get_equip_icon(eq)} {eq}</span>' 
            for eq in equipements_list
        ])

        # Spécifications de base
        surface = chambre.get("surface", "45 m²")
        vue = chambre.get("vue", "Vue sur Jardin")
        lit = chambre.get("lit", "Lit King Size")

        # Description par défaut si non renseignée
        desc = chambre.get("description") or f"Une expérience d'exception au cœur de Meknès. Offrant confort, élégance et intimité pour un séjour inoubliable."

        prix_b = chambre.get("prix_basse", 0.0)
        prix_h = chambre.get("prix_haute", 0.0)

        # Rendu de la carte en 3 colonnes
        st.markdown('<div class="room-card-wrapper">', unsafe_allow_html=True)
        col_img, col_info, col_action = st.columns([1.15, 1.85, 1.15], gap="medium")

        # COLONNE 1 : Image + Badge Rose sur l'image
        with col_img:
            st.markdown(f"""
                <div style="position: relative; border-radius: 14px; overflow: hidden; border: 1px solid #1f2c40;">
                    <img src="{image_url}" style="width: 100%; height: 210px; object-fit: cover; display: block;" />
                    <div style="position: absolute; top: 10px; left: 10px; background: #ff2a75; color: #ffffff; 
                                padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700;">
                        {tag_badge}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # COLONNE 2 : Titre, Description & Pilules
        with col_info:
            st.markdown(f"""
                <h3 style="color: #ffffff; font-size: 1.3rem; font-weight: 700; margin: 0 0 6px 0;">{nom_chambre}</h3>
                <p style="color: #94a3b8; font-size: 0.8rem; line-height: 1.45; margin: 0 0 14px 0;">{desc}</p>
                
                <div style="margin-bottom: 8px;">
                    <span class="pill-spec">📐 {surface}</span>
                    <span class="pill-spec">🪟 {vue}</span>
                    <span class="pill-spec">🛏️ {lit}</span>
                </div>
                <div>
                    {equip_pills}
                </div>
            """, unsafe_allow_html=True)

        # COLONNE 3 : Statut, Tarifs & Bouton
        with col_action:
            # Badge de Statut (Haut Droite)
            if is_available:
                status_html = f"""
                    <div style="text-align: right; margin-bottom: 16px;">
                        <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); 
                                     color: #10b981; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">
                            🟢 Disponible ({stock} dispo)
                        </span>
                    </div>
                """
            else:
                status_html = """
                    <div style="text-align: right; margin-bottom: 16px;">
                        <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); 
                                     color: #ef4444; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">
                            ❌ Complet (0 disponible)
                        </span>
                    </div>
                """

            st.markdown(status_html, unsafe_allow_html=True)

            # Tarifs (Basse / Haute saison)
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 22px; 
                            border-left: 1px solid #1f2c40; padding-left: 14px;">
                    <div>
                        <div style="color: #64748b; font-size: 0.72rem; margin-bottom: 2px;">Basse saison</div>
                        <div style="color: #ff2a75; font-size: 1.3rem; font-weight: 800;">
                            {prix_b} €<span style="font-size: 0.7rem; color: #64748b; font-weight: 400;"> /nuit</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #64748b; font-size: 0.72rem; margin-bottom: 2px;">Haute saison</div>
                        <div style="color: #ffffff; font-size: 1.2rem; font-weight: 700;">
                            {prix_h} €<span style="font-size: 0.7rem; color: #64748b; font-weight: 400;"> /nuit</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Bouton d'action Streamlit
            btn_label = f"Réserver" if is_available else "🚫 Établissement complet"
            if st.button(
                btn_label, 
                key=f"btn_res_{chambre['id']}", 
                disabled=btn_disabled,
                use_container_width=True
            ):
                st.session_state.selected_chambre_id = chambre["id"]
                st.session_state.selected_chambre_res = nom_chambre
                st.session_state.current_page = "Réservation"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)