import streamlit as st

def render_kpi_cards(stats_data: dict, stock_total: int, taux_occupation: int):
    ca_total = stats_data.get("chiffre_affaires_total", 0.0)
    total_res = stats_data.get("total_reservations", 0)
    panier_moyen = stats_data.get("panier_moyen", 0.0)
    duree_moyenne = stats_data.get("duree_moyenne_sejour_jours", 0.0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(244, 63, 94, 0.15); color: #f43f5e; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">📅</div>
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 500;">Réservations</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; color: #ffffff;">{total_res}</div>
                <div style="color: #10b981; font-size: 0.78rem; font-weight: 600; display: flex; align-items: center; gap: 4px;">⏱️ Séjour moyen: {duree_moyenne} j</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">🪙</div>
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 500;">Chiffre d'affaires</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; color: #ffffff;">{ca_total:.2f} €</div>
                <div style="color: #10b981; font-size: 0.78rem; font-weight: 600; display: flex; align-items: center; gap: 4px;">🏷️ Panier moyen: {panier_moyen:.2f} €</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(168, 85, 247, 0.15); color: #a855f7; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">🛏️</div>
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 500;">Chambres dispo</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; color: #ffffff;">{stock_total}</div>
                <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 500; display: flex; align-items: center; gap: 4px;">🛏️ Stock en temps réel</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="background: rgba(16, 185, 129, 0.15); color: #10b981; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">📈</div>
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 500;">Taux d'occupation</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; color: #ffffff;">{taux_occupation}%</div>
                <div style="color: #10b981; font-size: 0.78rem; font-weight: 600; display: flex; align-items: center; gap: 4px;">↗ Capacité globale</div>
            </div>
        """, unsafe_allow_html=True)