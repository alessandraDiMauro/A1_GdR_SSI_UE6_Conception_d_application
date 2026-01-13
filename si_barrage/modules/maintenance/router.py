# Endpoints de l'API pour la maintenance
from fastapi import APIRouter

router = APIRouter()

@router.get("/tickets")
def get_tickets():
    # Logique pour récupérer les tickets de maintenance
    return {"message": "Tickets de maintenance"}
