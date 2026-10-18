import sqlite3
import os

# Remplacez 'hotel.db' par le nom/chemin exact de votre fichier de base de données SQLite
DB_PATH = "hotel_belvedere.db" 

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Fichier de base de données introuvable à l'emplacement : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("statut", "VARCHAR(50) DEFAULT 'EN_ATTENTE'"),
        ("mode_garantie", "VARCHAR(50)"),
        ("ref_virement", "VARCHAR(100)")
    ]

    print("🚀 Début de la migration de la table 'reservations'...")

    for col_name, col_type in columns_to_add:
        try:
            sql = f"ALTER TABLE reservations ADD COLUMN {col_name} {col_type};"
            cursor.execute(sql)
            print(f"  ✅ Colonne '{col_name}' ajoutée.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"  ℹ️ Colonne '{col_name}' déjà existante (ignorée).")
            else:
                print(f"  ⚠️ Erreur lors de l'ajout de '{col_name}': {e}")

    conn.commit()
    conn.close()
    print("✨ Migration terminée avec succès !")

if __name__ == "__main__":
    migrate_database()