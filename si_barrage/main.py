# Point d'entrée de l'application FastAPI principale
from fastapi import FastAPI
from .modules.meteo import router as meteo_router
from .modules.maintenance import router as maintenance_router
from .modules.production import router as production_router

app = FastAPI(
    title="SI Barrage",
    description="API pour la gestion d'un barrage hydroélectrique",
    version="0.1.0",
)

app.include_router(meteo_router.router, prefix="/meteo", tags=["Météo"])
app.include_router(maintenance_router.router, prefix="/maintenance", tags=["Maintenance"])
app.include_router(production_router.router, prefix="/production", tags=["Production"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API du SI Barrage"}
