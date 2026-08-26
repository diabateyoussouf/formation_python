import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from IPython.display import HTML, display


def afficher_bienvenue_centrale():
    """Affiche une bannière d'accueil industrielle immersive."""
    html_code = """
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 25px; border-radius: 15px; color: white; font-family: Arial, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center;">
        <h1 style="margin: 0; font-size: 28px; color: #f1c40f;">☀️ SUPERVISION CENTRALE SOLAIRE IoT v5.0</h1>
        <p style="font-size: 16px; margin-top: 10px; color: #ecf0f1;">Architecture Orientée Objet & Traitement Telemetrique en Temps Réel</p>
        <div style="display: flex; justify-content: space-around; margin-top: 20px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <div>⚡ <b>Capacité Cible :</b> 500 kWp</div>
            <div>📡 <b>Protocole Capteurs :</b> MQTT / IoT</div>
            <div>📊 <b>Moteur d'Audit :</b> Python POO + Pandas</div>
        </div>
    </div>
    """
    display(HTML(html_code))


def afficher_etat_capteur(capteur):
    """Affiche une carte télémétrique visuelle pour un CapteurIoT."""
    moyenne = capteur.obtenir_moyenne()
    historique_str = (
        " -> ".join([f"{v}{capteur.unite}" for v in capteur.historique_mesures])
        if capteur.historique_mesures
        else "Aucune donnée"
    )

    fig, ax = plt.subplots(figsize=(7, 2.5), facecolor="#f8f9fa")
    if capteur.historique_mesures:
        ax.plot(
            range(1, len(capteur.historique_mesures) + 1),
            capteur.historique_mesures,
            marker="o",
            color="#27ae60",
            linewidth=2,
            markersize=8,
        )
        ax.axhline(
            moyenne,
            color="#e74c3c",
            linestyle="--",
            label=f"Moyenne: {moyenne:.1f} {capteur.unite}",
        )
    ax.set_title(
        f"Télémétrie Capteur : {capteur.id_capteur} ({capteur.type_mesure})",
        fontsize=12,
        fontweight="bold",
        color="#2c3e50",
    )
    ax.set_xlabel("Relevés", fontsize=10)
    ax.set_ylabel(f"Valeur ({capteur.unite})", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.show()

    html_card = f"""
    <div style="border-left: 5px solid #27ae60; background-color: #ffffff; padding: 12px 20px; margin-top: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <b style="color: #2c3e50;">ID Capteur :</b> {capteur.id_capteur} | 
        <b style="color: #2c3e50;">Historique enregistré :</b> [{historique_str}] | 
        <b style="color: #27ae60;">Moyenne :</b> {moyenne:.2f} {capteur.unite}
    </div>
    """
    display(HTML(html_card))


def afficher_fiche_panneau(panneau, p_elec_kw, eta_stc_pct):
    """Affiche la fiche technique dynamique d'un PanneauSolaire."""
    degradation = panneau.obtenir_degradation()

    html_code = f"""
    <div style="background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); font-family: Arial, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f1c40f; padding-bottom: 10px; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #2c3e50;">☀️ Fiche Module Photovoltaïque : <span style="color: #d35400;">{panneau.id_module}</span></h3>
            <span style="background: #e8f8f5; color: #16a085; padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 13px;">Statut : Actif</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center;">
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
                <div style="font-size: 12px; color: #7f8c8d;">Surface</div>
                <div style="font-size: 18px; font-weight: bold; color: #2c3e50;">{panneau.surface_m2} m²</div>
            </div>
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
                <div style="font-size: 12px; color: #7f8c8d;">Dégradation cumulée</div>
                <div style="font-size: 18px; font-weight: bold; color: #c0392b;">{degradation:.1f} %</div>
            </div>
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
                <div style="font-size: 12px; color: #7f8c8d;">Puissance Produite</div>
                <div style="font-size: 18px; font-weight: bold; color: #2980b9;">{p_elec_kw:.2f} kW</div>
            </div>
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
                <div style="font-size: 12px; color: #7f8c8d;">Rendement STC</div>
                <div style="font-size: 18px; font-weight: bold; color: #27ae60;">{eta_stc_pct:.2f} %</div>
            </div>
        </div>
    </div>
    """
    display(HTML(html_code))


def afficher_schema_centrale(centrale):
    """Affiche la structure hiérarchique de la centrale solaire."""
    nb_modules = len(centrale.modules)
    p_totale = centrale.puissance_totale_nominale_kw()

    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor="#f4f6f7")
    ax.axis("off")

    # Dessin de la Centrale avec FancyBboxPatch (supporte les coins arrondis)
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0.1, 0.4),
            0.3,
            0.4,
            color="#2c3e50",
            ec="#1a252f",
            lw=2,
            boxstyle="round,pad=0.03",
        )
    )
    ax.text(
        0.25,
        0.6,
        f"CENTRALE\n{centrale.nom_centrale}\n({centrale.localisation})",
        color="white",
        weight="bold",
        fontsize=10,
        ha="center",
        va="center",
    )

    # Ligne de connexion
    ax.plot([0.4, 0.6], [0.6, 0.6], color="#7f8c8d", lw=3, linestyle="--")

    # Dessin des modules agrégés
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0.6, 0.3),
            0.35,
            0.6,
            color="#f39c12",
            ec="#d35400",
            lw=2,
            boxstyle="round,pad=0.03",
        )
    )
    ax.text(
        0.775,
        0.6,
        f"PARC PHOTOVOLTAÏQUE\n\n📦 Modules connectés : {nb_modules}\n⚡ Puissance Crête : {p_totale} kW",
        color="white",
        weight="bold",
        fontsize=9,
        ha="center",
        va="center",
    )

    plt.title(
        f" Architecture Logique : {centrale.nom_centrale}",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    plt.show()


def tracer_dashboard_poo(centrale, rapport_audit):
    """Génère le dashboard final de performance de la centrale."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor="#ffffff")

    # Graphique 1 : Indicateurs Clés (KPIs)
    kpis = ["Énergie (kWh)", "Puissance Moy. (kW)"]
    valeurs = [
        rapport_audit.get("energie_totale_kwh", 0),
        rapport_audit.get("puissance_moyenne_kw", 0),
    ]
    bars = ax1.bar(
        kpis, valeurs, color=["#f39c12", "#2980b9"], width=0.5, edgecolor="#333"
    )
    ax1.set_title(" Bilan Énergétique de l'Audit", fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax1.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Graphique 2 : Composition de la Centrale
    labels = [m.id_module for m in centrale.modules]
    puissances = [m.puissance_nominale_kw for m in centrale.modules]

    if puissances:
        ax2.pie(
            puissances,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=["#27ae60", "#2980b9", "#8e44ad", "#e67e22"],
        )
        ax2.set_title(
            " Répartition de la Puissance Nominale", fontweight="bold"
        )
    else:
        ax2.text(
            0.5,
            0.5,
            "Aucun module installé",
            ha="center",
            va="center",
            fontsize=12,
        )

    plt.tight_layout()
    plt.show()
