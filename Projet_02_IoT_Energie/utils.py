import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def afficher_bilan_puissance(p_w, e_kwh):
    """Affiche le résultat des formules physiques (Quête 1)."""
    print("\n" + "═"*55)
    print("⚡ BILAN PHYSIQUE DU CONVERTISSEUR")
    print("═"*55)
    print(f"  • Puissance Instantanée (P) : {p_w:.2f} W ({p_w/1000:.3f} kW)")
    print(f"  • Énergie Produite (E)      : {e_kwh:.4f} kWh")
    print("═"*55 + "\n")


def tracer_dataframe_energie(df):
    """Trace les courbes de puissance et tension issues du DataFrame (Quête 2)."""
    fig, ax1 = plt.subplots(figsize=(9, 4))

    color = '#1f77b4'
    ax1.set_xlabel('Index Temporel')
    ax1.set_ylabel('Puissance (kW)', color=color)
    ax1.plot(df.index, df['puissance_kw'], color=color, marker='o', linewidth=2, label='Puissance (kW)')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = '#ff7f0e'
    ax2.set_ylabel('Tension (V)', color=color)
    ax2.plot(df.index, df['tension_v'], color=color, linestyle='--', marker='s', label='Tension (V)')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("📊 Relevés Télémesurés du Smart Grid (Pandas DataFrame)", fontweight='bold')
    fig.tight_layout()
    plt.show()


def tracer_nettoyage_pandas(df_brut, df_propre):
    """Affiche la comparaison avant/après imputation des NaN (Quête 3)."""
    plt.figure(figsize=(9, 4))
    plt.plot(df_brut.index, df_brut['tension_v'], 'ro--', label='Tension Brute (avec Trous NaN)', alpha=0.6)
    plt.plot(df_propre.index, df_propre['tension_v'], 'go-', label='Tension Corrigée (Forward Fill)', linewidth=2)
    plt.title("🛠️ Imputation des Données Manquantes Temporelles (FFill)", fontweight='bold')
    plt.xlabel("Échantillons Horaires")
    plt.ylabel("Tension (V)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def tracer_agrégation_journaliere(df_journalier):
    """Affiche un diagramme en barres de la production quotidienne (Quête 4)."""
    plt.figure(figsize=(8, 4))
    bars = plt.bar(df_journalier['date'].astype(str), df_journalier['energie_kwh'], color='#2ca02c', alpha=0.85)
    plt.title("☀️ Production Énergétique Quotidienne (kWh)", fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Énergie Totale (kWh)")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f} kWh", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.show()


def tracer_emissions_co2(df_filtre, total_co2_kg):
    """Affiche la courbe des pics de consommation et l'empreinte carbone (Quête 5)."""
    plt.figure(figsize=(9, 4.2))
    plt.plot(df_filtre['horodateur'], df_filtre['puissance_kw'], 's-', color='#d62728', linewidth=2, label='Pics de Surchauffe (kW)')
    plt.axhline(df_filtre['puissance_kw'].mean(), color='black', linestyle=':', label='Moyenne des Pics')
    
    plt.title(f"🚨 Zones Fortes Émissions CO2 (Total Impact : {total_co2_kg:.2f} kg CO2)", fontweight='bold')
    plt.xlabel("Horodateur")
    plt.ylabel("Puissance Demandée (kW)")
    plt.xticks(rotation=20)
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.show()