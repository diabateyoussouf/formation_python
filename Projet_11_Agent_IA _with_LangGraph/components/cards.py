import streamlit as st

def render_cards():
    """Rend la grille de cartes interactives (6 catégories) avec le design Glassmorphism."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    cards_data = [
        {
            "icon": "📅", 
            "title": "Disponibilités", 
            "desc": "Vérifiez les chambres libres pour vos dates de séjour.", 
            "prompt": "Est-ce qu'il y a des chambres disponibles ce week-end ?"
        },
        {
            "icon": "🛏️", 
            "title": "Nos Chambres", 
            "desc": "Découvrez le catalogue, nos suites et équipements.", 
            "prompt": "Quels sont les équipements des chambres ?"
        },
        {
            "icon": "🏷️", 
            "title": "Tarifs & Offres", 
            "desc": "Consultez nos tarifs par saison et formules.", 
            "prompt": "Quels sont les tarifs des chambres ?"
        },
        {
            "icon": "🍴", 
            "title": "Services & Spa", 
            "desc": "Restaurant, piscine, Wi-Fi gratuit, parking et spa.", 
            "prompt": "Les animaux sont-ils autorisés et le wifi est-il gratuit ?"
        },
        {
            "icon": "📍", 
            "title": "Accès & Localisation", 
            "desc": "Trouvez comment nous rejoindre facilement à Meknès.", 
            "prompt": "Où se trouve l'hôtel et comment s'y rendre ?"
        },
        {
            "icon": "❓", 
            "title": "Informations Pratiques", 
            "desc": "Horaires de check-in/out, petit-déjeuner et règles.", 
            "prompt": "À quelle heure démarre le check-in ?"
        }
    ]

    col_a, col_b, col_c = st.columns(3)
    cols = [col_a, col_b, col_c]

    for idx, card in enumerate(cards_data):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="feature-card" style="margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-size: 1.6rem;">{card['icon']}</span>
                        <span style="background: rgba(255, 42, 117, 0.1); color: #ff2a75; border-radius: 8px; padding: 2px 8px; font-size: 0.7rem; font-weight: 600;">Question IA</span>
                    </div>
                    <h4 style="color: #ffffff; margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700;">{card['title']}</h4>
                    <p style="color: #94a3b8; font-size: 0.78rem; margin: 0 0 12px 0; line-height: 1.4;">{card['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Interroger : {card['title']} ➔", key=f"card_btn_{idx}", use_container_width=True):
                st.session_state["selected_question"] = card["prompt"]
                st.rerun()