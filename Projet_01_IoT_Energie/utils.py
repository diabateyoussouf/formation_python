import matplotlib.pyplot as plt
import numpy as np


# --- FONCTIONS DE BASE IoT (Niveaux 1 à 7 de base) ---
def afficher_etat_securite(temp, etat):
    """Affiche un badge visuel du statut de sécurité."""
    couleurs = {
        "GEL_RISQUE": "🟦 Bleu (Risque de Gel)",
        "NOMINAL": "🟩 Vert (Fonctionnement Optimal)",
        "ALERTE_CHAUD": "🟧 Orange (Surchauffe Modérée)",
        "ARRET_URGENCE": "🟥 Rouge (Danger Impérieux)",
    }
    desc = couleurs.get(etat, "Inconnu")
    print("\n" + "═" * 55)
    print(f"🌡️  CONTRÔLE SÉCURITÉ | Température : {temp}°C")
    print(f"📊 ÉTAT SYSTÈME      : [{etat}] ➔ {desc}")
    print("═" * 55 + "\n")


def tracer_serie_temporelle(valeurs, temp_max=None, temp_moy=None):
    """Trace les relevés d'un capteur avec lignes Max et Moyenne."""
    plt.figure(figsize=(8, 3.8))
    plt.plot(
        valeurs,
        marker="o",
        color="#1f77b4",
        linewidth=2,
        label="Relevés Capteur (°C)",
    )

    if temp_moy is not None:
        plt.axhline(
            temp_moy,
            color="#ff7f0e",
            linestyle="--",
            linewidth=1.8,
            label=f"Moyenne ({temp_moy:.2f}°C)",
        )
    if temp_max is not None:
        plt.axhline(
            temp_max,
            color="#d62728",
            linestyle=":",
            linewidth=2,
            label=f"Maximum ({temp_max}°C)",
        )

    plt.title(
        "📈 Série Temporelle des Relevés Solaire",
        fontsize=11,
        fontweight="bold",
    )
    plt.xlabel("Index Temporel (Heure / Mesure)")
    plt.ylabel("Température (°C)")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def tracer_nettoyage_signal(donnees_brutes, donnees_propres):
    """Compare le signal parasité et le signal filtré côte à côte."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))

    ax1.plot(donnees_brutes, "o--", color="#d62728", label="Données Brutes")
    ax1.set_title("⚠️ Signal Parasité (Bugs -999.0)", fontweight="bold")
    ax1.set_ylabel("Débit d'eau (L/min)")
    ax1.grid(True, alpha=0.5)
    ax1.legend()

    ax2.plot(donnees_propres, "o-", color="#2ca02c", label="Signal Nettoyé")
    ax2.set_title("✅ Signal Filtré (Valide)", fontweight="bold")
    ax2.set_ylabel("Débit d'eau (L/min)")
    ax2.grid(True, alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.show()


def afficher_grille_max(matrice, temp_max):
    """Affiche la grille 2D et met en évidence la valeur maximale."""
    mat = np.array(matrice)
    plt.figure(figsize=(5.5, 4))
    plt.imshow(mat, cmap="YlOrRd")
    plt.colorbar(label="Température (°C)")
    plt.title(
        f"🔥 Grille Capteurs (Max Détecté : {temp_max}°C)", fontweight="bold"
    )

    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            val = mat[r, c]
            bold = "bold" if val == temp_max else "normal"
            txt = f"{val:.1f}°C★" if val == temp_max else f"{val:.1f}°C"
            plt.text(
                c,
                r,
                txt,
                ha="center",
                va="center",
                fontweight=bold,
                color="white" if val > 50 else "black",
            )

    plt.tight_layout()
    plt.show()


def afficher_slicing_numpy(capteur_B, instant_t2, moyennes):
    """Affiche les extractions vectorielles issues du slicing NumPy."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3.5))

    ax1.plot(capteur_B, "o-", color="#9467bd", linewidth=2)
    ax1.set_title("Capteur B (`matrice[:, 1]`)", fontweight="bold")
    ax1.set_xlabel("Heures")
    ax1.set_ylabel("Température (°C)")
    ax1.grid(True, alpha=0.5)

    ax2.plot(
        ["Capteur A", "Capteur B", "Capteur C"],
        instant_t2,
        "s-",
        color="#ff7f0e",
        linewidth=2,
    )
    ax2.set_title("Instant t=2h (`matrice[2, :]`)", fontweight="bold")
    ax2.set_ylabel("Température (°C)")
    ax2.grid(True, alpha=0.5)

    ax3.bar(
        ["Capteur A", "Capteur B", "Capteur C"],
        moyennes,
        color="#17becf",
        alpha=0.85,
    )
    ax3.set_title("Moyenne Temporelle (`axis=0`)", fontweight="bold")
    ax3.set_ylabel("Température Moyenne (°C)")
    ax3.grid(True, alpha=0.5)

    plt.tight_layout()
    plt.show()


def afficher_hotspots_2d(grille, coordonnees, seuil):
    """Affiche la carte thermique avec marqueurs de Hotspots."""
    plt.figure(figsize=(6, 4.5))
    plt.imshow(grille, cmap="YlOrRd")
    plt.colorbar(label="Température (°C)")
    plt.title(f"⚠️ Carte des Hotspots (>= {seuil}°C)", fontweight="bold")

    for r in range(grille.shape[0]):
        for c in range(grille.shape[1]):
            val = grille[r, c]
            est_hotspot = (r, c) in coordonnees
            txt = f"{val:.1f}°C\n🔥" if est_hotspot else f"{val:.1f}°C"
            plt.text(
                c,
                r,
                txt,
                ha="center",
                va="center",
                fontweight="bold" if est_hotspot else "normal",
                color="white" if val > 60 else "black",
            )

    plt.tight_layout()
    plt.show()


def tracer_filtrage_1d(signal_brut, signal_lisse):
    """Trace la comparaison entre signal bruité et signal filtré."""
    plt.figure(figsize=(8.5, 4))
    plt.plot(
        signal_brut,
        "o--",
        color="#d62728",
        label="Signal Bruité (Brut)",
        alpha=0.7,
    )

    x_lisse = range(1, len(signal_brut) - 1)
    plt.plot(
        x_lisse,
        signal_lisse,
        "s-",
        color="#2ca02c",
        linewidth=2.5,
        label="Signal Lissé (Moyenne 3 pts)",
    )

    plt.title(
        "🎛️ Filtre Numérique : Élimination du Bruit Électrique",
        fontweight="bold",
    )
    plt.xlabel("Échantillons")
    plt.ylabel("Température (°C)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def afficher_dashboard_iot(nom_zone, matrice, seuil_alerte=75.0):
    """Affiche un résumé console du système."""
    temp_moy = matrice.mean()
    temp_max = matrice.max()
    nb_alertes = (matrice >= seuil_alerte).sum()

    print("\n" + "═" * 55)
    print(f"📊 MONITORING IOT EN TEMPS RÉEL | ZONE : {nom_zone}")
    print("═" * 55)
    print(f"  • Température Moyenne  : {temp_moy:.2f} °C")
    print(f"  • Température Maximale : {temp_max:.2f} °C")
    print(f"  • Hotspots (>= {seuil_alerte}°C) : {nb_alertes} zone(s) critique(s)")
    print("═" * 55 + "\n")


# --- FONCTIONS MATHÉMATIQUES & COURBES (Niveaux 01 à 10) ---
def tracer_signal_ac(t, v):
    """Trace la tension alternative 50Hz (Niveau 01)."""
    plt.figure(figsize=(8, 3))
    plt.plot(
        t * 1000,
        v,
        color="tab:blue",
        label="$v(t) = 325.4 \\sin(2\\pi \\cdot 50 t)$",
    )
    plt.title("Niveau 01 — Tension Alternative du Réseau (50 Hz)")
    plt.xlabel("Temps (ms)")
    plt.ylabel("Tension (V)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_rendement_pv(T, eta, T_opt):
    """Trace la courbe de rendement photovoltaïque (Niveau 02)."""
    plt.figure(figsize=(8, 3))
    plt.plot(T, eta, color="tab:orange", label="$\\eta(T) = -0.005(T-25)^2 + 22$")
    plt.axvline(
        T_opt, color="red", linestyle=":", label=f"Temp. Optimale ({T_opt}°C)"
    )
    plt.title("Niveau 02 — Rendement Photovoltaïque vs Température")
    plt.xlabel("Température (°C)")
    plt.ylabel("Rendement (%)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_refroidissement(temps, temp_reservoir, Tamb):
    """Trace le refroidissement thermique exponentiel (Niveau 03)."""
    plt.figure(figsize=(8, 3))
    plt.plot(
        temps,
        temp_reservoir,
        color="tab:red",
        label="$T(t) = 20 + 70 e^{-0.05 t}$",
    )
    plt.axhline(
        Tamb,
        color="gray",
        linestyle="--",
        label=f"Temp. Ambiante ({Tamb}°C)",
    )
    plt.title("Niveau 03 — Refroidissement du Fluide Caloporteur")
    plt.xlabel("Temps (minutes)")
    plt.ylabel("Température (°C)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_harmoniques(t_h, fondamental, harmonique3, signal_somme):
    """Trace la superposition du fondamental et de l'harmonique 3 (Niveau 04)."""
    plt.figure(figsize=(8, 3))
    plt.plot(
        t_h * 1000, fondamental, "--", label="Fondamental (50 Hz)", alpha=0.7
    )
    plt.plot(
        t_h * 1000, harmonique3, ":", label="Harmonique 3 (150 Hz)", alpha=0.7
    )
    plt.plot(
        t_h * 1000,
        signal_somme,
        color="purple",
        label="Signal Total Perturbé",
        lw=2,
    )
    plt.title("Niveau 04 — Superposition d'Ondes et Perturbations")
    plt.xlabel("Temps (ms)")
    plt.ylabel("Amplitude")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_systeme_lineaire(x_vals, y1, y2, x_sol, y_sol):
    """Trace l'intersection de deux droites de charge (Niveau 05)."""
    plt.figure(figsize=(8, 3))
    plt.plot(x_vals, y1, label="$2x + y = 8$")
    plt.plot(x_vals, y2, label="$-x + 3y = 10$")
    plt.plot(
        x_sol,
        y_sol,
        "ro",
        markersize=8,
        label=f"Intersection ({x_sol:.1f}, {y_sol:.1f})",
    )
    plt.title("Niveau 05 — Résolution de Systèmes Linéaires")
    plt.xlabel("Courant x (A)")
    plt.ylabel("Tension y (V)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_derivation(t_grad, T_grad, pente_thermique):
    """Trace la fonction et sa dérivée première (Niveau 06)."""
    fig, ax1 = plt.subplots(figsize=(8, 3))
    ax1.set_xlabel("Temps (s)")
    ax1.set_ylabel("Température (°C)", color="tab:red")
    ax1.plot(t_grad, T_grad, color="tab:red", label="Température $T(t)$")
    ax1.tick_params(axis="y", labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Vitesse de chauffe (°C/s)", color="tab:blue")
    ax2.plot(
        t_grad, pente_thermique, "--", color="tab:blue", label="Dérivée $dT/dt$"
    )
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    plt.title("Niveau 06 — Signal Temporel et sa Dérivée Première")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()


def tracer_integration_energie(heures, puissance, energie_totale):
    """Trace la puissance et l'aire d'énergie intégrée (Niveau 07)."""
    plt.figure(figsize=(8, 3))
    plt.plot(
        heures, puissance, color="tab:orange", lw=2, label="Puissance $P(t)$ (W)"
    )
    plt.fill_between(
        heures,
        puissance,
        color="tab:orange",
        alpha=0.3,
        label=f"Énergie Cumulée = {energie_totale:.0f} Wh",
    )
    plt.title("Niveau 07 — Intégration Numérique (Aire sous la Courbe)")
    plt.xlabel("Temps (Heures)")
    plt.ylabel("Puissance (W)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_saturation_sigmoide(x_sig, sigmoide):
    """Trace la courbe de saturation sigmoïdale (Niveau 08)."""
    plt.figure(figsize=(8, 3))
    plt.plot(
        x_sig,
        sigmoide,
        color="tab:green",
        lw=2.5,
        label="$\\sigma(x) = \\frac{1}{1 + e^{-x}}$",
    )
    plt.axhline(1.0, color="gray", linestyle=":", label="Asymptote Supérieure (1.0)")
    plt.axhline(
        0.5,
        color="orange",
        linestyle="--",
        alpha=0.6,
        label="Point d'Inflexion (0.5)",
    )
    plt.title("Niveau 08 — Courbe de Saturation Sigmoïdale")
    plt.xlabel("Signal de Commande x")
    plt.ylabel("Ouverture Vanne (%)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_bruit_gaussien(mesures_simulees, x_gauss, pdf):
    """Trace l'histogramme empirique et la loi normale gaussienne (Niveau 09)."""
    plt.figure(figsize=(8, 3))
    plt.hist(
        mesures_simulees,
        bins=40,
        density=True,
        alpha=0.4,
        color="tab:blue",
        label="Mesures Réelles Simulées",
    )
    plt.plot(
        x_gauss,
        pdf,
        color="tab:red",
        lw=2,
        label="Modèle Gaussien $\\mathcal{N}(50, 2^2)$",
    )
    plt.title("Niveau 09 — Distribution Numérique du Bruit Capteur")
    plt.xlabel("Température Mesurée (°C)")
    plt.ylabel("Densité de Probabilité")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def tracer_carte_thermique_2d(X, Y, Z):
    """Trace la carte de contours 2D (Niveau 10)."""
    plt.figure(figsize=(7, 4))
    contour = plt.contourf(X, Y, Z, levels=25, cmap="viridis")
    plt.colorbar(contour, label="Température Normalisée Z")
    plt.title("Niveau 10 — Carte Thermique Bidimensionnelle $Z = \\sin(X) \\cos(Y)$")
    plt.xlabel("Axe Spatial X (m)")
    plt.ylabel("Axe Spatial Y (m)")
    plt.tight_layout()
    plt.show()