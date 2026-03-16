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