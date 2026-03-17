import sqlite3

DB_FILE = "barrage.db"

SEED = [
    # T1
    ("T1", 1, "2024-01-03", "Jean", "Vibration anormale", "Inspection + serrage support", "Terminé", 60, 0.0, None),
    ("T1", 1, "2024-02-10", "Amina", "Vibration anormale", "Roulements changés", "Terminé", 180, 250.0, "Roulements"),
    ("T1", None, "2024-03-15", "Jean", "Surchauffe", "Nettoyage circuit huile", "Terminé", 90, 50.0, "Filtre"),
    # V3
    ("V3", 2, "2024-01-06", "Paul", "Vanne ne se ferme pas", "Réglage actionneur", "En cours", 45, 0.0, None),
    ("V3", 2, "2024-01-20", "Paul", "Vanne ne se ferme pas", "Remplacement joint", "Terminé", 75, 30.0, "Joint"),
    # S2
    ("S2", 3, "2024-01-07", "Amina", "Capteur défectueux", "Remplacement capteur", "Terminé", 30, 80.0, "Capteur pression"),
]

def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO interventions (
            id_equipement, ticket_id, date_intervention, intervenant, probleme, solution,
            statut, duree_minutes, cout, pieces_changees
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        SEED,
    )
    conn.commit()
    conn.close()
    print(f"OK: {len(SEED)} interventions insérées.")

if __name__ == "__main__":
    main()