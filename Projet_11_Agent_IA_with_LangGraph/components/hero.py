import streamlit as st

def render_hero():
    # Hero Banner principal avec Météo et Slogan
    st.markdown("""
        <div style="background: linear-gradient(rgba(11, 15, 25, 0.50), rgba(11, 15, 25, 0.88)), url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1400&q=80') center/cover;
                    border-radius: 16px; padding: 30px; margin-bottom: 20px; border: 1px solid #1f2c40; position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                <div>
                    <span style="background: rgba(255, 42, 117, 0.2); color: #ff2a75; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">ASSISTANT VIRTUEL</span>
                    <h1 style="color: #ffffff; font-size: 2rem; font-weight: 800; margin: 10px 0 6px 0;">
                        Bonjour et bienvenue à <span style="color: #ff2a75;">l’Hôtel Le Belvédère</span> !
                    </h1>
                    <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0; max-width: 620px; line-height: 1.5;">
                        Votre assistant virtuel est prêt à vous accompagner dans la gestion de vos réservations, chambres, services et bien plus encore.
                    </p>
                    <div style="font-family: 'Playfair Display', serif; font-style: italic; color: #ff2a75; font-size: 1.25rem; margin-top: 12px;">
                        L’excellence de votre séjour
                    </div>
                </div>
                <div class="weather-badge">
                    <span style="font-size: 1.4rem;">☀️</span>
                    <div>
                        <b style="color: #ffffff;">Meknès</b><br>
                        <span style="color: #94a3b8; font-size: 0.75rem;">22°C • Ciel dégagé</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Questions rapides (Chips)
    quick_questions = [
        ("📅 Disponibilités", "Est-ce qu'il reste une Suite Panoramic libre ?"),
        ("🛏️ Nos chambres", "Quelles sont les catégories de chambres disponibles ?"),
        ("🏷️ Tarifs & offres", "Combien coûte une chambre classique par nuit ?"),
        ("⭐ Nos services", "Quels sont les services proposés par l'hôtel ?")
    ]
    
    cols = st.columns(4)
    for i, (label, prompt) in enumerate(quick_questions):
        with cols[i]:
            if st.button(label, key=f"hero_chip_{i}", use_container_width=True):
                st.session_state["selected_question"] = prompt