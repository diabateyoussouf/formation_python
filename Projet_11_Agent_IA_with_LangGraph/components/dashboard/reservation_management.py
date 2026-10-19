import streamlit as st
import requests
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

from config_frontend import API_RESERVATIONS_URL


def clean_html(html_str: str) -> str:
    """Nettoie les espaces en début de ligne pour éviter l'interprétation en bloc de code Markdown."""
    return "\n".join([line.strip() for line in html_str.splitlines() if line.strip()])


def render_reservation_management(reservations: list, headers: dict = None):
    headers = headers or {}
    base_res_url = API_RESERVATIONS_URL.rstrip("/")

    # --- 1. CSS DÉDIÉ DASHBOARD RÉSERVATIONS ---
    st.markdown("""
    <style>
    .admin-res-card {
        background: rgba(19, 27, 46, 0.85);
        border: 1px solid #1f2c40;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
        transition: all 0.25s ease;
    }
    .admin-res-card:hover {
        border-color: rgba(255, 42, 117, 0.4);
    }
    .badge-status-pending {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .badge-status-overdue {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .badge-status-confirmed {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .badge-garantie {
        background: #131b2e;
        color: #94a3b8;
        border: 1px solid #1f2c40;
        padding: 3px 8px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. EN-TÊTE DE SECTION ---
    header_html = """
    <div style="margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 1.5rem; font-weight: 800;">📋 Suivi & Gestion des Réservations</h2>
        <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 0.88rem;">
            Supervisez les pré-réservations, suivez les retards (+12h), validez les paiements ou libérez le stock.
        </p>
    </div>
    """
    st.markdown(clean_html(header_html), unsafe_allow_html=True)

    if not reservations:
        st.info("Aucune réservation enregistrée dans la base de données.")
        return

    # --- 3. TRAITEMENT ET ENRICHISSEMENT DES DONNÉES (LOGIQUE +12H) ---
    now = datetime.now()
    enriched_list = []

    for r in reservations:
        date_arr_str = str(r.get("date_arrivee", ""))
        try:
            date_arr_dt = datetime.fromisoformat(date_arr_str.replace("Z", ""))
        except ValueError:
            date_arr_dt = now

        # Heure de vérification du retard (+12h après 14:00 le jour d'arrivée)
        cutoff_dt = date_arr_dt.replace(hour=14, minute=0, second=0) + timedelta(hours=12)
        
        statut_raw = str(r.get("statut", "EN_ATTENTE")).upper()
        garantie_raw = str(r.get("mode_garantie", "RECEPTION")).upper()
        
        is_overdue = (now > cutoff_dt) and (statut_raw == "EN_ATTENTE")

        r_copy = dict(r)
        r_copy["is_overdue"] = is_overdue
        r_copy["statut_clean"] = statut_raw
        r_copy["garantie_clean"] = garantie_raw
        enriched_list.append(r_copy)

    # --- 4. BARRE DE RECHERCHE ET FILTRES DE STATUT ---
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search = st.text_input("🔍 Recherche par client ou e-mail", placeholder="Saisissez un nom ou un email...", key="res_search_input")
    with f_col2:
        filter_status = st.selectbox(
            "Filtrer par statut",
            ["Tous", "🚨 En retard (>12h)", "⏳ En attente", "🟢 Confirmées"],
            key="res_status_filter"
        )

    # Filtrage des données
    filtered = enriched_list
    if search:
        search_lower = search.lower()
        filtered = [
            r for r in filtered 
            if search_lower in str(r.get("nom_client", "")).lower() 
            or search_lower in str(r.get("email_client", "")).lower()
        ]

    if filter_status == "🚨 En retard (>12h)":
        filtered = [r for r in filtered if r["is_overdue"]]
    elif filter_status == "⏳ En attente":
        filtered = [r for r in filtered if r["statut_clean"] == "EN_ATTENTE" and not r["is_overdue"]]
    elif filter_status == "🟢 Confirmées":
        filtered = [r for r in filtered if r["statut_clean"] == "CONFIRMEE"]

    # --- 5. VUE CARTE INTERACTIVE DES RÉSERVATIONS ---
    st.markdown(f"<p style='color:#64748b; font-size:0.8rem; font-weight:600;'>{len(filtered)} réservation(s) affichée(s)</p>", unsafe_allow_html=True)

    for r in filtered:
        res_id = r["id"]
        nom = r.get("nom_client", "Client")
        email = r.get("email_client", "N/A")
        date_arr = str(r.get("date_arrivee", ""))[:10]
        date_dep = str(r.get("date_depart", ""))[:10]
        prix = r.get("prix_total", 0.0)
        statut = r["statut_clean"]
        garantie = r["garantie_clean"]
        ref_vir = r.get("ref_virement")
        is_overdue = r["is_overdue"]

        # Choix des Badges
        if is_overdue:
            badge_status = '<span class="badge-status-overdue">🚨 Retard >12h</span>'
        elif statut == "CONFIRMEE":
            badge_status = '<span class="badge-status-confirmed">🟢 Confirmée</span>'
        else:
            badge_status = '<span class="badge-status-pending">⏳ En attente</span>'

        garantie_txt = f"💳 {garantie}"
        if garantie == "VIREMENT" and ref_vir:
            garantie_txt += f" (Réf: {ref_vir})"
        elif garantie == "RECEPTION":
            garantie_txt = "🏢 Sur place (18h)"

        badge_garantie = f'<span class="badge-garantie">{garantie_txt}</span>'

        c_info, c_actions = st.columns([2.5, 1.5], gap="medium")

        with c_info:
            card_html = f"""
            <div class="admin-res-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="color:#ffffff; font-weight:700; font-size:1.05rem;">#{res_id} — {nom}</span>
                    <div style="display:flex; gap:6px;">
                        {badge_garantie}
                        {badge_status}
                    </div>
                </div>
                <div style="color:#94a3b8; font-size:0.82rem; line-height:1.4;">
                    📧 <b>{email}</b> &nbsp;|&nbsp; 📅 <b>{date_arr}</b> ➔ <b>{date_dep}</b> &nbsp;|&nbsp; 💰 <b style="color:#ff2a75;">{prix:.2f} €</b>
                </div>
            </div>
            """
            st.markdown(clean_html(card_html), unsafe_allow_html=True)

        with c_actions:
            a_col1, a_col2, a_col3 = st.columns(3)

            # Action 1 : Relance Email (Lien Mailto)
            with a_col1:
                subject = f"Relance Réservation #{res_id} - Hôtel Le Belvédère"
                body = (
                    f"Bonjour {nom},\n\n"
                    f"Votre réservation #{res_id} du {date_arr} au {date_dep} est actuellement en attente.\n"
                    f"Merci de bien vouloir confirmer votre heure d'arrivée.\n\n"
                    f"Cordialement,\nLa Réception"
                )
                mailto_url = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                st.markdown(f"""
                    <a href="{mailto_url}" target="_blank" style="text-decoration:none;">
                        <button style="background:#131b2e; border:1px solid #1f2c40; color:#e2e8f0; border-radius:10px; padding:8px; width:100%; font-size:0.75rem; font-weight:600; cursor:pointer;">
                            📧 Email
                        </button>
                    </a>
                """, unsafe_allow_html=True)

            # Action 2 : Valider / Confirmer manuellement
            with a_col2:
                if statut != "CONFIRMEE":
                    if st.button("✅ Valider", key=f"btn_confirm_{res_id}", use_container_width=True):
                        try:
                            payload = {"statut": "CONFIRMEE"}
                            up_res = requests.patch(f"{base_res_url}/{res_id}", json=payload, headers=headers, timeout=5)
                            if up_res.status_code in [200, 204]:
                                st.success(f"#{res_id} confirmée !")
                                st.rerun()
                            else:
                                st.error("Échec maj.")
                        except requests.exceptions.RequestException:
                            st.error("API hors ligne.")
                else:
                    st.button("OK", key=f"btn_done_{res_id}", disabled=True, use_container_width=True)

            # Action 3 : Annuler & Libérer la chambre
            with a_col3:
                if st.button("❌ Annuler", key=f"btn_del_{res_id}", use_container_width=True):
                    try:
                        del_res = requests.delete(f"{base_res_url}/{res_id}", headers=headers, timeout=5)
                        if del_res.status_code in [200, 204]:
                            st.success(f"Réservation #{res_id} annulée.")
                            st.rerun()
                        else:
                            st.error("Erreur annulation.")
                    except requests.exceptions.RequestException:
                        st.error("API hors ligne.")