
#PARTIE CODE TDB: va contenir les routes et le HTML
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ....db import get_db
from . import services

router = APIRouter()



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