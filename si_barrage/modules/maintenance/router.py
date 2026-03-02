# Endpoints de l'API pour la maintenance
from fastapi import APIRouter
from pydantic import BaseModel
from si_barrage.db import get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from sqlalchemy import text

router = APIRouter()

class TicketCreate(BaseModel):
    nom: str
    id_equipement: str
    nom_equipement: str
    statut: str
    description: str
    date_creation: str
    niv_urgence: str

@router.post("/tickets")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    try:
        my_description = (
            f"{ticket.description}, technicien: {ticket.nom}, niv_urgence: {ticket.niv_urgence}"
        )
        sql = text("""
    INSERT INTO maintenance 
    (id_equipement, nom_equipement, statut, description, date_creation) 
    VALUES (:id_equipement, :nom_equipement, :statut, :description, :date_creation)
""")
        print("sql")
        db.execute(
            sql,
            {
                "id_equipement": ticket.id_equipement,
                "nom_equipement": ticket.nom_equipement,
                "statut": ticket.statut,
                "description": my_description,
                "date_creation": ticket.date_creation,
            },
        )
        print("execute")
        db.commit()
        print("commit")
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}   


@router.get("/tickets")
def get_tickets():
    # Logique pour récupérer les tickets de maintenance
    return {"message": "Tickets de maintenance"}

