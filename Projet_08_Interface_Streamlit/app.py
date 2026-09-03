"""
==============================================================================
🎓 CURSUS STREAMLIT SMART GRID — SUPPORT DE COURS & EXERCICES EN BATCH
==============================================================================
Instructions d'exécution :
0. Installer streamlit sur votre terminal : uv add streamlit
1. Lancez ce fichier dans votre terminal en étant dans dossier du projet projet 08: streamlit run app.py
2. L'application s'ouvrira dans votre navigateur web.
3. Pour chaque niveau, lisez le cours rédigé en commentaire multi-lignes.
4. Complétez le code en remplaçant TOUS les '...' par la syntaxe exacte.
5. Sauvegardez le fichier (Ctrl+S) pour voir l'interface se mettre à jour.
==============================================================================
"""

import pandas as pd
import streamlit as st
from utilis import (
    get_kpi_metrics,
    init_db,
    insert_trame_telemetrie,
    load_parc_capteurs,
    load_telemetrie_filtree,
)

# Garantir que la base SQLite de démonstration existe
init_db()

# Menu de navigation latéral pour basculer entre les TP
st.sidebar.title("📚 Navigation du Cursus")
niveau = st.sidebar.radio(
    "Sélectionnez le niveau d'exercice :",
    [
        "Niveau 01 : Initialisation & DataFrames",
        "Niveau 02 : Sidebar & Filtres Dynamiques",
        "Niveau 03 : Disposition en Colonnes & KPIs",
        "Niveau 04 : Visualisations & Graphiques",
        "Niveau 05 : Structure par Onglets & Expander",
        "Niveau 06 : Formulaires & Injection SQL",
    ],
)


# ==============================================================================
# 🟢 NIVEAU 01 : INITIALISATION & DATAFRAMES
# ==============================================================================
if niveau == "Niveau 01 : Initialisation & DataFrames":
    """
    ============================================================================
    📖 COURS NIVEAU 01 : LES BASES DE STREAMLIT
    ----------------------------------------------------------------------------
    Streamlit transforme un script Python en interface web. Il re-exécute le 
    script du haut vers le bas à chaque modification ou interaction.

    FONCTIONS CLÉS À RÉVISER :
    1. st.set_page_config(page_title="...", layout="wide")
       - Définit le titre de l'onglet et la largeur de page (wide / centered).
       - Doit être appelée au tout début de l'application si elle est utilisée.
    2. st.title("Texte") / st.caption("Texte")
       - Affichent respectivement un titre principal (H1) et un texte discret.
    3. st.dataframe(df, use_container_width=True)
       - Rend un DataFrame Pandas sous forme de tableau HTML interactif
         (triable, redimensionnable, téléchargeable).
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 01 : Configurer la page et afficher le parc")

    # ÉTAPE 1 : Charger les capteurs via la fonction fournie dans utilis.py
    df_capteurs = load_parc_capteurs()

    # ÉTAPE 2 : Ajouter un titre principal à l'écran
    st....("⚡ Dashboard de Supervision Énergétique IoT")  # <--- Compléter avec le composant titre

    # ÉTAPE 3 : Ajouter une sous-description
    st.caption("Données extraites de la table 'capteurs'")

    # ÉTAPE 4 : Afficher le DataFrame de manière interactive
    st.subheader("📋 Liste des Équipements")
    st....(df_capteurs, use_container_width=True)  # <--- Compléter avec le composant dataframe


# ==============================================================================
# 🟢 NIVEAU 02 : SIDEBAR & FILTRES DYNAMIQUES
# ==============================================================================
elif niveau == "Niveau 02 : Sidebar & Filtres Dynamiques":
    """
    ============================================================================
    📖 COURS NIVEAU 02 : LA BARRE LATÉRALE ET LE FILTRAGE PANDAS
    ----------------------------------------------------------------------------
    Pour isoler les contrôles de l'affichage principal, Streamlit propose le 
    conteneur 'st.sidebar'. Tout composant préfixé par 'st.sidebar.' est déporté
    dans le panneau latéral coulissant à gauche.

    FONCTIONS CLÉS À RÉVISER :
    1. st.sidebar.header("Titre")
       - Crée un en-tête dans la barre latérale.
    2. st.sidebar.multiselect(label, options, default)
       - Propose une liste de choix multiples.
       - Retourne une liste Python contenant les valeurs cochées.
    3. df[df["colonne"].isin(liste_selection)]
       - Méthode Pandas filtrant les lignes dont la colonne appartient à la liste.
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 02 : Filtrer les trames par capteur")

    df_capteurs = load_parc_capteurs()
    liste_codes = df_capteurs["sensor_code"].tolist()

    # ÉTAPE 1 : Ajouter un en-tête dans la barre latérale
    st.sidebar....("🎛️ Filtres Utilisateur")  # <--- Ajouter le composant header de la sidebar

    # ÉTAPE 2 : Créer le menu à choix multiples dans la sidebar
    capteurs_choisis = st.sidebar....(  # <--- Ajouter le composant multiselect
        "Sélectionnez les capteurs :",
        options=liste_codes,
        default=liste_codes,
    )

    # ÉTAPE 3 : Transmettre la liste filtrée à la fonction de chargement SQL
    df_filtre = load_telemetrie_filtree(sensor_ids=...)  # <--- Passer la variable des choix

    st.write(f"📊 Volume de trames récupérées : **{len(df_filtre)}**")
    st.dataframe(df_filtre, use_container_width=True)


# ==============================================================================
# 🟢 NIVEAU 03 : DISPOSITION EN COLONNES & KPIS
# ==============================================================================
elif niveau == "Niveau 03 : Disposition en Colonnes & KPIs":
    """
    ============================================================================
    📖 COURS NIVEAU 03 : DESIGN EN COLONNES ET CARTES MÉTRIQUES
    ----------------------------------------------------------------------------
    Les Dashboards nécessitent la présentation de chiffres clés (KPI) disposés 
    horizontalement sur une même ligne.

    FONCTIONS CLÉS À RÉVISER :
    1. col1, col2, col3 = st.columns(3)
       - Divise l'espace horizontal en 3 colonnes de largeur égale.
    2. col1.metric(label, value, delta=None)
       - Affiche une carte KPI structurée avec un titre, une valeur principale 
         et un indicateur de variation (delta).
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 03 : Construire le bandeau de KPIs")

    df_filtre = load_telemetrie_filtree()
    kpis = get_kpi_metrics(df_filtre)

    # ÉTAPE 1 : Diviser la page en 4 colonnes
    c1, c2, c3, c4 = st....(4)  # <--- Déclarer la division en 4 colonnes

    # ÉTAPE 2 : Remplir la première métrique avec la puissance totale
    c1....(  # <--- Utiliser le composant metric
        label="Énergie Totale",
        value=f"{kpis['puissance_totale_kw']} kWh",
        delta="Cumul",
    )

    # ÉTAPE 3 : Remplir les colonnes suivantes avec le dictionnaire 'kpis'
    c2.metric(
        label="Puissance Moyenne",
        value=f"{kpis['puissance_moyenne_w']} W",
    )
    c3.metric(
        label="Pic Maximal",
        value=f"{kpis['pic_max_w']} W",
    )
    c4.metric(
        label="Nombre de Mesures",
        value=f"{kpis['...']}",  # <--- Clé d'accès du dictionnaire (nb_mesures)
    )


# ==============================================================================
# 🟢 NIVEAU 04 : VISUALISATIONS & GRAPHIQUES
# ==============================================================================
elif niveau == "Niveau 04 : Visualisations & Graphiques":
    """
    ============================================================================
    📖 COURS NIVEAU 04 : SERIÉS TEMPORELLES ET DIAGRAMMES
    ----------------------------------------------------------------------------
    Streamlit intègre des composants graphiques simples basés sur Altair.

    FONCTIONS ET PANDAS À RÉVISER :
    1. df.pivot_table(index="...", columns="...", values="...")
       - Restructure un DataFrame plat en tableau croisé pour tracer une courbe 
         par capteur au fil du temps.
    2. st.line_chart(df)
       - Génère automatiquement un graphique temporel en lignes.
    3. st.bar_chart(df, x="...", y="...")
       - Génère un histogramme ou diagramme en barres.
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 04 : Graphiques Temporels et Agrégations")

    df_filtre = load_telemetrie_filtree()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Évolution de la Puissance (W)**")
        # ÉTAPE 1 : Pivoter les données pour la série temporelle
        df_pivot = df_filtre....(  # <--- Appliquer la méthode pivot_table de Pandas
            index="timestamp", columns="sensor_id", values="puissance_w"
        )
        # ÉTAPE 2 : Tracer le graphique en lignes
        st....(df_pivot)  # <--- Composant line_chart

    with col_right:
        st.markdown("**Puissance Moyenne par Capteur (W)**")
        # ÉTAPE 3 : Aggréger la moyenne par capteur
        df_agreg = (
            df_filtre.groupby("sensor_id")["puissance_w"]
            ....()  # <--- Calculer la moyenne (mean)
            .reset_index()
        )
        # ÉTAPE 4 : Tracer le diagramme en barres
        st....(  # <--- Composant bar_chart
            df_agreg, x="sensor_id", y="puissance_w"
        )


# ==============================================================================
# 🟢 NIVEAU 05 : STRUCTURE PAR ONGLETS & EXPANDER
# ==============================================================================
elif niveau == "Niveau 05 : Structure par Onglets & Expander":
    """
    ============================================================================
    📖 COURS NIVEAU 05 : ERGONOMIE DU DASHBOARD (TABS & EXPANDER)
    ----------------------------------------------------------------------------
    Pour éviter le défilement vertical infini, Streamlit permet d'organiser le 
    contenu en onglets ou dans des modules masqués/déroulants.

    FONCTIONS CLÉS À RÉVISER :
    1. tab1, tab2 = st.tabs(["Nom Tab 1", "Nom Tab 2"])
       - Divise la vue principale en onglets cliquables.
    2. with tab1:
       - Bloc de contexte dans lequel placer les éléments du premier onglet.
    3. with st.expander("Titre"):
       - Conteneur repliable idéal pour afficher de la documentation ou du SQL.
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 05 : Structurer la page en Onglets")

    df_filtre = load_telemetrie_filtree()

    # ÉTAPE 1 : Créer deux onglets
    t_data, t_info = st....(  # <--- Déclaration des onglets (tabs)
        ["📄 Données Brutes", "ℹ️ Informations"]
    )

    # ÉTAPE 2 : Remplir le premier onglet
    with t_data:
        st.dataframe(df_filtre, use_container_width=True)

    # ÉTAPE 3 : Remplir le second onglet
    with ...:  # <--- Indiquer la variable de l'onglet 2 (t_info)
        # ÉTAPE 4 : Ajouter un bloc déroulant
        with st....("🔍 Voir le schéma de la base"):  # <--- Composant expander
            st.code("SELECT * FROM telemetrie_energie;", language="sql")


# ==============================================================================
# 🟢 NIVEAU 06 : FORMULAIRES & INJECTION SQL
# ==============================================================================
elif niveau == "Niveau 06 : Formulaires & Injection SQL":
    """
    ============================================================================
    📖 COURS NIVEAU 06 : INTERACTION AVEC LA BASE (ST.FORM & ST.RERUN)
    ----------------------------------------------------------------------------
    Par défaut, Streamlit recharge la page dès qu'un champ est modifié. Dans un 
    formulaire de saisie, cela rafraîchirait la page avant la fin de la frappe.
    On utilise 'st.form' pour bloquer l'exécution jusqu'au clic sur le bouton.

    FONCTIONS CLÉS À RÉVISER :
    1. with st.form("form_id"):
       - Bloque l'interaction dynamique jusqu'à soumission.
    2. btn = st.form_submit_button("Texte")
       - Le seul bouton autorisé à valider un 'st.form'.
    3. st.cache_data.clear()
       - Invalide le cache mémoire de Streamlit pour forcer la relecture SQLite.
    4. st.rerun()
       - Relance instantanément l'exécution du script Python.
    ============================================================================
    """
    st.markdown("### 🎯 TP Niveau 06 : Ajouter une mesure dans la base SQLite")

    df_capteurs = load_parc_capteurs()
    liste_codes = df_capteurs["sensor_code"].tolist()

    # ÉTAPE 1 : Déclarer le conteneur de formulaire
    with st....("form_saisie", clear_on_submit=True):  # <--- Composant form
        sensor = st.selectbox("Capteur :", options=liste_codes)
        puissance = st.number_input("Puissance (W) :", value=1200.0)
        timestamp = st.text_input("Date ISO :", value="2026-08-31 14:00:00")
        tension = st.number_input("Tension (V) :", value=230.0)

        # ÉTAPE 2 : Ajouter le bouton de soumission spécifique
        btn_submit = st....(  # <--- Composant form_submit_button
            "🚀 Envoyer la Trame"
        )

    # ÉTAPE 3 : Traitement lors de la validation
    if btn_submit:
        insert_trame_telemetrie(
            sensor_id=sensor,
            timestamp=timestamp,
            puissance_w=puissance,
            tension_v=tension,
        )
        st.success("Trame insérée avec succès dans SQLite !")

        # ÉTAPE 4 : Invalider le cache et rafraîchir l'interface
        st.cache_data.clear()
        st....()  # <--- Relancer le script (rerun)