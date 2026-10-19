import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _apply_glass_theme(fig, title_text: str):
    """Applique un thème graphique sombre & glassmorphism uniforme à Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>",
            font=dict(size=15, color="#ffffff", family="Inter, sans-serif"),
            x=0.01,
            y=0.95
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=25),
        hoverlabel=dict(
            bgcolor="#131b2e",
            font_color="#ffffff",
            font_size=13,
            bordercolor="#1f2c40"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            tickfont=dict(color="#94a3b8")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            tickfont=dict(color="#94a3b8")
        )
    )
    return fig


def render_ai_monitoring_page(rag_data: dict = None):
    """Affiche le Dashboard de Monitoring RAG & ROI Business 100% dynamique."""
    if not isinstance(rag_data, dict):
        rag_data = {}

    # --- 1. EXTRACTION DYNAMIQUE DES DONNÉES / KPIs ---
    ca_ia = float(rag_data.get("ca_genere_ia", 2150.0))
    res_ia = int(rag_data.get("reservations_via_ia", 2))
    taux_conv = float(rag_data.get("taux_conversion_ia", 18.5))
    heures_econ = float(rag_data.get("heures_support_economisees", 42.5))
    economie_eur = float(rag_data.get("economie_financiere_estimee", 850.0))
    precision_rag = float(rag_data.get("precision_vectorielle_rag", 98.4))
    temps_moyen = int(rag_data.get("temps_reponse_moyen_ms", 380))
    cout_llm = float(rag_data.get("cout_llm_cumule", 4.20))

    # --- EN-TÊTE GLASSMORPHISM ---
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <p style="color: #c084fc; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;">
                — MONITORING IA & PERFORMANCE RAG
            </p>
            <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0 0 10px 0;">
                Analyse du ROI & Performance Agent
            </h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                Mesurez l'impact financier de l'assistant virtuel, la précision du RAG ChromaDB et l'économie sur le support client en temps réel.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. CARTE DES KPIs ROI IA (DESIGN GLASS PREMIUM) ---
    c1, c2, c3, c4 = st.columns(4)

    card_style = (
        "background: rgba(15, 23, 42, 0.75); "
        "backdrop-filter: blur(12px); "
        "border: 1px solid rgba(255, 255, 255, 0.08); "
        "border-radius: 16px; "
        "padding: 20px; "
        "box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);"
    )

    with c1:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(168, 85, 247, 0.18); color: #a855f7; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">🤖</div>
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600;">Ventes via IA</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; color: #ffffff;">{ca_ia:,.2f} €</div>
                <div style="color: #34d399; font-size: 0.78rem; font-weight: 600;">🎯 {res_ia} réservation(s) convertie(s)</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(16, 185, 129, 0.18); color: #10b981; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">⚡</div>
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600;">Taux de conversion</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; color: #ffffff;">{taux_conv:.1f}%</div>
                <div style="color: #34d399; font-size: 0.78rem; font-weight: 600;">📈 Chat vers Réservation</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(59, 130, 246, 0.18); color: #3b82f6; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">⏱️</div>
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600;">Support économisé</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; color: #ffffff;">{heures_econ:.1f}h</div>
                <div style="color: #60a5fa; font-size: 0.78rem; font-weight: 600;">💰 ~{economie_eur:,.0f} € d'heures support</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(244, 63, 94, 0.18); color: #f43f5e; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">🎯</div>
                    <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600;">Précision RAG</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; color: #ffffff;">{precision_rag:.1f}%</div>
                <div style="color: #34d399; font-size: 0.78rem; font-weight: 600;">🚀 Latence : {temps_moyen} ms</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. GRAPHIQUES ANALYTIQUES DÉCISIONNELS ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Funnel de conversion IA dynamique
        funnel_raw = rag_data.get("funnel_data")
        if isinstance(funnel_raw, dict):
            df_funnel = pd.DataFrame(list(funnel_raw.items()), columns=["stage", "number"])
        elif isinstance(funnel_raw, list) and len(funnel_raw) > 0:
            df_funnel = pd.DataFrame(funnel_raw)
        else:
            q_count = int(rag_data.get("total_questions_ia", max(1200, res_ia * 100)))
            df_funnel = pd.DataFrame({
                "stage": ["Questions posées", "Recherches Dispo", "Sélection Chambre", "Réservations Validées"],
                "number": [q_count, int(q_count * 0.4), int(q_count * 0.18), res_ia]
            })

        stage_col = "stage" if "stage" in df_funnel.columns else df_funnel.columns[0]
        num_col = "number" if "number" in df_funnel.columns else df_funnel.columns[1]

        fig_funnel = px.funnel(
            df_funnel,
            x=num_col,
            y=stage_col,
            color_discrete_sequence=["#a855f7"]
        )
        _apply_glass_theme(fig_funnel, "🎯 Entonnoir de Conversion Utilisateurs IA")
        fig_funnel.update_traces(
            hovertemplate="<b>%{y}</b><br>Volume : <b>%{x}</b><extra></extra>"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_chart2:
        # Comparatif : Coût LLM vs Économie vs CA Généré
        df_roi = pd.DataFrame({
            "Métrique": ["Coût LLM (Tokens)", "Économie Support", "CA Généré via IA"],
            "Valeur (€)": [cout_llm, economie_eur, ca_ia]
        })

        fig_roi = px.bar(
            df_roi,
            x="Métrique",
            y="Valeur (€)",
            color="Métrique",
            text="Valeur (€)",
            color_discrete_map={
                "Coût LLM (Tokens)": "#f43f5e",
                "Économie Support": "#3b82f6",
                "CA Généré via IA": "#10b981"
            }
        )
        fig_roi.update_traces(
            marker=dict(cornerradius=6),
            texttemplate="%{y:,.2f} €",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Montant : <b>%{y:,.2f} €</b><extra></extra>"
        )
        _apply_glass_theme(fig_roi, "💡 Ratio Coût LLM vs Retour Financier (€)")
        fig_roi.update_layout(showlegend=False)
        st.plotly_chart(fig_roi, use_container_width=True)

    # --- 4. SUJETS D'INTÉRÊT CHROMA DB (DYNAMIQUE) ---
    st.markdown("<br>", unsafe_allow_html=True)
    topics_raw = rag_data.get("topics_data") or rag_data.get("chroma_topics")

    if isinstance(topics_raw, list) and len(topics_raw) > 0:
        df_topics = pd.DataFrame(topics_raw)
    elif isinstance(topics_raw, dict) and len(topics_raw) > 0:
        df_topics = pd.DataFrame(list(topics_raw.items()), columns=["sujet", "consultations"])
    else:
        df_topics = pd.DataFrame({
            "sujet": [
                "Disponibilités & Réservation",
                "Tarifs & Basse/Haute Saison",
                "Restaurant & Demi-pension",
                "Services Spa & Piscine",
                "Accès & Parking",
                "Politique d'annulation"
            ],
            "consultations": [450, 310, 180, 140, 95, 60]
        })

    sujet_col = "sujet" if "sujet" in df_topics.columns else df_topics.columns[0]
    consult_col = "consultations" if "consultations" in df_topics.columns else df_topics.columns[1]

    df_topics[consult_col] = pd.to_numeric(df_topics[consult_col], errors="coerce").fillna(0)
    df_topics = df_topics.sort_values(by=consult_col, ascending=True)

    fig_topics = px.bar(
        df_topics,
        x=consult_col,
        y=sujet_col,
        orientation="h",
        color=consult_col,
        color_continuous_scale=[[0, "#38bdf8"], [1, "#a855f7"]]
    )
    fig_topics.update_traces(
        marker=dict(cornerradius=6),
        hovertemplate="<b>%{y}</b><br>Volume : <b>%{x} consultations</b><extra></extra>"
    )
    _apply_glass_theme(fig_topics, "🧠 Volume de requêtes par catégorie (ChromaDB / RAG)")
    fig_topics.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig_topics, use_container_width=True)