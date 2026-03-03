import sqlite3

DB_FILE = "barrage.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipement TEXT NOT NULL,
    ticket_id INTEGER NULL,
    date_intervention TEXT NOT NULL,
    intervenant TEXT NOT NULL,
    probleme TEXT NOT NULL,
    solution TEXT NOT NULL,
    statut TEXT NULL,
    duree_minutes INTEGER NULL,
    cout REAL NULL,
    pieces_changees TEXT NULL,
    FOREIGN KEY(ticket_id) REFERENCES maintenance(id)
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_interventions_id_equipement ON interventions(id_equipement);",
    "CREATE INDEX IF NOT EXISTS ix_interventions_ticket_id ON interventions(ticket_id);",
    "CREATE INDEX IF NOT EXISTS ix_interventions_date ON interventions(date_intervention);",
    "CREATE INDEX IF NOT EXISTS ix_interventions_equip_date ON interventions(id_equipement, date_intervention);",
    "CREATE INDEX IF NOT EXISTS ix_interventions_equip_prob ON interventions(id_equipement, probleme);",
]

def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(CREATE_SQL)
    for sql in INDEXES:
        cur.execute(sql)
    conn.commit()
    conn.close()
    print("OK: table interventions + index créés (si absent).")

if __name__ == "__main__":
    main()