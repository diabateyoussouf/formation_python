import streamlit as st
import pandas as pd
import requests
import random
import matplotlib.pyplot as plt
from datetime import datetime

# Style sombre pour harmoniser Matplotlib avec Streamlit Dark Mode
plt.style.use('dark_background')

# URL de base de votre serveur FastAPI
API_URL = "http://localhost:8001/api"

st.set_page_config(
    page_title="Smart Grid Supervision | API Client",
    page_icon="⚡",
    layout="wide"
)

# ==============================================================================
# 🎨 STYLES & HERO
# ==============================================================================
st.markdown("""
<style>
    .kpi-card { background-color: #1E293B; border-radius: 12px; padding: 20px; border-left: 5px solid #3B82F6; }
    .kpi-title { color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: #F8FAFC; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.image("https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

st.title("⚡ Smart Grid Supervision (Client API)")
st.caption("🌐 Application Frontend consommant les routes REST de FastAPI (`main.py`)")

st.divider()

# ==============================================================================
# 🔄 FONCTIONS D'APPEL À VOTRE API (REQUÊTES HTTP)
# ==============================================================================
def charger_donnees_via_api():
    """Appelle la route GET /api/telemetrie/historique"""
    try:
        response = requests.get(f"{API_URL}/telemetrie/historique?limite=200", timeout=3)
        if response.status_code == 200:
            data = response.json().get("resultats", [])
            return pd.DataFrame(data)
    except requests.exceptions.ConnectionError:
        st.error("🚨 Impossible de se connecter à FastAPI ! Vérifiez que `uvicorn main:app` tourne bien sur le port 8001.")
    return pd.DataFrame()

def envoyer_trame_via_api(sensor_id, puissance, tension):
    """Appelle la route POST /api/telemetrie/enregistrer"""
    payload = {
        "sensor_id": sensor_id,
        "puissance_w": puissance,
        "tension_v": tension,
        "timestamp": datetime.now().isoformat()
    }
    try:
        res = requests.post(f"{API_URL}/telemetrie/enregistrer", json=payload, timeout=3)
        return res.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

# ==============================================================================
# 🎛️ CONTROLES ET CHARGEMENT
# ==============================================================================
st.sidebar.title("🎮 Panneau de Contrôle")
if st.sidebar.button("🔄 Rafraîchir via l'API", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.link_button("🚀 Documentation Swagger (/docs)", "http://localhost:8001/docs", use_container_width=True)

# Récupération des données depuis l'API REST
df = charger_donnees_via_api()

# ==============================================================================
# 📊 METRIQUES ET ONGLETS
# ==============================================================================
if df.empty:
    st.warning("⚠️ Aucune donnée retournée par l'API.")
else:
    # 🔧 CORRECTION DE L'ERREUR DE DATE (format='mixed')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
    df = df.sort_values(by="timestamp")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">📥 Trames Reçues (API)</div><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card" style="border-left-color: #10B981;"><div class="kpi-title">🔋 Énergie Cumulée</div><div class="kpi-value">{round(df["puissance_w"].sum()/1000, 2)} kWh</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card" style="border-left-color: #F59E0B;"><div class="kpi-title">⚡ Puissance Moyenne</div><div class="kpi-value">{round(df["puissance_w"].mean(), 1)} W</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card" style="border-left-color: #8B5CF6;"><div class="kpi-title">🔌 Tension Moyenne</div><div class="kpi-value">{round(df["tension_v"].mean(), 1)} V</div></div>', unsafe_allow_html=True)

    st.write("")

    tab_graphs, tab_data, tab_simu = st.tabs(["📊 Graphiques Avancés (Matplotlib)", "🗄️ Données Brutes (JSON)", "🧪 Simulation d'envoi HTTP"])

    with tab_graphs:
        st.subheader("📈 Analyses Avancées du Réseau Électrique")
        
        col_m1, col_m2 = st.columns(2)
        
        # 🟢 GRAPHE 1 : Double Axe Y - Puissance vs Tension
        with col_m1:
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            ax2 = ax1.twinx()

            ax1.plot(df['timestamp'], df['puissance_w'], color='#3B82F6', label='Puissance (W)', linewidth=2)
            ax2.plot(df['timestamp'], df['tension_v'], color='#F59E0B', linestyle='--', label='Tension (V)', linewidth=1.5)

            ax1.set_xlabel('Horodatage', color='#94A3B8')
            ax1.set_ylabel('Puissance (W)', color='#3B82F6')
            ax2.set_ylabel('Tension (V)', color='#F59E0B')
            ax1.tick_params(axis='x', rotation=30)
            fig1.suptitle("⚡ Corrélation Puissance vs Tension (Double Axe)", color='white', fontsize=12)
            fig1.tight_layout()
            
            st.pyplot(fig1)

        # 🟢 GRAPHE 2 : Dispersion / Stabilité de Tension selon la Puissance
        with col_m2:
            fig2, ax = plt.subplots(figsize=(7, 4))
            scatter = ax.scatter(df['puissance_w'], df['tension_v'], c=df['puissance_w'], cmap='plasma', alpha=0.8, edgecolors='none')
            
            # Ligne de référence tension nominale (230V)
            ax.axhline(230, color='#10B981', linestyle=':', label='Nominal (230V)')
            
            ax.set_xlabel('Puissance Apportée (W)', color='#94A3B8')
            ax.set_ylabel('Tension Observée (V)', color='#94A3B8')
            fig2.suptitle("🔌 Comportement de la Tension sous Charge", color='white', fontsize=12)
            fig2.tight_layout()
            
            st.pyplot(fig2)

        # 🟢 GRAPHE 3 : Boîtes à Moustaches (Boxplot) pour la détection d'Anomalies
        st.write("")
        fig3, ax = plt.subplots(figsize=(12, 3.5))
        capteurs = df['sensor_id'].unique()
        data_to_plot = [df[df['sensor_id'] == capteur]['puissance_w'].values for capteur in capteurs]
        
        bp = ax.boxplot(data_to_plot, patch_artist=True, tick_labels=capteurs)
        for patch in bp['boxes']:
            patch.set_facecolor('#8B5CF6')
            patch.set_alpha(0.6)
            
        ax.set_ylabel('Puissance (W)', color='#94A3B8')
        fig3.suptitle("📦 Distribution de la Puissance et Détection de Pics par Capteur", color='white', fontsize=12)
        fig3.tight_layout()
        
        st.pyplot(fig3)

    with tab_data:
        st.subheader("📋 Trames consommées depuis la route GET /api/telemetrie/historique")
        st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)

    with tab_simu:
        st.subheader("🧪 Simuler des requêtes HTTP POST vers l'API")
        if st.button("🚀 Envoyer 5 trames JSON via POST HTTP", use_container_width=True):
            for i in range(5):
                envoyer_trame_via_api(
                    sensor_id=f"PHONE_SIMULATED_0{random.randint(1, 3)}",
                    puissance=round(random.uniform(500.0, 2800.0), 2),
                    tension=round(random.uniform(220.0, 240.0), 1)
                )
            st.success("5 requêtes HTTP POST envoyées avec succès à FastAPI !")
            st.rerun()

st.divider()

# ==============================================================================
# ➕ FORMULAIRE D'ENVOI HTTP POST
# ==============================================================================
with st.expander("➕ Envoyer une trame individuelle (Requête HTTP POST)"):
    with st.form("form_api_post", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        sensor_input = col_f1.text_input("Capteur", "PHONE_DIRECT_01")
        p_input = col_f2.number_input("Puissance (W)", value=1500.0)
        v_input = col_f3.number_input("Tension (V)", value=230.0)
        submit = st.form_submit_button("✉️ Envoyer à FastAPI")

    if submit:
        if envoyer_trame_via_api(sensor_input, p_input, v_input):
            st.toast("Trame transmise via l'API !", icon="✅")
            st.rerun()
        else:
            st.error("Échec de l'envoi HTTP.")