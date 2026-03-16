from sqlalchemy import text


def get_equipment_last_events(db, prefix: str = "", status: str = ""):
    params = {}
    conditions = []

    if prefix:
        conditions.append("UPPER(SUBSTR(id_equipement, 1, 1)) = :prefix")
        params["prefix"] = prefix.upper()

    if status:
        conditions.append("statut = :status")
        params["status"] = status

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    result = db.execute(text(f"""
        SELECT
            id_equipement,
            COALESCE(nom_equipement, id_equipement) AS nom_equipement,
            statut,
            date_creation,
            description
        FROM maintenance
        {where}
        ORDER BY date_creation DESC, id_equipement ASC
    """), params).fetchall()

    return [
        {
            "id_equipement": r[0],
            "nom_equipement": r[1],
            "statut": r[2],
            "date_creation": r[3],
            "description": r[4]
        }
        for r in result
    ]


def get_kpis(db):
    result = db.execute(text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN statut = 'Terminé' THEN 1 ELSE 0 END) as termines,
            SUM(CASE WHEN statut = 'En cours' THEN 1 ELSE 0 END) as encours,
            SUM(CASE WHEN statut = 'En attente' THEN 1 ELSE 0 END) as attente
        FROM maintenance
    """)).fetchone()

    return {
        "termines": result[1] or 0,
        "encours": result[2] or 0,
        "attente": result[3] or 0
    }


def get_id_prefixes(db):
    rows = db.execute(text("""
        SELECT DISTINCT UPPER(SUBSTR(id_equipement, 1, 1)) AS prefix
        FROM maintenance
        WHERE id_equipement IS NOT NULL
          AND LENGTH(id_equipement) > 0
        ORDER BY prefix
    """)).fetchall()

    return [r[0] for r in rows if r[0]]