# ==============================================================================
# 🛠️ UTILIS.PY — MODULE DE VISUALISATION SQL & TÉLÉMÉTRIE IOT (PROJET 07)
# ==============================================================================
import sqlite3
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def query_to_dataframe(db_file: str, query: str, params: tuple = None) -> pd.DataFrame:
    """Exécute une requête SQL SELECT et retourne le résultat sous forme de DataFrame.

    :param db_file: Chemin du fichier SQLite (.db)
    :param query: Requête SQL (ex: "SELECT * FROM telemetrie_energie")
    :param params: Paramètres sécurisés de la requête SQL (tuple)
    :return: DataFrame Pandas nettoyé avec index temporel si présent
    """
    conn = sqlite3.connect(db_file)
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)

        # Conversion automatique de la colonne timestamp en datetime si elle existe
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df
    finally:
        conn.close()


def plot_telemetrie_temporelle(
    df: pd.DataFrame,
    x_col: str = "timestamp",
    y_col: str = "puissance_w",
    hue_col: str = "sensor_id",
    title: str = "Télémétrie Énergétique IoT",
    ylabel: str = "Puissance (W)",
) -> None:
    """Trace la série temporelle d'un ou plusieurs capteurs issus d'une requête SQL."""
    plt.figure(figsize=(10, 4.5))

    if hue_col and hue_col in df.columns:
        for sensor_id, group in df.groupby(hue_col):
            plt.plot(
                group[x_col], group[y_col], marker="o", ms=3, label=f"Capteur: {sensor_id}"
            )
        plt.legend(loc="upper right")
    else:
        plt.plot(df[x_col], df[y_col], color="#1f77b4", linewidth=1.8, marker="o", ms=3)

    plt.title(title, fontweight="bold")
    plt.xlabel("Horodatage")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle="--", alpha=0.5)

    # Formatage propre des heures sur l'axe X
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M"))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()


def plot_agregation_capteurs(
    df: pd.DataFrame,
    cat_col: str = "sensor_id",
    val_col: str = "energie_kwh",
    title: str = "Bilan Énergétique par Capteur",
    ylabel: str = "Énergie Cumulée (kWh)",
) -> None:
    """Affiche un diagramme en barres des agrégations SQL (GROUP BY)."""
    plt.figure(figsize=(8, 4))

    couleurs = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    bars = plt.bar(
        df[cat_col],
        df[val_col],
        color=couleurs[: len(df)],
        edgecolor="black",
        alpha=0.85,
        width=0.5,
    )

    # Affichage des valeurs exactes au-dessus de chaque barre
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.2f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    plt.title(title, fontweight="bold")
    plt.xlabel("Capteur / Zone")
    plt.ylabel(ylabel)
    plt.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()


def plot_dashboard_sql_complet(
    df_series: pd.DataFrame,
    df_agreg: pd.DataFrame,
    title: str = "Rapport Globale IoT SQL",
) -> None:
    """Génère un tableau de bord à double vue (Série temporelle + Agrégation)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Vue 1 : Courbe temporelle
    if "sensor_id" in df_series.columns:
        for sensor_id, group in df_series.groupby("sensor_id"):
            ax1.plot(
                group["timestamp"], group["puissance_w"], label=str(sensor_id)
            )
        ax1.legend()
    else:
        ax1.plot(df_series["timestamp"], df_series["puissance_w"], color="#1f77b4")

    ax1.set_title("Flux Puissance Instantanée (W)")
    ax1.set_xlabel("Horodatage")
    ax1.set_ylabel("Puissance (W)")
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Vue 2 : Repartition par barres
    ax2.bar(
        df_agreg["sensor_id"],
        df_agreg["puissance_moyenne"],
        color="#2ca02c",
        alpha=0.8,
    )
    ax2.set_title("Puissance Moyenne par Capteur (W)")
    ax2.set_xlabel("Capteur")
    ax2.set_ylabel("Moyenne (W)")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


print("✅ Module 'utilis.py' chargé avec succès !")