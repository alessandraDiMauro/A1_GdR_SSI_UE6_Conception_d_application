from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ....db import get_db
from . import services

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def maintenance_dashboard_page():
    """
    Page principale du tableau de bord maintenance.

    Cette page charge dynamiquement :
    - les KPI
    - les filtres
    - le tableau des équipements

    On utilise HTMX pour éviter un rechargement complet après chaque action.
    """
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Maintenance — Vue globale</title>
      <script src="https://unpkg.com/htmx.org@1.9.10"></script>
      <style>
        body {
            font-family: system-ui;
            padding: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }

        h1 { margin-bottom: 20px; }

        .kpi-grid {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
        }

        .kpi-card {
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.09);
            border: 1px solid #ddd;
        }

        .kpi-number {
            font-size: 36px;
            font-weight: bold;
        }

        .kpi-label {
            color: #666;
            margin-top: 5px;
        }

        .loading {
            color: #666;
            padding: 12px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }

        .kpi-termine { border: 2px solid green; }
        .kpi-encours { border: 2px solid orange; }
        .kpi-attente { border: 2px solid lightcoral; }

        .status-termine td { background-color: #d4edda; }
        .status-encours td { background-color: #ffd8a8; }
        .status-attente td { background-color: #f8d7da; }

        .filter-bar {
            display: flex;
            gap: 16px;
            margin: 20px 0;
            align-items: center;
            flex-wrap: wrap;
        }

        .btn-delete {
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
        }

        .btn-delete:hover {
            background: #bb2d3b;
        }

        .flash-message {
            display: none;
            margin: 14px 0;
            padding: 12px 16px;
            border-radius: 8px;
            background: #d1e7dd;
            color: #0f5132;
            border: 1px solid #badbcc;
            font-weight: 500;
        }

        .info-note {
            color: #666;
            margin: 8px 0 14px 0;
            font-size: 14px;
        }
      </style>
    </head>
    <body>
      <h1>🛠️ Maintenance : Vue globale du parc</h1>

      <div id="flash-message" class="flash-message"></div>

      <h3>Répartition des équipements par statut</h3>
      <div id="kpis"
          hx-get="/maintenance/tdb/api/kpis"
          hx-trigger="load, every 10s"
          hx-swap="innerHTML">
      </div>

      <h3>Tableau récapitulatif des maintenances</h3>
      <div class="info-note">
        Le tableau affiche au maximum les 5 dernières entrées visibles, après application des filtres.
      </div>

      <div id="filter"
           hx-get="/maintenance/tdb/api/id-prefix-filter"
           hx-trigger="load"
           hx-swap="innerHTML">
      </div>

      <div id="equipment-table"
           hx-get="/maintenance/tdb/api/equipment-table"
           hx-trigger="load, every 10s"
           hx-include="#prefix-select, #status-select"
           hx-swap="innerHTML">
        <div class="loading">Chargement…</div>
      </div>

      <div style="margin: 20px 0; display:flex; gap:12px; flex-wrap:wrap;">
        <a href="/maintenance/nouveau-ticket"
           style="background:#007bff;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">
           ➕ Créer un nouveau ticket
        </a>

        <a href="/maintenance/interventions"
           style="background:#6f42c1;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">
           🛠️ Voir l'historique des interventions
        </a>
      </div>

      <script>
        // Après une suppression réussie :
        // - on recharge le tableau
        // - on recharge les KPI
        // - on affiche un message temporaire
        document.body.addEventListener("htmx:afterRequest", function(event) {
          const elt = event.detail.elt;

          if (elt && elt.matches(".btn-delete") && event.detail.successful) {
            const equipmentName = elt.getAttribute("data-equipment-name") || "cet équipement";

            const flash = document.getElementById("flash-message");
            flash.textContent = "Suppression effectuée avec succès pour " + equipmentName + ".";
            flash.style.display = "block";

            htmx.ajax("GET", "/maintenance/tdb/api/equipment-table", {
              target: "#equipment-table",
              swap: "innerHTML",
              values: {
                prefix: document.getElementById("prefix-select")?.value || "",
                status: document.getElementById("status-select")?.value || ""
              }
            });

            htmx.ajax("GET", "/maintenance/tdb/api/kpis", {
              target: "#kpis",
              swap: "innerHTML"
            });

            setTimeout(() => {
              flash.style.display = "none";
            }, 3000);
          }
        });
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/api/equipment-table", response_class=HTMLResponse)
async def equipment_table(
    prefix: str = "",
    status: str = "",
    db: Session = Depends(get_db),
):
    """
    Construit le tableau du TDB.

    Important :
    - le TDB n'affiche qu'une seule ligne par équipement : la plus récente
    - le service limite déjà le résultat aux 5 dernières entrées visibles
    - la suppression utilise le vrai `id` de la ligne dans la table maintenance
    """
    rows = services.get_equipment_events(db, prefix, status)

    trs = ""
    for r in rows:
        row_class = ""

        if r["statut"] == "Terminé":
            row_class = "status-termine"
        elif r["statut"] == "En cours":
            row_class = "status-encours"
        elif r["statut"] == "En attente":
            row_class = "status-attente"

        equipment_name = r["nom_equipement"] or r["id_equipement"]

        delete_btn = f"""
        <button
          class="btn-delete"
          data-equipment-name="{equipment_name}"
          hx-delete="/maintenance/tickets/{r['id']}"
          hx-confirm="Voulez-vous vraiment supprimer l’équipement {equipment_name} ?"
        >
          Supprimer
        </button>
        """

        trs += f"""
        <tr class="{row_class}">
          <td>{r["id_equipement"]}</td>
          <td>{r["nom_equipement"] or ""}</td>
          <td>{r["statut"] or ""}</td>
          <td>{r["date_creation"] or ""}</td>
          <td>{r["ticket_id"] if r["ticket_id"] is not None else ""}</td>
          <td>{r["description"] or ""}</td>
          <td>{delete_btn}</td>
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
          <th>Num_ticket</th>
          <th>Description</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {trs if trs else '<tr><td colspan="7">Aucune donnée maintenance.</td></tr>'}
      </tbody>
    </table>
    """
    return HTMLResponse(content=html)


@router.get("/api/kpis", response_class=HTMLResponse)
async def kpis(db: Session = Depends(get_db)):
    """
    Retourne les KPI du tableau de bord :
    - terminés
    - en cours
    - en attente
    """
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


@router.get("/api/id-prefix-filter", response_class=HTMLResponse)
async def id_prefix_filter(db: Session = Depends(get_db)):
    """
    Construit les filtres du TDB :
    - filtre par préfixe d'équipement
    - filtre par statut
    """
    prefixes = services.get_id_prefixes(db)

    options = '<option value="">Tous</option>'
    for p in prefixes:
        options += f'<option value="{p}">{p}</option>'

    html = f"""
    <div class="filter-bar">
        <label for="prefix-select">Filtre ID :</label>
        <select id="prefix-select"
                name="prefix"
                hx-preserve="true"
                hx-get="/maintenance/tdb/api/equipment-table"
                hx-trigger="change"
                hx-target="#equipment-table"
                hx-include="#prefix-select, #status-select">
            {options}
        </select>

        <label for="status-select">Filtre statut :</label>
        <select id="status-select"
                name="status"
                hx-preserve="true"
                hx-get="/maintenance/tdb/api/equipment-table"
                hx-trigger="change"
                hx-target="#equipment-table"
                hx-include="#prefix-select, #status-select">
            <option value="">Tous</option>
            <option value="Terminé">Vert - Terminé</option>
            <option value="En cours">Orange - En cours</option>
            <option value="En attente">Rouge - En attente</option>
        </select>
    </div>
    """

    return HTMLResponse(content=html)