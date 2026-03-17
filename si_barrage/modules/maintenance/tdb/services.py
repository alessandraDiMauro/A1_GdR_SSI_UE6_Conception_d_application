from sqlalchemy import text


def get_equipment_last_events(db, prefix: str = "", status: str = ""):
    params = {
        "prefix": prefix.upper() if prefix else "",
        "status": status if status else "",
    }

    result = db.execute(
        text("""
            WITH ranked AS (
                SELECT
                    id,
                    id_equipement,
                    COALESCE(nom_equipement, id_equipement) AS nom_equipement,
                    statut,
                    date_creation,
                    description,
                    ROW_NUMBER() OVER (
                        PARTITION BY id_equipement
                        ORDER BY date_creation DESC, id DESC
                    ) AS rn
                FROM maintenance
                WHERE id_equipement IS NOT NULL
                  AND LENGTH(id_equipement) > 0
            )
            SELECT
                id_equipement,
                nom_equipement,
                statut,
                date_creation,
                description
            FROM ranked
            WHERE rn = 1
              AND (:prefix = '' OR UPPER(SUBSTR(id_equipement, 1, 1)) = :prefix)
              AND (:status = '' OR statut = :status)
            ORDER BY date_creation DESC, id_equipement ASC
        """),
        params
    ).fetchall()

    return [
        {
            "id_equipement": r[0],
            "nom_equipement": r[1],
            "statut": r[2],
            "date_creation": r[3],
            "description": r[4],
        }
        for r in result
    ]


def get_kpis(db):
    result = db.execute(
        text("""
            WITH ranked AS (
                SELECT
                    id,
                    id_equipement,
                    statut,
                    ROW_NUMBER() OVER (
                        PARTITION BY id_equipement
                        ORDER BY date_creation DESC, id DESC
                    ) AS rn
                FROM maintenance
                WHERE id_equipement IS NOT NULL
                  AND LENGTH(id_equipement) > 0
            )
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN statut = 'Terminé' THEN 1 ELSE 0 END) AS termines,
                SUM(CASE WHEN statut = 'En cours' THEN 1 ELSE 0 END) AS encours,
                SUM(CASE WHEN statut = 'En attente' THEN 1 ELSE 0 END) AS attente
            FROM ranked
            WHERE rn = 1
        """)
    ).fetchone()

    return {
        "termines": result[1] or 0,
        "encours": result[2] or 0,
        "attente": result[3] or 0,
    }


def get_id_prefixes(db):
    rows = db.execute(
        text("""
            SELECT DISTINCT UPPER(SUBSTR(id_equipement, 1, 1)) AS prefix
            FROM maintenance
            WHERE id_equipement IS NOT NULL
              AND LENGTH(id_equipement) > 0
            ORDER BY prefix
        """)
    ).fetchall()

    return [r[0] for r in rows if r[0]]