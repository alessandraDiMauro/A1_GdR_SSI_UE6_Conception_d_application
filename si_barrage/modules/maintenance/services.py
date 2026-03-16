# Logique métier pour la maintenance

from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_equipment_last_events(db: Session) -> List[Dict[str, Any]]:
    result = db.execute(text("""
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
      ORDER BY m.id_equipement ASC
    """)).fetchall()

    out = []
    for row in result:
        out.append({
            "id_equipement": row[0],
            "nom_equipement": row[1],
            "statut": row[2],
            "date_creation": row[3],
            "description": row[4] if len(row) > 4 else None
        })
    return out

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
