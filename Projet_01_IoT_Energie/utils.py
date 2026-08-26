import matplotlib.pyplot as plt
import numpy as np

def afficher_etat_securite(temp, etat):
    """Affiche un badge visuel du statut de sécurité (Quête 1)."""
    couleurs = {
        "GEL_RISQUE": "🟦 Bleu (Risque de Gel)",
        "NOMINAL": "🟩 Vert (Fonctionnement Optimal)",
        "ALERTE_CHAUD": "🟧 Orange (Surchauffe Modérée)",
        "ARRET_URGENCE": "🟥 Rouge (Danger Impérieux)"
    }
    desc = couleurs.get(etat, "Inconnu")
    print("\n" + "═"*55)
    print(f"🌡️  CONTRÔLE SÉCURITÉ | Température : {temp}°C")
    print(f"📊 ÉTAT SYSTÈME      : [{etat}] ➔ {desc}")
    print("═"*55 + "\n")


def tracer_serie_temporelle(valeurs, temp_max=None, temp_moy=None):
    """Trace les relevés d'un capteur avec lignes Max et Moyenne (Quête 2)."""
    plt.figure(figsize=(8, 3.8))
    plt.plot(valeurs, marker='o', color='#1f77b4', linewidth=2, label='Relevés Capteur (°C)')
    
    if temp_moy is not None:
        plt.axhline(temp_moy, color='#ff7f0e', linestyle='--', linewidth=1.8, label=f'Moyenne ({temp_moy:.2f}°C)')
    if temp_max is not None:
        plt.axhline(temp_max, color='#d62728', linestyle=':', linewidth=2, label=f'Maximum ({temp_max}°C)')
        
    plt.title("📈 Série Temporelle des Relevés Solaire", fontsize=11, fontweight='bold')
    plt.xlabel("Index Temporel (Heure / Mesure)")
    plt.ylabel("Température (°C)")
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def tracer_nettoyage_signal(donnees_brutes, donnees_propres):
    """Compare le signal parasité et le signal filtré côte à côte (Quête 3)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))
    
    # Signal Brut
    ax1.plot(donnees_brutes, 'o--', color='#d62728', label='Données Brutes')
    ax1.set_title("⚠️ Signal Parasité (Bugs -999.0)", fontweight='bold')
    ax1.set_ylabel("Débit d'eau (L/min)")
    ax1.grid(True, alpha=0.5)
    ax1.legend()
    
    # Signal Propre
    ax2.plot(donnees_propres, 'o-', color='#2ca02c', label='Signal Nettoyé')
    ax2.set_title("✅ Signal Filtré (Valide)", fontweight='bold')
    ax2.set_ylabel("Débit d'eau (L/min)")
    ax2.grid(True, alpha=0.5)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()


def afficher_grille_max(matrice, temp_max):
    """Affiche la grille 2D et met en évidence la valeur maximale (Quête 4)."""
    mat = np.array(matrice)
    plt.figure(figsize=(5.5, 4))
    plt.imshow(mat, cmap='YlOrRd')
    plt.colorbar(label='Température (°C)')
    plt.title(f"🔥 Grille Capteurs (Max Détecté : {temp_max}°C)", fontweight='bold')
    
    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            val = mat[r, c]
            bold = 'bold' if val == temp_max else 'normal'
            txt = f"{val:.1f}°C★" if val == temp_max else f"{val:.1f}°C"
            plt.text(c, r, txt, ha='center', va='center', fontweight=bold,
                     color='white' if val > 50 else 'black')
            
    plt.tight_layout()
    plt.show()


def afficher_slicing_numpy(capteur_B, instant_t2, moyennes):
    """Affiche les extractions vectorielles issues du slicing NumPy (Quête 5)."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3.5))
    
    # Colonne Capteur B
    ax1.plot(capteur_B, 'o-', color='#9467bd', linewidth=2)
    ax1.set_title("Capteur B (`matrice[:, 1]`)", fontweight='bold')
    ax1.set_xlabel("Heures")
    ax1.set_ylabel("Température (°C)")
    ax1.grid(True, alpha=0.5)
    
    # Ligne t=2h
    ax2.plot(["Capteur A", "Capteur B", "Capteur C"], instant_t2, 's-', color='#ff7f0e', linewidth=2)
    ax2.set_title("Instant t=2h (`matrice[2, :]`)", fontweight='bold')
    ax2.set_ylabel("Température (°C)")
    ax2.grid(True, alpha=0.5)
    
    # Moyenne par capteur (axis=0)
    ax3.bar(["Capteur A", "Capteur B", "Capteur C"], moyennes, color='#17becf', alpha=0.85)
    ax3.set_title("Moyenne Temporelle (`axis=0`)", fontweight='bold')
    ax3.set_ylabel("Température Moyenne (°C)")
    ax3.grid(True, alpha=0.5)
    
    plt.tight_layout()
    plt.show()


def afficher_hotspots_2d(grille, coordonnees, seuil):
    """Affiche la carte thermique avec marqueurs de Hotspots (Quête 6)."""
    plt.figure(figsize=(6, 4.5))
    plt.imshow(grille, cmap='YlOrRd')
    plt.colorbar(label='Température (°C)')
    plt.title(f"⚠️ Carte des Hotspots (>= {seuil}°C)", fontweight='bold')
    
    for r in range(grille.shape[0]):
        for c in range(grille.shape[1]):
            val = grille[r, c]
            est_hotspot = (r, c) in coordonnees
            txt = f"{val:.1f}°C\n🔥" if est_hotspot else f"{val:.1f}°C"
            plt.text(c, r, txt, ha='center', va='center', 
                     fontweight='bold' if est_hotspot else 'normal',
                     color='white' if val > 60 else 'black')
            
    plt.tight_layout()
    plt.show()


def tracer_filtrage_1d(signal_brut, signal_lisse):
    """Trace la comparaison entre signal bruité et signal filtré (Quête 7)."""
    plt.figure(figsize=(8.5, 4))
    plt.plot(signal_brut, 'o--', color='#d62728', label='Signal Bruité (Brut)', alpha=0.7)
    
    # Ajustement de l'axe X pour les points lissés
    x_lisse = range(1, len(signal_brut) - 1)
    plt.plot(x_lisse, signal_lisse, 's-', color='#2ca02c', linewidth=2.5, label='Signal Lissé (Moyenne 3 pts)')
    
    plt.title("🎛️ Filtre Numérique : Élimination du Bruit Électrique", fontweight='bold')
    plt.xlabel("Échantillons")
    plt.ylabel("Température (°C)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def afficher_dashboard_iot(nom_zone, matrice, seuil_alerte=75.0):
    """Affiche un résumé console du système (Bilan Final)."""
    temp_moy = matrice.mean()
    temp_max = matrice.max()
    nb_alertes = (matrice >= seuil_alerte).sum()
    
    print("\n" + "═"*55)
    print(f"📊 MONITORING IOT EN TEMPS RÉEL | ZONE : {nom_zone}")
    print("═"*55)
    print(f"  • Température Moyenne  : {temp_moy:.2f} °C")
    print(f"  • Température Maximale : {temp_max:.2f} °C")
    print(f"  • Hotspots (>= {seuil_alerte}°C) : {nb_alertes} zone(s) critique(s)")
    print("═"*55 + "\n")