#PARTIE CODE TDB : va contenir uniquement les requêtes 
# et logique (kpis, liste équipements, mapping statut → couleur)

from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_equipment_last_events(db, prefix: str = ""):
    params = {}
    where = ""

    if prefix:
        where = "WHERE UPPER(SUBSTR(m.id_equipement, 1, 1)) = :prefix"
        params["prefix"] = prefix.upper()

    result = db.execute(text(f"""
      WITH last_by_eq AS (
          SELECT id_equipement, MAX(date_creation) AS max_date
          FROM maintenance
          GROUP BY id_equipement
      )
      SELECT m.id_equipement,
             COALESCE(m.nom_equipement, m.id_equipement) AS nom_equipement,
             m.statut,
             m.date_creation,
             m.description
      FROM maintenance m
      JOIN last_by_eq l
        ON l.id_equipement = m.id_equipement
       AND l.max_date = m.date_creation
      {where}
      ORDER BY m.id_equipement ASC
    """), params).fetchall()

    return [{
        "id_equipement": r[0],
        "nom_equipement": r[1],
        "statut": r[2],
        "date_creation": r[3],
        "description": r[4]
    } for r in result]

#partie kpis status d'équipement 

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

#récupère les premières lettres distinctes de l'ID pour le type d'équipement 

def get_id_prefixes(db):
    rows = db.execute(text("""
        SELECT DISTINCT UPPER(SUBSTR(id_equipement, 1, 1)) AS prefix
        FROM maintenance
        WHERE id_equipement IS NOT NULL
          AND LENGTH(id_equipement) > 0
        ORDER BY prefix
    """)).fetchall()

    return [r[0] for r in rows if r[0]]
