
from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from si_barrage.db import get_db
from .tdb.router import router as tdb_router

router = APIRouter()

# On branche le sous-router du tableau de bord
router.include_router(tdb_router, prefix="/tdb", tags=["TDB Maintenance"])


@router.post("/tickets")
async def create_ticket(
    nom: str = Form(...),
    id_equipement: str = Form(...),
    nom_equipement: str = Form(...),
    statut: str = Form(...),
    description: str = Form(...),
    date_creation: str = Form(...),
    niv_urgence: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        my_description = f"{description}, technicien: {nom}, niv_urgence: {niv_urgence}"

        sql = text("""
            INSERT INTO maintenance 
            (id_equipement, nom_equipement, statut, description, date_creation) 
            VALUES (:id_equipement, :nom_equipement, :statut, :description, :date_creation)
        """)

        db.execute(
            sql,
            {
                "id_equipement": id_equipement,
                "nom_equipement": nom_equipement,
                "statut": statut,
                "description": my_description,
                "date_creation": date_creation,
            },
        )
        db.commit()

        return RedirectResponse(url="/maintenance/tdb/", status_code=303)

    except Exception as e:
        db.rollback()
        print("Erreur:", e)
        return RedirectResponse(url="/maintenance/nouveau-ticket?error=1", status_code=303)


@router.get("/nouveau-ticket", response_class=HTMLResponse)
async def nouveau_ticket_page():
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nouveau ticket — Maintenance</title>
        <style>
            body { 
                font-family: system-ui; 
                max-width: 600px; 
                margin: 40px auto; 
                padding: 20px;
            }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: 500; }
            input, select, textarea { 
                width: 100%; 
                padding: 12px; 
                border: 1px solid #ddd; 
                border-radius: 6px; 
                font-size: 16px;
                box-sizing: border-box;
            }
            .btn { 
                background: #28a745; 
                color: white; 
                padding: 14px 28px; 
                border: none; 
                border-radius: 6px; 
                font-size: 16px; 
                cursor: pointer;
                width: 100%;
            }
            .btn:hover { background: #218838; }
            .back-link { 
                display: inline-block; 
                margin-bottom: 30px; 
                color: #007bff; 
                text-decoration: none;
            }
            .back-link:hover { text-decoration: underline; }
            h1 { color: #333; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <a href="/maintenance/tdb/" class="back-link">← Retour au tableau de bord</a>
        
        <h1>➕ Nouveau ticket de maintenance</h1>
        
        <form action="/maintenance/tickets" method="POST">
            <div class="form-group">
                <label for="nom">Technicien :</label>
                <input type="text" id="nom" name="nom" required>
            </div>
            
            <div class="form-group">
                <label for="id_equipement">ID Équipement :</label>
                <input type="text" id="id_equipement" name="id_equipement" required>
            </div>
            
            <div class="form-group">
                <label for="nom_equipement">Nom Équipement :</label>
                <input type="text" id="nom_equipement" name="nom_equipement" required>
            </div>
            
            <div class="form-group">
                <label for="statut">Statut :</label>
                <select id="statut" name="statut" required>
                    <option value="">Choisir...</option>
                    <option value="En cours">En cours</option>
                    <option value="En attente">En attente</option>
                    <option value="Terminé">Terminé</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="niv_urgence">Niveau d'urgence :</label>
                <select id="niv_urgence" name="niv_urgence" required>
                    <option value="">Choisir...</option>
                    <option value="faible">Faible</option>
                    <option value="moyen">Moyen</option>
                    <option value="urgent">Urgent</option>
                    <option value="critique">Critique</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="description">Description du problème :</label>
                <textarea id="description" name="description" rows="4" required 
                          placeholder="Décrivez précisément le problème rencontré..."></textarea>
            </div>
            
            <div class="form-group">
                <label>Date de création :</label>
                <input type="date" id="date_creation" name="date_creation" required>
            </div>
            
            <button type="submit" class="btn">Créer le ticket</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

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

