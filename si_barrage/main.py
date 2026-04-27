from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from si_barrage.modules.maintenance.router import router as maintenance_router
from si_barrage.modules.maintenance.ui_router import router as maintenance_ui_router

from .db import get_db
from .modules.dashboard import router as dashboard_router
from .modules.meteo import router as meteo_router
from .modules.production import router as production_router


# 👉 AJOUT demandé par le prof
tags_metadata = [
    {
        "name": "maintenance",
        "description": "Gestion de la maintenance : tickets, interventions, suivi des équipements et tableau de bord.",
    },
    {
        "name": "production",
        "description": "Gestion de la production du barrage : données, configuration et analyse.",
    },
    {
        "name": "meteo",
        "description": "Données météorologiques liées au barrage.",
    },
    {
        "name": "root",
        "description": "Routes de base de l’API.",
    },
    {
        "name": "database",
        "description": "Vérification de la connexion à la base de données.",
    },
]


app = FastAPI(
    title="SI Barrage",
    description="API pour la gestion d'un barrage hydroélectrique",
    version="0.1.0",
    openapi_tags=tags_metadata,  # ✅ IMPORTANT
)


# 👉 CORRECTION DES TAGS (uniformisation)
app.include_router(meteo_router.router, prefix="/meteo", tags=["meteo"])
app.include_router(maintenance_router, prefix="/maintenance", tags=["maintenance"])
app.include_router(maintenance_ui_router, prefix="/maintenance", tags=["maintenance"])
app.include_router(production_router.router, prefix="/production", tags=["production"])


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Bienvenue sur l'API du SI Barrage"}


@app.get("/db", tags=["database"])
def check_db_connection(db: Session = Depends(get_db)):
    """
    Vérifie la connexion à la base de données et liste les tables disponibles.
    """
    try:
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result]
        return {"status": "ok", "tables": tables}
    except Exception as e:
        return {"status": "error", "detail": str(e)}