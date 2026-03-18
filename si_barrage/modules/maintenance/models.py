from sqlalchemy import Column, Float, Integer, String

from si_barrage.db import Base


class MaintenanceTicket(Base):
    """
    Modèle unique de la table `maintenance`.

    Cette table centralise :
    - les tickets de maintenance
    - les informations d'intervention / historique
    - les champs utiles au tableau de bord

    On ne garde plus de modèle `Intervention` séparé.
    """

    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    # Identification équipement
    id_equipement = Column(String, nullable=False, index=True)
    nom_equipement = Column(String, nullable=True)

    # Ticket / suivi
    statut = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date_creation = Column(String, nullable=True)  # ISO: YYYY-MM-DD

    # Champs enrichis pour la feature historique / intervention
    ticket_id = Column(Integer, nullable=True, index=True)
    date_intervention = Column(String, nullable=True, index=True)  # ISO: YYYY-MM-DD
    intervenant = Column(String, nullable=True)
    solution = Column(String, nullable=True)

    # Champs complémentaires
    duree_minutes = Column(Integer, nullable=True)
    cout = Column(Float, nullable=True)
    pieces_changees = Column(String, nullable=True)