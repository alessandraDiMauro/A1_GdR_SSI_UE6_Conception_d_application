# Endpoints de l'API pour la maintenance
from fastapi import APIRouter
from pydantic import BaseModel
from si_barrage.db import get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from sqlalchemy import text
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from . import services

router = APIRouter()

@router.post("/tickets")
async def create_ticket(nom: str = Form(...),
    id_equipement: str = Form(...),
    nom_equipement: str = Form(...),
    statut: str = Form(...),
    description: str = Form(...),
    date_creation: str = Form(...),
    niv_urgence: str = Form(...), db: Session = Depends(get_db)):
    try:
        my_description = (
            f"{description}, technicien: {nom}, niv_urgence: {niv_urgence}"
        )
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
        return RedirectResponse(url="/maintenance/", status_code=303)
    except Exception as e:
        db.rollback()
        print("Erreur:", e)
        return RedirectResponse(url="/maintenance/nouveau-ticket?error=1", status_code=303)  


@router.get("/", response_class=HTMLResponse)
async def maintenance_dashboard_page():
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Maintenance — Vue globale</title>
      <script src="https://unpkg.com/htmx.org@1.9.10"></script>
      <style>
        body{font-family:system-ui; padding:20px; max-width:1100px; margin:0 auto;}
        h1{margin-bottom:12px;}
        .card{border:1px solid #ddd; border-radius:12px; padding:16px;}
        .loading{color:#666; padding:12px;}
        table{width:100%; border-collapse:collapse;}
        th,td{padding:10px; border-bottom:1px solid #eee; text-align:left;}


      body{
          font-family:system-ui;
          padding:20px;
          max-width:1100px;
          margin:0 auto;
      }

      h1{
          margin-bottom:20px;
      }

      /* KPI */

      .kpi-grid{
          display:flex;
          gap:20px;
          margin-bottom:25px;
      }

      .kpi-card{
          flex:1;
          background:#f8f9fa;
          border-radius:12px;
          padding:20px;
          text-align:center;
          border:1px solid #ddd;
      }

      .kpi-number{
          font-size:36px;
          font-weight:bold;
      }

      .kpi-label{
          color:#666;
          margin-top:5px;
      }

      /* tableau */

      .card{
          border:1px solid #ddd;
          border-radius:12px;
          padding:16px;
      }

      table{
          width:100%;
          border-collapse:collapse;
      }

      th,td{
          padding:10px;
          border-bottom:1px solid #eee;
          text-align:left;
      }

    /* KPI couleurs */

    .kpi-termine{
        border:2px solid green;
    }

    .kpi-encours{
        border:2px solid orange;
    }

    .kpi-attente{
        border:2px solid lightcoral;
    }


    .kpi-card{
    flex:1;
    background:white;
    border-radius:12px;
    padding:20px;
    text-align:center;
    box-shadow:0 2px 6px rgba(0,0,0,0.09);
    }
      </style>
    </head>
    <body>

    <h2>Vue globale</h2>

    <div id="kpis"
        hx-get="/maintenance/tdb/api/kpis"
        hx-trigger="load, every 10s"
        hx-swap="innerHTML">
    </div>

      <h1>🛠️ Maintenance : Vue globale du parc</h1>
                                  <!-- on récupère les donnees de la requete equipement-table puis on affche ds le tableau final -->
      <div class="card">
        <h2>État des équipements (dernier événement)</h2>
        <div id="equipment-table"
             hx-get="/maintenance/tdb/api/equipment-table" 
             hx-trigger="load, every 10s"
             hx-swap="innerHTML">
          <div class="loading">Chargement…</div>
        </div>
      </div>
      <div style="margin: 20px 0;">
     <a href="/maintenance/nouveau-ticket" 
        class="btn" 
        style="background: #007bff; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
        ➕ Créer un nouveau ticket
  </a>
</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

#sert à créer les user stories mais n'est pas lié au TDB final
@router.get("/api/equipment-table", response_class=HTMLResponse)
async def equipment_table(db: Session = Depends(get_db)):
    rows = services.get_equipment_last_events(db)

    trs = ""
    for r in rows:
        trs += f"""
        <tr>
          <td>{r["id_equipement"]}</td>
          <td>{r["nom_equipement"]}</td>
          <td>{r["statut"]}</td>
          <td>{r["date_creation"]}</td>
          <td>{r["description"]}</td>
        </tr>
        """

    html = f"""
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nom</th>
          <th>Dernier statut</th>
          <th>Dernière MAJ</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {trs if trs else '<tr><td colspan="5">Aucune donnée maintenance.</td></tr>'}
      </tbody>
    </table>
    """
    return HTMLResponse(content=html)

#partie kpis
@router.get("/api/kpis", response_class=HTMLResponse)
async def kpis(db: Session = Depends(get_db)):

    data = services.get_kpis(db)

    html = f"""
    <div class="kpi-grid">

        <div class="kpi-card kpi-termine">
            <div class="kpi-number">{data["termines"]}</div>
            <div class="kpi-label">Terminés</div>
        </div>

        <div class="kpi-card kpi-encours">
            <div class="kpi-number">{data["encours"]}</div>
            <div class="kpi-label">En cours</div>
        </div>

        <div class="kpi-card kpi-attente">
            <div class="kpi-number">{data["attente"]}</div>
            <div class="kpi-label">En attente</div>
        </div>

    </div>

    """

    return HTMLResponse(content=html)

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
        <a href="/maintenance/" class="back-link">← Retour à la vue globale</a>
        
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
                    <option value="en cours">En cours</option>
                    <option value="en attente">En attente</option>
                    <option value="terminé">Terminé</option>
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
                <input type="date" id="date_creation" name="date_creation" 
                       value="2026-03-03" required>
            </div>
            
            <button type="submit" class="btn">Créer le ticket</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

