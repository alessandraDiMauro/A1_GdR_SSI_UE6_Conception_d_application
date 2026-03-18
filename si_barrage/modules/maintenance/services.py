from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session

from .models import Intervention, MaintenanceTicket
from .schemas import InterventionCreate, InterventionUpdate


def equipment_exists(db: Session, id_equipement: str) -> bool:
    # Un équipement "existe" si on a au moins un ticket dans maintenance
    return (
        db.query(MaintenanceTicket.id)
        .filter(MaintenanceTicket.id_equipement == id_equipement)
        .first()
        is not None
    )


def get_interventions(
    db: Session,
    id_equipement: str,
    *,
    limit: int = 50,
    offset: int = 0,
) -> List[Intervention]:
    return (
        db.query(Intervention)
        .filter(Intervention.id_equipement == id_equipement)
        .order_by(desc(Intervention.date_intervention), desc(Intervention.id))
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_intervention_by_id(db: Session, intervention_id: int) -> Optional[Intervention]:
    return db.query(Intervention).filter(Intervention.id == intervention_id).first()


def create_intervention(
    db: Session,
    id_equipement: str,
    payload: InterventionCreate,
) -> Intervention:
    intervention = Intervention(
        id_equipement=id_equipement,
        date_intervention=payload.date_intervention,
        intervenant=payload.intervenant,
        probleme=payload.probleme,
        solution=payload.solution,
        ticket_id=payload.ticket_id,
        statut=payload.statut,
        duree_minutes=payload.duree_minutes,
        cout=payload.cout,
        pieces_changees=payload.pieces_changees,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


def update_intervention(
    db: Session, intervention: Intervention, payload: InterventionUpdate
) -> Intervention:
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(intervention, k, v)
    db.commit()
    db.refresh(intervention)
    return intervention


def analyse_recurrent_breakdowns(
    db: Session,
    id_equipement: str,
    *,
    top_n: int = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[int, List[dict], Optional[dict]]:
    query = db.query(Intervention).filter(Intervention.id_equipement == id_equipement)

    periode = None
    if start_date:
        query = query.filter(Intervention.date_intervention >= start_date)
    if end_date:
        query = query.filter(Intervention.date_intervention <= end_date)

    if start_date or end_date:
        periode = {"start_date": start_date, "end_date": end_date}

    total = query.count()

    rows = (
        db.query(
            Intervention.probleme.label("probleme"),
            func.count(Intervention.id).label("occurrences"),
            func.min(Intervention.date_intervention).label("premiere_date"),
            func.max(Intervention.date_intervention).label("derniere_date"),
        )
        .filter(Intervention.id_equipement == id_equipement)
        .filter(Intervention.date_intervention >= start_date if start_date else True)
        .filter(Intervention.date_intervention <= end_date if end_date else True)
        .group_by(Intervention.probleme)
        .order_by(desc("occurrences"), desc("derniere_date"))
        .limit(top_n)
        .all()
    )

    top = [
        {
            "probleme": r.probleme,
            "occurrences": int(r.occurrences),
            "premiere_date": r.premiere_date,
            "derniere_date": r.derniere_date,
        }
        for r in rows
    ]
    return total, top, periode


# Logique métier pour la maintenance


def get_equipment_last_events(db: Session) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
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
    """)
    ).fetchall()

    out = []
    for row in result:
        out.append(
            {
                "id_equipement": row[0],
                "nom_equipement": row[1],
                "statut": row[2],
                "date_creation": row[3],
                "description": row[4] if len(row) > 4 else None,
            }
        )
    return out


# partie kpis status d'équipement


def get_kpis(db):

    result = db.execute(
        text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN statut = 'Terminé' THEN 1 ELSE 0 END) as termines,
            SUM(CASE WHEN statut = 'En cours' THEN 1 ELSE 0 END) as encours,
            SUM(CASE WHEN statut = 'En attente' THEN 1 ELSE 0 END) as attente
        FROM maintenance
    """)
    ).fetchone()

    return {
        "termines": result[1] or 0,
        "encours": result[2] or 0,
        "attente": result[3] or 0,
    }
