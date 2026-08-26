import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def tracer_masquage_numpy(matrice_u, masque):
    """Affiche la carte des tensions et surligne les surtensions détectées (Quête 1)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Carte des valeurs
    cax1 = ax1.imshow(matrice_u, cmap='YlOrRd')
    fig.colorbar(cax1, ax=ax1, label='Tension (V)')
    ax1.set_title("⚡ Carte des Tensions (NumPy 2D)", fontweight='bold')
    for r in range(matrice_u.shape[0]):
        for c in range(matrice_u.shape[1]):
            ax1.text(c, r, f"{matrice_u[r, c]:.1f}V", ha='center', va='center', fontweight='bold')

    # Carte du masque booléen
    cax2 = ax2.imshow(masque, cmap='Blues')
    fig.colorbar(cax2, ax=ax2, label='Masque (> 235V)')
    ax2.set_title("🚨 Masque de Surtension (True/False)", fontweight='bold')
    for r in range(masque.shape[0]):
        for c in range(masque.shape[1]):
            txt = "SURTENSION" if masque[r, c] else "OK"
            ax2.text(c, r, txt, ha='center', va='center', color='red' if masque[r, c] else 'black', fontweight='bold')
            
    plt.tight_layout()
    plt.show()


def tracer_nettoyage_complet(df_brut, df_propre):
    """Compare le dataset altéré et le dataset réparé (Quête 2)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    
    # Avant nettoyage
    ax1.plot(df_brut['horodateur'], df_brut['tension_v'], 'ro--', label='Tension (avec NaN & Doublons)')
    ax1.set_title(f"⚠️ Données Brutes ({len(df_brut)} lignes)", fontweight='bold')
    ax1.set_ylabel("Tension (V)")
    ax1.tick_params(axis='x', rotation=30)
    ax1.grid(True, alpha=0.4)
    ax1.legend()
    
    # Après nettoyage
    ax2.plot(df_propre['horodateur'], df_propre['tension_v'], 'go-', label='Tension Nettoyée (ffill)')
    ax2.plot(df_propre['horodateur'], df_propre['puissance_kw'], 'bs-', label='Puissance (kW)')
    ax2.set_title(f"✅ Données Prétraitées ({len(df_propre)} lignes)", fontweight='bold')
    ax2.set_ylabel("Valeurs")
    ax2.tick_params(axis='x', rotation=30)
    ax2.grid(True, alpha=0.4)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()


def tracer_kpi_groupby(df_bilan):
    """Affiche un barplot comparatif des performances par site (Quête 3)."""
    fig, ax1 = plt.subplots(figsize=(8.5, 4))
    
    x = np.arange(len(df_bilan))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, df_bilan['puissance_totale_kw'], width, label='Puissance Totale (kW)', color='#1f77b4')
    ax1.set_ylabel('Puissance Totale (kW)', color='#1f77b4')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_bilan['site'])
    
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, df_bilan['rendement_moyen_pct'], width, label='Rendement Moy. (%)', color='#2ca02c')
    ax2.set_ylabel('Rendement Moyen (%)', color='#2ca02c')
    ax2.set_ylim(0, 100)
    
    plt.title("📊 Bilan Consolidé par Site (`.groupby()`)", fontweight='bold')
    plt.tight_layout()
    plt.show()


def tracer_dashboard_matplotlib_complet(df):
    """Masterclass Matplotlib : Génère un dashboard multi-panneaux (Quête 4)."""
    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 2)
    
    # Panel 1 : Évolution temporelle
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(df['horodateur'], df['puissance_kw'], color='#d62728', marker='o', linewidth=2, label='Puissance (kW)')
    ax1.set_title("📈 Chronogramme de Puissance du Microgrid", fontweight='bold')
    ax1.set_ylabel("Puissance (kW)")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()
    
    # Panel 2 : Histogramme de distribution
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(df['tension_v'], bins=5, color='#9467bd', edgecolor='black', alpha=0.7)
    ax2.set_title("📊 Distribution des Tensions (V)", fontweight='bold')
    ax2.set_xlabel("Tension (V)")
    ax2.set_ylabel("Fréquence")
    ax2.grid(True, alpha=0.4)
    
    # Panel 3 : Nuage de points Tension vs Courant
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.scatter(df['tension_v'], df['courant_a'], color='#17becf', s=80, edgecolors='black')
    ax3.set_title("🔬 Corrélation Tension vs Courant", fontweight='bold')
    ax3.set_xlabel("Tension (V)")
    ax3.set_ylabel("Courant (A)")
    ax3.grid(True, alpha=0.4)
    
    plt.tight_layout()
    plt.show()


def afficher_bilan_grand_projet(df_final, kpi_site):
    """Affiche le rapport de synthèse de fin de projet (Quête 5)."""
    print("\n" + "═"*60)
    print("🏆 AUDIT DATA ENERGY COMPLET : RAPPORT DE PRÉTRAITEMENT")
    print("═"*60)
    print(f"  • Volume d'échantillons traités : {len(df_final)} enregistrements")
    print(f"  • Puissance Totale Produite     : {df_final['puissance_kw'].sum():.2f} kW")
    print(f"  • Tension Moyenne du Réseau    : {df_final['tension_v'].mean():.2f} V")
    print("─"*60)
    print("  • Performance consolidée par Site :")
    print(kpi_site.to_string(index=False))
    print("═"*60 + "\n")