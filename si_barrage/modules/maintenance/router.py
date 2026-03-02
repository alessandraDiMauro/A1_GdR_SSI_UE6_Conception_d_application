# Endpoints de l'API pour la maintenance
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
from .tdb.router import router as tdb_router

router = APIRouter()
router.include_router(tdb_router, prefix="/tdb", tags=["Partie Maintenance"])