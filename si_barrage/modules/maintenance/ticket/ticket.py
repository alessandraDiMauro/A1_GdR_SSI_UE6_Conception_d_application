from si_barrage.db import get_db
from sqlalchemy.orm import Session

def create_ticket(nom, id_equipement, nom_equipement, statut, description, date_creation, niv_urgence):
    db: Session = (get_db)
    try:
        MyDescription = description + ", technicien: " + nom + ", niv_urgence:" + niv_urgence
        sql = "INSERT INTO maintenance (id_equipement, nom_equipement, statut, description, date_creation) VALUES (%s, %s, %s, %s, %s)"
        val = (id_equipement, nom_equipement, statut, MyDescription, date_creation)
        db.execute(sql, val)
        db.commit()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}    

create_ticket("Clara", "T1", "Turbine 1", "en cours", "Ne demarre pas", "2026-02-27", "urgent")

def supp_ticket(id): 
    db: Session = (get_db)
    try:
        sql = "DELETE FROM maintenance WHERE id = %s"
        val = (id)
        db.execute(sql, val)
        db.commit()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}
    
supp_ticket(6)

def print_ticket(): {

}
