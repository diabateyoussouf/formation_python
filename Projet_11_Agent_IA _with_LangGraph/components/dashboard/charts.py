import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _apply_glass_chart_theme(fig, title_text: str):
    """Applique un thème graphique sombre & glassmorphism uniforme à Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>",
            font=dict(size=16, color="#ffffff", family="Inter, sans-serif"),
            x=0.01,
            y=0.95
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=55, b=25),
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


def render_revenue_trend_chart(monthly_data: list = None):
    """Graphique en aire lissée : Évolution du Chiffre d'Affaires Mensuel."""
    if monthly_data and len(monthly_data) > 0:
        df = pd.DataFrame(monthly_data)
    else:
        # Données de démonstration
        df = pd.DataFrame({
            "mois_nom": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct"],
            "chiffre_affaires": [4200, 5800, 7100, 6900, 8500, 11200, 14500, 16800, 12100, 9400]
        })

    x_col = "mois_nom" if "mois_nom" in df.columns else df.columns[0]
    y_col = "chiffre_affaires" if "chiffre_affaires" in df.columns else df.columns[1]

    df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="lines+markers",
        name="Chiffre d'affaires",
        line=dict(color="#ff2a75", width=3.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255, 42, 117, 0.12)",
        marker=dict(size=7, color="#ff2a75", symbol="circle", line=dict(color="#ffffff", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Chiffre d'Affaires : <b>%{y:,.0f} €</b><extra></extra>"
    ))

    _apply_glass_chart_theme(fig, "📈 Évolution du Chiffre d'Affaires Mensuel")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def render_room_distribution_chart(room_revenue_data: list = None, max_items: int = 5):
    """Graphique en Donut : Répartition du CA par Chambre avec regroupement dynamique Top N + Autres."""
    if room_revenue_data and len(room_revenue_data) > 0:
        df = pd.DataFrame(room_revenue_data)
    else:
        # Données de démonstration
        df = pd.DataFrame({
            "nom_chambre": ["Vue Panaroma", "Suite Royale Vue Jardin", "Suite Deluxe Impériale", "Chambre Standard", "Chambre Executive"],
            "chiffre_affaires": [505, 180, 120, 95, 60]
        })

    name_col = "nom_chambre" if "nom_chambre" in df.columns else df.columns[0]
    val_col = "chiffre_affaires" if "chiffre_affaires" in df.columns else df.columns[1]

    # Sécurité type numérique
    df[val_col] = pd.to_numeric(df[val_col], errors="coerce").fillna(0)

    # Tri par chiffre d'affaires décroissant
    df = df.sort_values(by=val_col, ascending=False)

    # --- REGROUPEMENT INTELLIGENT SI GRAND NOMBRE DE CHAMBRES ---
    if len(df) > max_items:
        df_top = df.iloc[:max_items].copy()
        autres_ca = df.iloc[max_items:][val_col].sum()
        df_others = pd.DataFrame([{name_col: "Autres chambres", val_col: autres_ca}])
        df = pd.concat([df_top, df_others], ignore_index=True)

    total_ca = df[val_col].sum()
    palette = ["#38bdf8", "#ff2a75", "#818cf8", "#34d399", "#fbbf24", "#94a3b8"]

    fig = go.Figure(data=[go.Pie(
        labels=df[name_col],
        values=df[val_col],
        hole=0.68,
        marker=dict(colors=palette, line=dict(color="#0f172a", width=2)),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>CA : <b>%{value:,.0f} €</b> (%{percent})<extra></extra>"
    )])

    _apply_glass_chart_theme(fig, "🛏️ Répartition des Revenus par Chambre")

    # Positionnement optimal de la légende verticale à droite pour éviter l'encombrement
    fig.update_layout(
        margin=dict(l=15, r=130, t=55, b=15),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color="#94a3b8")
        )
    )

    # Indice KPI au centre du Donut
    fig.add_annotation(
        text=f"<span style='font-size:11px;color:#94a3b8;'>TOTAL REVENUS</span><br><b style='font-size:16px;color:#ffffff;'>{total_ca:,.0f} €</b>",
        x=0.5, y=0.5,
        showarrow=False,
        align="center"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_ai_topics_chart(ai_topics_data: list = None):
    """Graphique en barres horizontales dynamiques : Questions les plus fréquentes (RAG IA)."""
    if ai_topics_data and len(ai_topics_data) > 0:
        df = pd.DataFrame(ai_topics_data)
    else:
        df = pd.DataFrame({
            "sujet": ["Réservations & Disponibilités", "Tarifs & Offres", "Restauration & Spa", "Parking & Accès", "Politique Annulation"],
            "requetes": [340, 210, 180, 120, 95]
        })

    sujet_col = "sujet" if "sujet" in df.columns else df.columns[0]
    req_col = "requetes" if "requetes" in df.columns else df.columns[1]

    df[req_col] = pd.to_numeric(df[req_col], errors="coerce").fillna(0)
    df = df.sort_values(by=req_col, ascending=True)

    fig = px.bar(
        df,
        x=req_col,
        y=sujet_col,
        orientation="h",
        color=req_col,
        color_continuous_scale=[[0, "#38bdf8"], [1, "#ff2a75"]]
    )

    fig.update_traces(
        marker=dict(cornerradius=6),
        hovertemplate="<b>%{y}</b><br>Volume : <b>%{x} requêtes</b><extra></extra>"
    )

    _apply_glass_chart_theme(fig, "🧠 Intentions & Questions Clients (Agent RAG)")
    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig, use_container_width=True)