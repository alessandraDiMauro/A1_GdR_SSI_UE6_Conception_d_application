from si_barrage.db import get_db
from si_barrage.modules.maintenance.router import *
from si_barrage.db import SessionLocal

ticket = TicketCreate(
            nom="Clara",
            id_equipement="T1",
            nom_equipement="Turbine 1",
            statut="en cours",
            description="Ne démarre pas",
            date_creation="2026-03-02",
            niv_urgence="urgent",
        )
db = SessionLocal()
create_ticket(ticket, db)
print("OK, ticket inséré")


def print_ticket(): {

}
