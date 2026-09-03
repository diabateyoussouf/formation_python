# ==============================================================================
# 🛠️ UTILIS.PY — COUCHE ACCÈS DONNÉES SQL & STREAMLIT CACHING
# ==============================================================================
import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "iot_energie.db"


def init_db(db_file: str = DB_FILE) -> None:
    """Initialise la BDD SQLite et insère des données de test si elle est vide."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capteurs (
        sensor_code TEXT PRIMARY KEY,
        emplacement TEXT NOT NULL,
        type_equipement TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetrie_energie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        puissance_w REAL NOT NULL,
        tension_v REAL NOT NULL,
        FOREIGN KEY (sensor_id) REFERENCES capteurs(sensor_code)
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM capteurs;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO capteurs VALUES (?, ?, ?);",
            [
                ("SOLAR_PANEL_01", "Toiture Bâtiment A", "Solaire"),
                ("WIND_TURBINE_02", "Ferme Éolienne Est", "Éolien"),
                ("BATTERY_BANK_01", "Local Technique 01", "Stockage"),
            ],
        )

        cursor.executemany(
            "INSERT INTO telemetrie_energie (sensor_id, timestamp, puissance_w, tension_v) VALUES (?, ?, ?, ?);",
            [
                ("SOLAR_PANEL_01", "2026-08-31 08:00:00", 450.00, 228.5),
                ("WIND_TURBINE_02", "2026-08-31 08:00:00", 2100.00, 400.0),
                ("SOLAR_PANEL_01", "2026-08-31 12:00:00", 1850.50, 231.0),
                ("WIND_TURBINE_02", "2026-08-31 12:00:00", 2500.00, 401.0),
                ("BATTERY_BANK_01", "2026-08-31 12:00:00", -450.00, 48.2),
            ],
        )
        conn.commit()

    conn.close()


@st.cache_data(ttl=60)
def load_parc_capteurs(db_file: str = DB_FILE) -> pd.DataFrame:
    """Charge la liste complète des capteurs et leurs métadonnées."""
    init_db(db_file)
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query(
        "SELECT sensor_code, emplacement, type_equipement FROM capteurs;", conn
    )
    conn.close()
    return df


@st.cache_data(ttl=30)
def load_telemetrie_filtree(
    sensor_ids: list = None, db_file: str = DB_FILE
) -> pd.DataFrame:
    """Extrait la télémétrie enrichie avec filtrage dynamique par capteur."""
    init_db(db_file)
    conn = sqlite3.connect(db_file)

    sql = """
    SELECT 
        t.id,
        t.timestamp,
        t.sensor_id,
        c.emplacement,
        c.type_equipement,
        t.puissance_w,
        t.tension_v
    FROM telemetrie_energie t
    LEFT JOIN capteurs c ON t.sensor_id = c.sensor_code
    """

    if sensor_ids:
        placeholders = ",".join(["?"] * len(sensor_ids))
        sql += f" WHERE t.sensor_id IN ({placeholders})"
        sql += " ORDER BY t.timestamp DESC;"
        df = pd.read_sql_query(sql, conn, params=sensor_ids)
    else:
        sql += " ORDER BY t.timestamp DESC;"
        df = pd.read_sql_query(sql, conn)

    conn.close()

    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data(ttl=30)
def get_kpi_metrics(df: pd.DataFrame) -> dict:
    """Calcule les indicateurs clés de performance du réseau Smart Grid."""
    if df.empty:
        return {
            "puissance_totale_kw": 0.0,
            "puissance_moyenne_w": 0.0,
            "pic_max_w": 0.0,
            "nb_mesures": 0,
        }

    return {
        "puissance_totale_kw": round(df["puissance_w"].sum() / 1000.0, 2),
        "puissance_moyenne_w": round(df["puissance_w"].mean(), 2),
        "pic_max_w": round(df["puissance_w"].max(), 2),
        "nb_mesures": len(df),
    }


def insert_trame_telemetrie(
    sensor_id: str,
    timestamp: str,
    puissance_w: float,
    tension_v: float,
    db_file: str = DB_FILE,
) -> None:
    """Injecte une nouvelle ligne de télémétrie dans la base SQLite."""
    conn = sqlite3.connect(db_file)
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