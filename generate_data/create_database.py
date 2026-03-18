import csv
import os
import sqlite3

# Define the path for the database and the data directory
DB_FILE = "barrage.db"
DATA_DIR = "generate_data"


def create_database():
    """
    Creates the SQLite database and all the necessary tables.
    """
    # Remove the DB file if it exists to start from scratch
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Creating tables...")

    # --- Create meteo table ---
    cursor.execute("""
    CREATE TABLE meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        debit_riviere_m3s REAL,
        pluviometrie_mm REAL
    );
    """)

    # --- Create maintenance table ---
    # Table centrale du projet :
    # - tickets de maintenance
    # - état des équipements (TDB)
    # - historique / détails / analyse des interventions
    cursor.execute("""
    CREATE TABLE maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_equipement TEXT NOT NULL,
        nom_equipement TEXT,
        description TEXT,
        statut TEXT,
        date_creation TEXT,
        ticket_id INTEGER,
        date_intervention TEXT,
        intervenant TEXT,
        solution TEXT,
        duree_minutes INTEGER,
        cout REAL,
        pieces_changees TEXT
    );
    """)

    # --- Create production table ---
    cursor.execute("""
    CREATE TABLE production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        production_mwh REAL,
        volume_eau_m3 INTEGER
    );
    """)

    # --- Create meteo_previsions table ---
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
    Populates a table from a given CSV file.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    csv_path = os.path.join(DATA_DIR, csv_file)

    print(f"Populating table '{table_name}' from '{csv_path}'...")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header row

        placeholders = ", ".join(["?"] * len(header))
        query = f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({placeholders})"

        count = 0
        for row in reader:
            # Ignore blank lines frequently present at end of CSV files.
            if not row or all(not cell.strip() for cell in row):
                continue

            # Skip malformed rows instead of crashing the full import.
            if len(row) != len(header):
                print(
                    f"Skipping malformed row in '{csv_file}': "
                    f"expected {len(header)} values, got {len(row)} -> {row}"
                )
                continue

            try:
                cursor.execute(query, row)
                count += 1
            except (sqlite3.InterfaceError, sqlite3.ProgrammingError) as e:
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
    print(f"You can now find your database in the file named '{DB_FILE}'.")