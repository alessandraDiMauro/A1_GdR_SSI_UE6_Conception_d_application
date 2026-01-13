# Endpoints de l'API pour la météo
from fastapi import APIRouter

router = APIRouter()

@router.get("/releves")
def get_releves():
    # Logique pour récupérer les relevés météo
    return {"message": "Relevés météo"}
