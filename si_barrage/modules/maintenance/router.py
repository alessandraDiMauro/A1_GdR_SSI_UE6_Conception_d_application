# Mon debut

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from datetime import date

from si_barrage.db import get_db
from . import services
from .schemas import InterventionCreate, InterventionRead, AnalyseRead
from .models import MaintenanceTicket

router = APIRouter()

# BONUS: liste des tickets existants (pratique, et garde /tickets utile)
@router.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(MaintenanceTicket).order_by(MaintenanceTicket.id.desc()).all()
    return [
        {
            "id": t.id,
            "id_equipement": t.id_equipement,
            "nom_equipement": t.nom_equipement,
            "statut": t.statut,
            "description": t.description,
            "date_creation": t.date_creation,
        }
        for t in tickets
    ]


@router.get(
    "/equipements/{id_equipement}/interventions",
    response_model=List[InterventionRead],
    summary="Lister l'historique d'interventions d'un équipement",
)
def get_interventions(
    id_equipement: str = Path(..., examples=["T1"]),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(status_code=404, detail=f"Équipement inconnu: {id_equipement}")

    interventions = services.get_interventions(db, id_equipement, limit=limit, offset=offset)
    return interventions


@router.get(
    "/interventions/{intervention_id}",
    response_model=InterventionRead,
    summary="Détail d'une intervention",
)
def get_intervention_detail(
    intervention_id: int,
    db: Session = Depends(get_db),
):
    intervention = services.get_intervention_by_id(db, intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention introuvable: {intervention_id}")
    return intervention


@router.post(
    "/equipements/{id_equipement}/interventions",
    response_model=InterventionRead,
    status_code=201,
    summary="Créer une intervention pour un équipement",
)
def create_intervention(
    payload: InterventionCreate,
    id_equipement: str = Path(..., examples=["T1"]),
    db: Session = Depends(get_db),
):
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(status_code=404, detail=f"Équipement inconnu: {id_equipement}")

    # Validation: ticket_id doit exister si fourni + correspondre au bon équipement
    if payload.ticket_id is not None:
        ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == payload.ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket introuvable: {payload.ticket_id}")
        if ticket.id_equipement != id_equipement:
            raise HTTPException(status_code=400, detail="ticket_id ne correspond pas à l'équipement demandé")

    created = services.create_intervention(db, id_equipement, payload)
    return created


@router.get(
    "/equipements/{id_equipement}/interventions/analyse",
    response_model=AnalyseRead,
    summary="Analyse des pannes récurrentes (top N problèmes)",
)
def analyse_interventions(
    id_equipement: str = Path(..., examples=["T1"]),
    top_n: int = Query(5, ge=1, le=50),
    start_date: Optional[str] = Query(None, description="Filtre date ISO YYYY-MM-DD (inclusive)"),
    end_date: Optional[str] = Query(None, description="Filtre date ISO YYYY-MM-DD (inclusive)"),
    db: Session = Depends(get_db),
):
    if not services.equipment_exists(db, id_equipement):
        raise HTTPException(status_code=404, detail=f"Équipement inconnu: {id_equipement}")

    # Valide dates si fournies
    for label, value in [("start_date", start_date), ("end_date", end_date)]:
        if value is not None:
            try:
                date.fromisoformat(value)
            except Exception:
                raise HTTPException(status_code=422, detail=f"{label} doit être au format ISO YYYY-MM-DD")

    total, top, periode = services.analyse_recurrent_breakdowns(
        db,
        id_equipement,
        top_n=top_n,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "id_equipement": id_equipement,
        "total_interventions": total,
        "top_problemes": top,
        "periode": periode,
    }