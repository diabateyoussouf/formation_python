import streamlit as st
import requests
from datetime import date, timedelta, datetime

from src.config_frontend import API_CHAMBRES_URL, API_RESERVATIONS_URL

def clean_html(html_str: str) -> str:
    """Nettoie les espaces en début de ligne pour éviter l'interprétation en code brut Markdown."""
    return "\n".join([line.strip() for line in html_str.splitlines() if line.strip()])


def render_reservation_page():
    # --- 1. STYLES CSS DÉDIÉS ---
    st.markdown("""
    <style>
    .res-glass-card {
        background: #0d1322;
        border: 1px solid #1f2c40;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }

    .summary-box {
        background: rgba(19, 27, 46, 0.85);
        border: 1px solid #1f2c40;
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }

    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #ff2a75 0%, #e91e63 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 18px rgba(255, 42, 117, 0.4) !important;
        transition: all 0.25s ease-in-out !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255, 42, 117, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. BANNIÈRE HERO PRINCIPALE ---
    hero_html = """
    <div style="background: linear-gradient(90deg, rgba(11, 15, 25, 0.95) 35%, rgba(11, 15, 25, 0.45) 100%), 
                url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1400&q=80') center/cover;
                border-radius: 16px; padding: 28px 32px; margin-bottom: 28px; border: 1px solid #1f2c40;">
        <span style="color: #ff2a75; font-size: 0.72rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">
            RÉSERVATION EN LIGNE
        </span>
        <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 6px 0 8px 0;">
            📅 Réserver votre <span style="color: #ff2a75;">Séjour</span>
        </h1>
        <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; max-width: 620px; line-height: 1.45;">
            Vérifiez les disponibilités en temps réel et choisissez votre mode de garantie pour valider votre séjour.
        </p>
    </div>
    """
    st.markdown(clean_html(hero_html), unsafe_allow_html=True)

    # --- 3. PRÉ-REMPLISSAGE DYNAMIQUE UTILISATEUR ---
    user = st.session_state.get("user") or {}
    default_nom = user.get("nom_complet") or user.get("nom") or ""
    default_email = st.session_state.get("user_email") or ""

    # --- 4. RÉCUPÉRATION DES CHAMBRES FASTAPI ---
    chambres_list = []
    try:
        response = requests.get(API_CHAMBRES_URL, timeout=5)
        if response.status_code == 200:
            chambres_list = response.json()
        else:
            st.error("Impossible de charger le catalogue de chambres depuis le serveur.")
            return
    except requests.exceptions.RequestException:
        st.error("⚠️ Serveur Backend indisponible sur http://127.0.0.1:8005.")
        return

    if not chambres_list:
        st.warning("Aucune chambre n'est répertoriée dans le système.")
        return

    chambre_dict = {c["nom"]: c for c in chambres_list}
    chambre_names = list(chambre_dict.keys())

    selected_chambre_name = st.session_state.get("selected_chambre_res", chambre_names[0])
    default_index = chambre_names.index(selected_chambre_name) if selected_chambre_name in chambre_names else 0

    # --- 5. DISPOSITION EN 2 COLONNES ---
    col_form, col_summary = st.columns([2.2, 1.1], gap="large")

    with col_form:
        with st.form("form_reservation"):
            st.markdown("<h3 style='color:#fff; font-size:1.1rem; font-weight:700; margin-bottom:14px;'>📝 1. Coordonnées & Séjour</h3>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                nom_client = st.text_input("Nom complet *", value=default_nom, placeholder="Ex: Youssouf Diabaté")
                date_arrivee = st.date_input("Date d'arrivée *", value=date.today())
                type_chambre = st.selectbox("Type de chambre *", chambre_names, index=default_index)

            with c2:
                email_client = st.text_input("Adresse E-mail *", value=default_email, placeholder="Ex: contact@client.com")
                date_depart = st.date_input("Date de départ *", value=date.today() + timedelta(days=2))
                nb_personnes = st.number_input("Nombre de personnes", min_value=1, max_value=4, value=2)

            st.markdown("<h3 style='color:#fff; font-size:1.1rem; font-weight:700; margin-top:20px; margin-bottom:14px;'>💳 2. Mode de Garantie & Paiement</h3>", unsafe_allow_html=True)
            
            choice_garantie = st.radio(
                "Comment souhaitez-vous garantir votre réservation ?",
                [
                    "🏢 Paiement à la réception (Garantie d'arrivée jusqu'à 18h00)",
                    "🏦 Virement bancaire (Acompte de 30% requis)",
                    "💳 Carte Bancaire / Simulation Sandbox (Confirmation immédiate)"
                ],
                index=0
            )

            ref_virement = ""
            if "Virement bancaire" in choice_garantie:
                st.info("📌 **RIB Hôtel Le Belvédère** : `MA64 0077 8000 0123 4567 8901 2345` (Bank Of Africa Meknès)")
                ref_virement = st.text_input("Référence ou Numéro d'ordre du virement", placeholder="Ex: VIR-894021")

            if "Carte Bancaire" in choice_garantie:
                cb_c1, cb_c2, cb_c3 = st.columns([2, 1, 1])
                with cb_c1:
                    st.text_input("Numéro de carte (Test)", value="4242 •••• •••• 4242", disabled=True)
                with cb_c2:
                    st.text_input("Exp.", value="12/28", disabled=True)
                with cb_c3:
                    st.text_input("CVC", value="123", disabled=True)

            cgv_ok = st.checkbox("J'accepte la politique d'annulation (chambre conservée jusqu'à 18h00 sans virement).")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("💳 Valider la Réservation", use_container_width=True)

    # --- 6. RÉCAPITULATIF & APERÇU DE LA CHAMBRE SÉLECTIONNÉE ---
    with col_summary:
        selected_obj = chambre_dict.get(type_chambre, chambres_list[0])
        
        image_url = selected_obj.get("image_url") or "https://images.unsplash.com/photo-1611892440504-42a792e24d32"
        surface = selected_obj.get("surface", "45 m²")
        vue = selected_obj.get("vue", "Vue impériale")
        prix_basse = selected_obj.get("prix_basse", 0.0)
        stock = selected_obj.get("stock", 0)
        
        nuits_est = (date_depart - date_arrivee).days if date_depart > date_arrivee else 1
        total_est = prix_basse * nuits_est
        acompte_est = total_est * 0.30

        status_badge = f'🟢 {stock} disponible(s)' if stock > 0 else '🔴 Épuisé'
        status_color = '#10b981' if stock > 0 else '#ef4444'

        summary_html = f"""
        <div class="summary-box">
            <h4 style="color: #ff2a75; font-size: 0.78rem; font-weight: 800; letter-spacing: 1.2px; margin: 0 0 12px 0; text-transform: uppercase;">
                📊 DÉTAILS DE LA RÉSERVATION
            </h4>
            <div style="position: relative; border-radius: 12px; overflow: hidden; border: 1px solid #1f2c40; margin-bottom: 12px;">
                <img src="{image_url}" style="width: 100%; height: 120px; object-fit: cover; display: block;" />
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 4px;">{type_chambre}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 10px;">Hôtel Le Belvédère - Meknès</div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
                <span style="background: #131b2e; border: 1px solid #1f2c40; color: #94a3b8; padding: 3px 8px; border-radius: 8px; font-size: 0.7rem;">📐 {surface}</span>
                <span style="background: #131b2e; border: 1px solid #1f2c40; color: #94a3b8; padding: 3px 8px; border-radius: 8px; font-size: 0.7rem;">🪟 {vue}</span>
            </div>
            <div style="border-top: 1px solid #1f2c40; border-bottom: 1px solid #1f2c40; padding: 10px 0; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.8rem; margin-bottom: 6px;">
                    <span>Durée séjour :</span>
                    <span style="color: #fff; font-weight: 600;">{nuits_est} nuit(s)</span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.8rem; margin-bottom: 6px;">
                    <span>Acompte estimé (30%) :</span>
                    <span style="color: #ff2a75; font-weight: 700;">{acompte_est:.2f} €</span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.8rem;">
                    <span>Disponibilité :</span>
                    <span style="color: {status_color}; font-weight: 700;">{status_badge}</span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 14px;">
                <span style="color: #cbd5e1; font-weight: 600; font-size: 0.88rem;">Total Séjour :</span>
                <span style="color: #ff2a75; font-size: 1.4rem; font-weight: 800;">{total_est:.2f} €</span>
            </div>
        </div>
        """
        st.markdown(clean_html(summary_html), unsafe_allow_html=True)

    # --- 7. TRAITEMENT DE LA SOUMISSION ET MAP PREDICATE ---
    if submit_btn:
        if not cgv_ok:
            st.warning("⚠️ Veuillez accepter les conditions d'annulation pour poursuivre.")
            return

        nuits = (date_depart - date_arrivee).days
        if nuits <= 0:
            st.error("La date de départ doit être strictement postérieure à la date d'arrivée.")
            return

        if not nom_client or not email_client:
            st.error("Veuillez renseigner votre nom complet et votre adresse e-mail.")
            return

        chambre_obj = chambre_dict[type_chambre]

        if chambre_obj["stock"] <= 0:
            st.error(f"Désolé, la '{type_chambre}' est actuellement épuisée.")
            return

        # Mappage des modes de garantie et statuts pour la base de données
        if "Virement bancaire" in choice_garantie:
            mode_garantie_key = "VIREMENT"
            statut_key = "EN_ATTENTE"
            msg_confirm = f"Réservation enregistrée sous référence de virement ({ref_virement or 'N/A'})."
        elif "Carte Bancaire" in choice_garantie:
            mode_garantie_key = "CARTE"
            statut_key = "CONFIRMEE"
            msg_confirm = "Paiement CB simulé avec succès ! Votre réservation est 100% confirmée."
        else:
            mode_garantie_key = "RECEPTION"
            statut_key = "EN_ATTENTE"
            msg_confirm = "Pré-réservation enregistrée. Votre chambre est bloquée jusqu'à 18h00."

        payload = {
            "nom_client": nom_client,
            "email_client": email_client,
            "chambre_id": chambre_obj["id"],
            "date_arrivee": datetime.combine(date_arrivee, datetime.min.time()).isoformat(),
            "date_depart": datetime.combine(date_depart, datetime.min.time()).isoformat(),
            "nb_personnes": nb_personnes,
            "statut": statut_key,
            "mode_garantie": mode_garantie_key,
            "ref_virement": ref_virement if mode_garantie_key == "VIREMENT" else None
        }

        try:
            res_response = requests.post(API_RESERVATIONS_URL, json=payload, timeout=10)
            if res_response.status_code == 201:
                res_data = res_response.json()
                st.success(f"🎉 Réservation N°#{res_data['id']} validée pour {nom_client} !")
                st.info(f"📌 **Statut** : `{res_data.get('statut', statut_key)}` | 💰 **Montant total** : **{res_data['prix_total']:.2f} €**\n\n{msg_confirm}")
            else:
                err_detail = res_response.json().get("detail", "Erreur lors de la réservation.")
                st.error(f"Erreur API ({res_response.status_code}) : {err_detail}")
        except requests.exceptions.RequestException:
            st.error("⚠️ Échec de communication avec l'API de réservation.")