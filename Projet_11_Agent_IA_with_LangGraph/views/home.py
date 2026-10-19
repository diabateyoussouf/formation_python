import uuid
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import sécurisé avec fallback pour éviter les échecs de chemin d'importation
try:
    from config_frontend import API_CHAT_URL
except ImportError:
    from src.config_frontend import API_CHAT_URL


def render_occupancy_chart():
    """Graphique lissé du Taux d'Occupation (Magenta Area Chart)."""
    dates = ["18 sept.", "19 sept.", "20 sept.", "21 sept.", "22 sept.", "23 sept.", "24 sept."]
    taux = [30, 50, 45, 60, 40, 75, 100]

    df = pd.DataFrame({"Date": dates, "Taux": taux})
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Taux"],
        mode="lines+markers",
        line=dict(color="#ff2a75", width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255, 42, 117, 0.18)",
        marker=dict(size=6, color="#ff2a75")
    ))

    fig.update_layout(
        title=dict(text="📈 Taux d'occupation des chambres", font=dict(color="#ffffff", size=13)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=10),
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1f2c40", range=[0, 105], ticksuffix="%"),
        height=200
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_room_status_donut():
    """Graphique Donut du statut des chambres (28 Total)."""
    fig = go.Figure(data=[go.Pie(
        labels=["Occupées", "Disponibles", "En maintenance"], 
        values=[28, 0, 0], 
        hole=0.74,
        marker=dict(colors=["#ff2a75", "#00e5ff", "#f59e0b"]),
        textinfo="none"
    )])

    fig.add_annotation(
        text="<b>28</b><br><span style='font-size:10px;color:#64748b;'>Total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#ffffff")
    )

    fig.update_layout(
        title=dict(text="🍩 Statut des chambres", font=dict(color="#ffffff", size=13)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=10),
        margin=dict(l=10, r=10, t=35, b=10),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.15),
        height=200
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_home_page():
    # ⚠️ Ne PAS appeler render_sidebar() ni render_header() ici : app.py le fait déjà
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Hero Banner principal avec slogan en cursive et widget Météo
    st.markdown("""
        <div style="background: linear-gradient(rgba(11, 15, 25, 0.45), rgba(11, 15, 25, 0.88)), url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1400&q=80') center/cover;
                    border-radius: 16px; padding: 28px; margin-bottom: 20px; border: 1px solid #1f2c40;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="color: #64748b; font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">TABLEAU DE BORD</span>
                    <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 6px 0 4px 0;">
                        Bonjour et bienvenue à <br><span style="color: #ff2a75;">l’Hôtel Le Belvédère !</span>
                    </h1>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0; max-width: 580px; line-height: 1.4;">
                        Votre assistant virtuel est prêt à vous accompagner dans la gestion de vos réservations, chambres, services et bien plus encore.
                    </p>
                    <div style="font-family: 'Playfair Display', serif; font-style: italic; color: #ff2a75; font-size: 1.25rem; margin-top: 12px;">
                        L’excellence de votre séjour
                    </div>
                </div>
                <div class="weather-badge">
                    <span style="font-size: 1.4rem;">☀️</span>
                    <div>
                        <b style="color: #fff;">Meknès</b><br>
                        <span style="color: #94a3b8; font-size: 0.75rem;">22°C • Ciel dégagé</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Cartes d'Accès Rapide (4 Colonnes)
    c1, c2, c3, c4 = st.columns(4)

    cards_nav = [
        ("📅", "Gérer les réservations", "Consulter et gérer toutes les réservations de l'hôtel.", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=400&q=80", "Réservation", c1),
        ("🛏️", "Voir les chambres", "Vérifier l'occupation et la disponibilité des chambres.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=400&q=80", "Chambres", c2),
        ("🏷️", "Tarifs & offres", "Gérer les tarifs et promotions spéciales.", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=400&q=80", "Services", c3),
        ("⭐", "Nos services", "Découvrir les services et équipements de l'hôtel.", "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=400&q=80", "Services", c4),
    ]

    for icon, title, desc, img, page, col in cards_nav:
        with col:
            st.markdown(f"""
                <div class="nav-card-hero" style="background-image: url('{img}');">
                    <div class="nav-card-overlay"></div>
                    <div class="nav-card-content">
                        <span style="font-size: 1.4rem;">{icon}</span>
                        <h4 style="color: #fff; margin: 8px 0 4px 0; font-size: 0.95rem; font-weight: 700;">{title}</h4>
                        <p style="color: #94a3b8; font-size: 0.72rem; margin: 0; line-height: 1.3;">{desc}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Accéder : {title}", key=f"qnav_{title}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Grille Principale Analytics & Activité
    left_col, right_col = st.columns([2.3, 1])

    with left_col:
        st.markdown("### 📊 Vue d'ensemble de l'établissement")
        
        # Row KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("""
                <div class="glass-card">
                    <span style="font-size: 0.72rem; color: #64748b;">Réservations du jour</span>
                    <h2 style="margin: 2px 0; color: #fff;">3</h2>
                    <span style="color: #10b981; font-size: 0.68rem;">▲ +50% vs. hier</span>
                </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown("""
                <div class="glass-card">
                    <span style="font-size: 0.72rem; color: #64748b;">Chambres occupées</span>
                    <h2 style="margin: 2px 0; color: #ff2a75;">100%</h2>
                    <span style="color: #ff2a75; font-size: 0.68rem;">Toutes complètes</span>
                </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown("""
                <div class="glass-card">
                    <span style="font-size: 0.72rem; color: #64748b;">Chambres disponibles</span>
                    <h2 style="margin: 2px 0; color: #fff;">0</h2>
                    <span style="color: #64748b; font-size: 0.68rem;">Aucune disponible</span>
                </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown("""
                <div class="glass-card">
                    <span style="font-size: 0.72rem; color: #64748b;">Services actifs</span>
                    <h2 style="margin: 2px 0; color: #fff;">4</h2>
                    <span style="color: #94a3b8; font-size: 0.68rem;">Resto, piscine, Wi-Fi, Spa</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphiques Plotly
        ch_a, ch_b = st.columns(2)
        with ch_a:
            render_occupancy_chart()
        with ch_b:
            render_room_status_donut()

    with right_col:
        st.markdown("### 📈 Activité récente")
        st.markdown("""
            <div class="glass-card" style="padding: 14px;">
                <div style="margin-bottom: 12px; border-bottom: 1px solid #1f2c40; padding-bottom: 8px;">
                    <span class="badge-dot"></span><b style="font-size: 0.82rem; color: #fff;">Nouvelle réservation</b>
                    <span style="color: #64748b; font-size: 0.7rem; float: right;">Il y a 12 min</span>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 14px; margin-top: 2px;">Chambre Deluxe • 2 adultes • 12 sept. 2026</div>
                </div>
                <div style="margin-bottom: 12px; border-bottom: 1px solid #1f2c40; padding-bottom: 8px;">
                    <span class="badge-dot" style="background: #10b981;"></span><b style="font-size: 0.82rem; color: #fff;">Client enregistré</b>
                    <span style="color: #64748b; font-size: 0.7rem; float: right;">Il y a 1 h</span>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 14px; margin-top: 2px;">Ahmed Benali • a terminé son séjour</div>
                </div>
                <div style="margin-bottom: 12px; border-bottom: 1px solid #1f2c40; padding-bottom: 8px;">
                    <span class="badge-dot" style="background: #00e5ff;"></span><b style="font-size: 0.82rem; color: #fff;">Chambre disponible</b>
                    <span style="color: #64748b; font-size: 0.7rem; float: right;">Il y a 2 h</span>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 14px; margin-top: 2px;">Chambre 101 • Nettoyée et prête</div>
                </div>
                <div>
                    <span class="badge-dot" style="background: #f59e0b;"></span><b style="font-size: 0.82rem; color: #fff;">Alerte IA</b>
                    <span style="color: #64748b; font-size: 0.7rem; float: right;">Il y a 4 h</span>
                    <div style="font-size: 0.72rem; color: #94a3b8; padding-left: 14px; margin-top: 2px;">Tendance de réservation en hausse pour les prochains jours</div>
                </div>
            </div>
            <br>
            <div style="background: linear-gradient(rgba(11, 15, 25, 0.3), rgba(11, 15, 25, 0.9)), url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80') center/cover;
                        border-radius: 14px; padding: 16px; border: 1px solid #1f2c40; text-align: left;">
                <b style="color: #fff; font-size: 0.85rem;">📍 Meknès, Maroc</b>
                <p style="font-size: 0.72rem; color: #cbd5e1; margin: 4px 0 10px 0;">Une expérience unique au cœur de la ville impériale.</p>
                <div style="background: #ff2a75; color: white; padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; display: inline-block; cursor: pointer;">
                    ➔ Découvrir l'hôtel
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #1f2c40;'><br>", unsafe_allow_html=True)

    # 4. Dock Chat IA en bas
    st.subheader("🤖 Poser une question à l'Assistant IA")

    active_email = st.session_state.get("user_email")
    if not active_email and isinstance(st.session_state.get("user"), dict):
        active_email = st.session_state.user.get("email")
        if active_email:
            st.session_state["user_email"] = active_email

    # Affichage de l'historique des messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "intent" in msg and msg.get("intent"):
                st.caption(f"⚙️ *Intention : `{msg['intent']}` | Latence: {msg.get('latency_ms', 0)} ms*")

    # Boutons de suggestions rapides de questions
    col_s1, col_s2, _ = st.columns([1, 1, 2])
    with col_s1:
        if st.button("🛏️ Les chambres disponibles", key="btn_sug_chambres", use_container_width=True):
            st.session_state.selected_question = "Quelles sont les chambres disponibles ?"
            st.rerun()
    with col_s2:
        if st.button("📅 Je veux faire une réservation", key="btn_sug_reser", use_container_width=True):
            st.session_state.selected_question = "Je veux faire une réservation"
            st.rerun()

    selected_prompt = st.session_state.pop("selected_question", None)
    user_input = st.chat_input("Posez votre question à l'Assistant IA...")
    prompt_to_send = selected_prompt or user_input

    if prompt_to_send:
        st.session_state.messages.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        user_email = st.session_state.get("user_email")
        user_role = st.session_state.get("user_role", "client")

        with st.chat_message("assistant"):
            with st.spinner("L'agent LangGraph analyse votre demande..."):
                try:
                    payload = {
                        "session_id": st.session_state.session_id,
                        "message": prompt_to_send,
                        "user_email": user_email.strip().lower() if user_email else None,
                        "user_role": str(user_role).lower()
                    }
                    
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(API_CHAT_URL, json=payload, headers=headers, timeout=45)
                    
                    if response.status_code == 200:
                        data = response.json()
                        bot_response = data.get("response", "Aucune réponse renvoyée.")
                        intent = data.get("intent", "INCONNU")
                        latency = data.get("latency_ms", 0)

                        st.markdown(bot_response)
                        st.caption(f"⚙️ *Intention : `{intent}` | Latence: {latency} ms*")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": bot_response,
                            "intent": intent,
                            "latency_ms": latency
                        })
                    else:
                        st.error(f"Erreur API ({response.status_code}) : {response.text}")
                except Exception as e:
                    st.error(f"Erreur de connexion avec le backend : {str(e)}")

        st.rerun()