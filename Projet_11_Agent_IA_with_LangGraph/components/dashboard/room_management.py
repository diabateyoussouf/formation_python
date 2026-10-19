import streamlit as st
import requests

from src.config_frontend import API_CHAMBRES_URL

def clean_html(html_str: str) -> str:
    """Nettoie les espaces en début de ligne pour éviter l'interprétation en bloc de code Markdown."""
    return "\n".join([line.strip() for line in html_str.splitlines() if line.strip()])


def render_room_management(chambres: list, headers: dict = None):
    headers = headers or {}

    # --- 1. CSS DÉDIÉ DARK GLASSMORPHISM ---
    st.markdown("""
    <style>
    .room-glass-card {
        background: rgba(13, 19, 34, 0.85);
        border: 1px solid #1f2c40;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35);
        transition: all 0.25s ease-in-out;
    }
    .room-glass-card:hover {
        border-color: rgba(255, 42, 117, 0.4);
        box-shadow: 0 12px 30px rgba(255, 42, 117, 0.12);
    }
    .room-pill {
        background: #131b2e;
        border: 1px solid #1f2c40;
        color: #94a3b8;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-stock-ok {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-stock-out {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .price-tag-basse {
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .price-tag-haute {
        color: #ff2a75;
        font-weight: 700;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. EN-TÊTE DE LA SECTION ---
    header_html = """
    <div style="margin-bottom: 24px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 1.5rem; font-weight: 800;">🛏️ Gestion du Catalogue & Des Stocks</h2>
        <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 0.88rem;">
            Administrez les catégories de chambres, ajustez les grilles tarifaires et gérez les disponibilités en temps réel.
        </p>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

    # --- 3. FORMULAIRE D'AJOUT D'UNE CHAMBRE ---
    with st.expander("➕ Ajouter une nouvelle catégorie au catalogue", expanded=False):
        with st.form("form_add_room", clear_on_submit=True):
            st.markdown("<h4 style='color:#fff; font-size:0.95rem; font-weight:700; margin-bottom:12px;'>📝 Caractéristiques de la chambre</h4>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                nom = st.text_input("Nom de la chambre *", placeholder="ex: Suite Royale Vue Jardin")
                surface = st.text_input("Surface *", placeholder="ex: 45 m²")
                vue = st.text_input("Vue *", placeholder="ex: Vue sur le jardin impérial")
                lit = st.text_input("Type de lit *", placeholder="ex: Lit King Size VIP")
            with c2:
                prix_basse = st.number_input("Prix basse saison (€) *", min_value=0.0, value=180.0, step=10.0)
                prix_haute = st.number_input("Prix haute saison (€) *", min_value=0.0, value=230.0, step=10.0)
                stock = st.number_input("Nombre de chambres en stock *", min_value=0, value=3)

            st.markdown("<h4 style='color:#fff; font-size:0.95rem; font-weight:700; margin-top:12px; margin-bottom:12px;'>🖼️ Média & Équipements</h4>", unsafe_allow_html=True)
            image_url = st.text_input("URL de l'image *", value="https://images.unsplash.com/photo-1611892440504-42a792e24d32")
            equipements = st.text_input("Équipements (séparés par des virgules) *", value="Wi-Fi Fibre, Jacuzzi, Mini-bar, Climatisation, Coffre-fort")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_add = st.form_submit_button("💾 Enregistrer la chambre dans le catalogue", use_container_width=True)

            if submit_add:
                if nom and surface and vue and lit and image_url and equipements:
                    payload = {
                        "nom": nom,
                        "surface": surface,
                        "vue": vue,
                        "lit": lit,
                        "prix_basse": prix_basse,
                        "prix_haute": prix_haute,
                        "stock": stock,
                        "image_url": image_url,
                        "equipements": equipements
                    }
                    try:
                        res = requests.post(API_CHAMBRES_URL, json=payload, headers=headers, timeout=5)
                        if res.status_code == 201:
                            st.success(f"🎉 Chambre '{nom}' créée avec succès !")
                            st.rerun()
                        else:
                            st.error(f"Erreur API ({res.status_code}) : {res.text}")
                    except requests.exceptions.RequestException:
                        st.error("⚠️ Impossible de contacter le serveur backend.")
                else:
                    st.warning("Veuillez remplir tous les champs obligatoires.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. AFFICHAGE ET GESTION DU CATALOGUE DE CHAMBRES ---
    if chambres:
        st.markdown(f"<p style='color:#64748b; font-size:0.8rem; font-weight:600;'>{len(chambres)} catégorie(s) enregistrée(s)</p>", unsafe_allow_html=True)

        for ch in chambres:
            ch_id = ch["id"]
            nom_ch = ch.get("nom", "Chambre")
            stock_val = ch.get("stock", 0)
            img_src = ch.get("image_url") or "https://images.unsplash.com/photo-1611892440504-42a792e24d32"
            
            p_basse = float(ch.get("prix_basse", 0.0))
            p_haute = float(ch.get("prix_haute", 0.0))
            
            surf = ch.get("surface", "N/A")
            vue_txt = ch.get("vue", "N/A")
            lit_txt = ch.get("lit", "N/A")
            eq_txt = ch.get("equipements", "")

            # Badge de stock
            if stock_val > 0:
                stock_badge = f'<span class="badge-stock-ok">🟢 {stock_val} en stock</span>'
            else:
                stock_badge = '<span class="badge-stock-out">🔴 Épuisée</span>'

            # Transformation des équipements en pilules HTML
            eq_items = [e.strip() for e in eq_txt.split(",") if e.strip()] if eq_txt else []
            eq_badges_html = "".join([f'<span class="room-pill">✨ {item}</span>' for item in eq_items])

            with st.container():
                col_img, col_info, col_actions = st.columns([1.2, 2.8, 1.2], gap="medium")

                # Colonne 1 : Image
                with col_img:
                    st.image(img_src, use_container_width=True)

                # Colonne 2 : Informations détaillées en HTML Glass
                with col_info:
                    info_html = f"""
                    <div style="margin-bottom: 6px;">
                        <span style="color:#ffffff; font-size:1.15rem; font-weight:800; margin-right:8px;">{nom_ch}</span>
                        <span style="color:#64748b; font-size:0.75rem; font-weight:700;">ID #{ch_id}</span>
                        <div style="float: right;">{stock_badge}</div>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span class="room-pill">📐 {surf}</span>
                        <span class="room-pill">👁️ {vue_txt}</span>
                        <span class="room-pill">🛏️ {lit_txt}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        {eq_badges_html}
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; border-top:1px solid #1f2c40; padding-top:6px; margin-top:6px;">
                        Basse saison : <span class="price-tag-basse">{p_basse:.2f} €</span> / nuit &nbsp;|&nbsp; 
                        Haute saison : <span class="price-tag-haute">{p_haute:.2f} €</span> / nuit
                    </div>
                    """
                    st.markdown(clean_html(info_html), unsafe_allow_html=True)

                # Colonne 3 : Actions rapides (Popover d'Édition & Popover de Suppression)
                with col_actions:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    btn_col1, btn_col2 = st.columns(2)

                    # Popover 1 : Édition rapide
                    with btn_col1:
                        with st.popover("✏️ Éditer", use_container_width=True):
                            st.markdown(f"<h4 style='color:#fff; font-size:0.9rem; font-weight:700;'>Modifier {nom_ch}</h4>", unsafe_allow_html=True)
                            with st.form(f"form_edit_{ch_id}"):
                                new_stock = st.number_input("Stock disponible", value=stock_val, min_value=0, key=f"s_{ch_id}")
                                new_pb = st.number_input("Tarif basse saison (€)", value=p_basse, min_value=0.0, step=5.0, key=f"pb_{ch_id}")
                                new_ph = st.number_input("Tarif haute saison (€)", value=p_haute, min_value=0.0, step=5.0, key=f"ph_{ch_id}")
                                new_img = st.text_input("URL Image", value=img_src, key=f"img_{ch_id}")
                                new_eq = st.text_input("Équipements", value=eq_txt, key=f"eq_{ch_id}")

                                if st.form_submit_button("💾 Appliquer", use_container_width=True):
                                    update_payload = {
                                        "stock": new_stock,
                                        "prix_basse": new_pb,
                                        "prix_haute": new_ph,
                                        "image_url": new_img,
                                        "equipements": new_eq
                                    }
                                    res = requests.put(f"{API_CHAMBRES_URL}{ch_id}", json=update_payload, headers=headers)
                                    if res.status_code == 200:
                                        st.success("Modifications enregistrées !")
                                        st.rerun()
                                    else:
                                        st.error(f"Erreur API : {res.text}")

                    # Popover 2 : Confirmation de Suppression
                    with btn_col2:
                        with st.popover("🗑️ Suppr.", use_container_width=True):
                            st.warning(f"Supprimer définitivement la catégorie #{ch_id} ?")
                            if st.button("Oui, supprimer", key=f"del_{ch_id}", type="primary", use_container_width=True):
                                res = requests.delete(f"{API_CHAMBRES_URL}{ch_id}", headers=headers)
                                if res.status_code in [200, 204]:
                                    st.success("Chambre supprimée.")
                                    st.rerun()
                                else:
                                    st.error("Échec de la suppression.")

            st.markdown("<hr style='border:0; border-top:1px solid #1f2c40; margin: 16px 0;'>", unsafe_allow_html=True)

    else:
        st.info("Aucune catégorie de chambre n'est répertoriée dans le catalogue.")