# Endpoints de l'API pour la production
from fastapi import APIRouter

router = APIRouter()

@router.get("/historique")
def get_historique():
    # Logique pour récupérer l'historique de production
    return {"message": "Historique de production"}
