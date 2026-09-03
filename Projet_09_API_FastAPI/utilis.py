import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = "iot_energie.db"


def get_connection():
    """Crée et retourne une connexion SQLite avec accès par nom de colonne."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise la table de télémétrie énergétique."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetrie_energie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        puissance_w REAL NOT NULL,
        tension_v REAL NOT NULL
    );
    """)
    conn.commit()
    conn.close()


def insert_trame(sensor_id: str, puissance_w: float, tension_v: float, timestamp: str = None) -> bool:
    """Insère une nouvelle trame IoT en BDD."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO telemetrie_energie (sensor_id, timestamp, puissance_w, tension_v)
        VALUES (?, ?, ?, ?);
        """,
        (sensor_id, timestamp, puissance_w, tension_v),
    )
    conn.commit()
    conn.close()
    return True


def fetch_telemetrie(sensor_id: str = None, limit: int = 50) -> list:
    """Récupère les dernières trames enregistrées."""
    conn = get_connection()
    cursor = conn.cursor()

    if sensor_id:
        cursor.execute(
            "SELECT * FROM telemetrie_energie WHERE sensor_id = ? ORDER BY id DESC LIMIT ?;",
            (sensor_id, limit),
        )
    else:
        cursor.execute(
            "SELECT * FROM telemetrie_energie ORDER BY id DESC LIMIT ?;",
            (limit,),
        )

    lignes = cursor.fetchall()
    conn.close()
    return [dict(ligne) for ligne in lignes]


def fetch_stats_capteur(sensor_id: str) -> dict:
    """Calcule les métriques cumulées pour un capteur donné."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            COUNT(*) as nb_trames,
            AVG(puissance_w) as puissance_moy,
            MAX(puissance_w) as puissance_max,
            AVG(tension_v) as tension_moy
        FROM telemetrie_energie 
        WHERE sensor_id = ?;
        """,
        (sensor_id,),
    )
    resultat = cursor.fetchone()
    conn.close()

    if not resultat or resultat["nb_trames"] == 0:
        return None

    return dict(resultat)


def load_telemetrie_df() -> pd.DataFrame:
    """Charge l'ensemble des données sous forme de DataFrame Pandas."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM telemetrie_energie ORDER BY timestamp ASC;", conn)
    conn.close()
    return df