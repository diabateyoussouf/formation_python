import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def tracer_inspection_energetique(df):
    """Affiche la distribution des grandeurs physiques mesurées par les capteurs du champ PV."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    
    # Distribution de l'Irradiance Solaire G (W/m²)
    ax1.hist(df['irradiance_w_m2'], bins=10, color='#e67e22', edgecolor='black', alpha=0.75)
    ax1.set_title("☀️ Irradiance Solaire Incidente $G$ (W/m²)", fontweight='bold')
    ax1.set_xlabel("Irradiance $G$ (W/m²)")
    ax1.set_ylabel("Nombre de relevés (Heures)")
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    # Distribution de la Température du Module T_mod (°C)
    ax2.hist(df['temp_module_c'], bins=10, color='#c0392b', edgecolor='black', alpha=0.75)
    ax2.set_title("🌡️ Température du Panneau $T_{mod}$ (°C)", fontweight='bold')
    ax2.set_xlabel("Température (°C)")
    ax2.set_ylabel("Nombre de relevés (Heures)")
    ax2.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.show()


def tracer_iqr_thermique(df_orig, df_filtre, q1, q3, seuil_inf, seuil_sup):
    """Visualise la détection des bugs de capteurs thermiques par la méthode statistique IQR."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    
    # Boxplot explicatif avec seuil haut IQR
    ax1.boxplot(df_orig['temp_module_c'], vert=False, patch_artist=True, boxprops=dict(facecolor='#e74c3c', alpha=0.6))
    ax1.axvline(seuil_sup, color='black', linestyle='--', linewidth=2, label=f'Seuil Maximum Valide ({seuil_sup:.1f}°C)')
    ax1.set_title("🔍 Détection des Valeurs Aberrantes ($T_{mod}$)", fontweight='bold')
    ax1.set_xlabel("Température (°C)")
    ax1.legend(loc='lower right')
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    # Comparaison du nombre de données avant et après nettoyage
    ax2.bar(['Données Brutes (Capteurs)', 'Données Propres (Filtrées)'], [len(df_orig), len(df_filtre)], 
            color=['#c0392b', '#27ae60'], width=0.4, edgecolor='black')
    ax2.set_title(f"🧹 Nettoyage : {len(df_orig) - len(df_filtre)} erreurs supprimées", fontweight='bold')
    ax2.set_ylabel("Nombre de mesures")
    ax2.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.show()


def tracer_rendement_physique(df):
    """Affiche le rendement photovoltaïque et la classification selon l'ensoleillement."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    
    # Rendement vs Irradiance
    sc = ax1.scatter(df['irradiance_w_m2'], df['rendement_pct'], c=df['temp_module_c'], cmap='inferno', alpha=0.85, edgecolors='black')
    fig.colorbar(sc, ax=ax1, label='Température $T_{mod}$ (°C)')
    ax1.set_title("⚡ Rendement $\eta$ (%) en fonction du Soleil $G$", fontweight='bold')
    ax1.set_xlabel("Irradiance Solaire $G$ (W/m²)")
    ax1.set_ylabel("Rendement Photovoltaïque $\eta$ (%)")
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    # Répartition des 3 régimes d'ensoleillement
    counts = df['regime_ensoleillement'].value_counts()
    ax2.bar(counts.index.astype(str), counts.values, color=['#2980b9', '#f39c12', '#27ae60'], edgecolor='black')
    ax2.set_title("🏷️ Catégories d'Ensoleillement (`pd.cut`)", fontweight='bold')
    ax2.set_xlabel("Régime Météo")
    ax2.set_ylabel("Nombre de mesures")
    ax2.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.show()


def tracer_kpi_regime(df_kpi):
    """Compare l'énergie produite et le rendement moyen par régime météo."""
    fig, ax1 = plt.subplots(figsize=(8.5, 4))
    
    x = np.arange(len(df_kpi))
    width = 0.35
    
    # Barre de puissance totale produite
    ax1.bar(x, df_kpi['puissance_totale_kw'], width, color='#2980b9', edgecolor='black', label='Puissance Cumulée (kW)')
    ax1.set_ylabel("Puissance Totale (kW)", color='#2980b9', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_kpi['regime_ensoleillement'])
    
    # Courbe du rendement moyen
    ax2 = ax1.twinx()
    ax2.plot(x, df_kpi['rendement_moyen_pct'], color='#c0392b', marker='s', markersize=8, linewidth=2.5, label='Rendement Moyen (%)')
    ax2.set_ylabel("Rendement Moyen $\eta$ (%)", color='#c0392b', fontweight='bold')
    
    plt.title("📊 Bilan Énergétique par Régime Météo", fontweight='bold')
    plt.tight_layout()
    plt.show()


def tracer_dashboard_energetique_eda(df):
    """Tableau de bord visuel complet pour analyser l'installation solaire."""
    fig = plt.figure(figsize=(12, 7))
    gs = fig.add_gridspec(2, 2)
    
    # Graphe 1: Puissance vs Irradiance
    ax1 = fig.add_subplot(gs[0, :])
    sc = ax1.scatter(df['irradiance_w_m2'], df['puissance_kw'], c=df['temp_module_c'], cmap='plasma', s=60, edgecolors='black')
    fig.colorbar(sc, ax=ax1, label='Température (°C)')
    ax1.set_title("🔬 Puissance Électrique Produite $P_{él}$ vs Irradiance $G$", fontweight='bold')
    ax1.set_xlabel("Irradiance Solaire Incidente $G$ (W/m²)")
    ax1.set_ylabel("Puissance Produite $P_{él}$ (kW)")
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    # Graphe 2: Stabilité de la Tension
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(df['tension_v'], bins=10, color='#27ae60', edgecolor='black', alpha=0.75)
    ax2.set_title("⚡ Tension Mesurée $V$ (Volts)", fontweight='bold')
    ax2.set_xlabel("Tension (V)")
    ax2.grid(True, linestyle='--', alpha=0.4)
    
    # Graphe 3: Rendement par Régime
    ax3 = fig.add_subplot(gs[1, 1])
    regimes = df['regime_ensoleillement'].unique()
    data_by_reg = [df[df['regime_ensoleillement'] == reg]['rendement_pct'] for reg in regimes]
    ax3.boxplot(data_by_reg, tick_labels=regimes, patch_artist=True)
    ax3.set_title("📦 Rendement $\eta$ (%) selon le Régime Météo", fontweight='bold')
    ax3.set_xlabel("Régime")
    ax3.grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    plt.show()


def afficher_bilan_projet_04(df_orig, df_final):
    """Résumé du travail effectué affiché dans la console."""
    print("\n" + "═"*65)
    print("🏆 BILAN DE L'EXERCICE DE TRAITEMENT DE DONNÉES SOLAIRES (L3)")
    print("═"*65)
    print(f"  • Mesures initiales reçues des capteurs : {len(df_orig)} lignes")
    print(f"  • Mesures physiquement correctes      : {len(df_final)} lignes")
    print(f"  • Bugs / Erreurs de mesure éliminés    : {len(df_orig) - len(df_final)} erreurs")
    print(f"  • Puissance totale produite mesurée     : {df_final['puissance_kw'].sum():.2f} kW")
    print(f"  • Rendement moyen de l'installation     : {df_final['rendement_pct'].mean():.2f} %")
    print("═"*65 + "\n")