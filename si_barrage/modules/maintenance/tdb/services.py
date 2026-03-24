from sqlalchemy import text


def get_equipment_events(db, prefix: str = "", status: str = ""):
    """
    Retourne le dernier état connu de chaque équipement pour alimenter
    le tableau de bord (TDB).

    Idée métier :
    - un même équipement peut avoir plusieurs lignes dans `maintenance`
      car cette table sert aussi d'historique
    - le TDB, lui, ne doit afficher qu'une seule ligne par équipement :
      la plus récente
    """

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
                    ticket_id,
                    description,

                    -- On classe les lignes d'un même équipement
                    -- de la plus récente à la plus ancienne.
                    ROW_NUMBER() OVER (
                        PARTITION BY id_equipement
                        ORDER BY date_creation DESC, id DESC
                    ) AS rn
                FROM maintenance
                WHERE id_equipement IS NOT NULL
                  AND LENGTH(id_equipement) > 0

                  -- Les suppressions logiques ne doivent plus apparaître
                  -- dans le tableau de bord.
                  AND statut != 'Supprimé'
            )
            SELECT
                id,
                id_equipement,
                nom_equipement,
                statut,
                date_creation,
                ticket_id,
                description
            FROM ranked
            WHERE rn = 1

              -- Filtre optionnel sur la première lettre.
              AND (:prefix = '' OR UPPER(SUBSTR(id_equipement, 1, 1)) = :prefix)

              -- Filtre optionnel sur le statut.
              AND (:status = '' OR statut = :status)

            ORDER BY date_creation DESC, id_equipement ASC
        """),
        params,
    ).fetchall()

    return [
        {
            "id": r[0],  # vrai identifiant de la ligne
            "id_equipement": r[1],
            "nom_equipement": r[2],
            "statut": r[3],
            "date_creation": r[4],
            "ticket_id": r[5],
            "description": r[6],
        }
        for r in result
    ]


def get_kpis(db):
    """
    Calcule les KPI du tableau de bord.

    Logique :
    - on ne compte pas toutes les lignes historiques
    - on compte uniquement le dernier état connu de chaque équipement

    Les lignes 'Supprimé' sont exclues.
    """

    result = db.execute(
        text("""
            WITH ranked AS (
                SELECT
                    id,
                    id_equipement,
                    statut,

                    -- Même logique que pour le tableau :
                    -- on identifie la ligne la plus récente par équipement.
                    ROW_NUMBER() OVER (
                        PARTITION BY id_equipement
                        ORDER BY date_creation DESC, id DESC
                    ) AS rn
                FROM maintenance
                WHERE id_equipement IS NOT NULL
                  AND LENGTH(id_equipement) > 0
                  AND statut != 'Supprimé'
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
    """
    Retourne la liste des préfixes disponibles pour le filtre du tableau de bord.

    On travaille ici aussi sur le dernier état connu de chaque équipement,
    pour que le filtre reflète ce qui est réellement visible dans le TDB.

    Les lignes 'Supprimé' sont exclues.
    """

    rows = db.execute(
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
                  AND statut != 'Supprimé'
            )
            SELECT DISTINCT UPPER(SUBSTR(id_equipement, 1, 1)) AS prefix
            FROM ranked
            WHERE rn = 1
            ORDER BY prefix
        """)
    ).fetchall()

    return [r[0] for r in rows if r[0]]
