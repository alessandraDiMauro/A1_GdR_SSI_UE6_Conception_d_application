from __future__ import annotations

from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .models import MaintenanceTicket, Intervention
from .schemas import InterventionCreate, InterventionUpdate


def equipment_exists(db: Session, id_equipement: str) -> bool:
    # Un équipement "existe" si on a au moins un ticket dans maintenance
    return db.query(MaintenanceTicket.id).filter(MaintenanceTicket.id_equipement == id_equipement).first() is not None


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


def update_intervention(db: Session, intervention: Intervention, payload: InterventionUpdate) -> Intervention:
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
