import csv
import os
import sqlite3

DB_FILE = "barrage.db"
DATA_DIR = "generate_data"


def create_database():
    """
    Crée la base SQLite et toutes les tables nécessaires.
    """

    # Supprime la base existante pour repartir propre
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Creating tables...")

    # ------------------------
    # Table METEO
    # ------------------------
    cursor.execute("""
    CREATE TABLE meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        debit_riviere_m3s REAL,
        pluviometrie_mm REAL
    );
    """)

    # ------------------------
    # Table MAINTENANCE (CENTRALE)
    # ------------------------
    cursor.execute("""
    CREATE TABLE maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        id_equipement TEXT NOT NULL,
        nom_equipement TEXT,

        statut TEXT,
        description TEXT,         -- problème uniquement
        date_creation TEXT,

        ticket_id INTEGER,
        date_intervention TEXT,

        intervenant TEXT,         -- technicien
        solution TEXT,

        duree_minutes INTEGER,
        cout REAL,
        pieces_changees TEXT
    );
    """)

    # ------------------------
    # Table PRODUCTION
    # ------------------------
    cursor.execute("""
    CREATE TABLE production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        production_mwh REAL,
        volume_eau_m3 INTEGER
    );
    """)

    # ------------------------
    # Table PREVISIONS METEO
    # ------------------------
    cursor.execute("""
    CREATE TABLE meteo_previsions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_prevision TEXT NOT NULL,
        date_creation TEXT NOT NULL,
        debit_riviere_m3s_prevu REAL,
        pluviometrie_mm_prevue REAL
    );
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")


def populate_table(table_name, csv_file):
    """
    Remplit une table à partir d’un fichier CSV.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    csv_path = os.path.join(DATA_DIR, csv_file)

    print(f"Populating '{table_name}' from '{csv_path}'...")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        placeholders = ", ".join(["?"] * len(header))
        query = f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({placeholders})"

        count = 0

        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue

            if len(row) != len(header):
                print(f"Skipping malformed row: {row}")
                continue

            try:
                cursor.execute(query, row)
                count += 1
            except Exception as e:
                print(f"Error inserting row: {row}")
                print(e)

    conn.commit()
    conn.close()
    print(f"Inserted {count} rows into '{table_name}'.")


if __name__ == "__main__":
    create_database()

    populate_table("meteo", "meteo_data.csv")
    populate_table("maintenance", "maintenance_data.csv")
    populate_table("production", "production_data.csv")
    populate_table("meteo_previsions", "meteo_previsions_data.csv")

    print("\nDatabase generation complete.")
    print(f"Database file: '{DB_FILE}'")