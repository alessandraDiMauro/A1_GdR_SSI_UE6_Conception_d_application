from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from si_barrage.db import Base


class MaintenanceTicket(Base):
    """
    Mapping ORM de la table existante `maintenance`.
    On considère chaque ligne comme un ticket.
    """

    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    id_equipement = Column(String, nullable=False, index=True)
    nom_equipement = Column(String)
    statut = Column(String)
    description = Column(String)
    date_creation = Column(String)  # ISO: YYYY-MM-DD


class Intervention(Base):
    """
    Historique d'interventions (feature 3).
    Lié à un équipement via `id_equipement` (obligatoire)
    et optionnellement à un ticket via `ticket_id`.
    """

    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiant logique de l'équipement (ex: T1, V3, S2...)
    id_equipement = Column(String, nullable=False, index=True)

    # Ticket de maintenance source (optionnel)
    ticket_id = Column(Integer, ForeignKey("maintenance.id"), nullable=True, index=True)

    # Champs minimum requis par US 3.2
    date_intervention = Column(String, nullable=False, index=True)  # ISO: YYYY-MM-DD
    intervenant = Column(String, nullable=False)
    probleme = Column(String, nullable=False, index=True)
    solution = Column(String, nullable=False)

    # Champs optionnels (simples, non bloquants)
    statut = Column(String, nullable=True)  # ex: "Terminé"
    duree_minutes = Column(Integer, nullable=True)
    cout = Column(Float, nullable=True)
    pieces_changees = Column(String, nullable=True)

    ticket = relationship("MaintenanceTicket", backref="interventions")

    __table_args__ = (
        # Accélère: /equipements/{id}/interventions tri date
        Index("ix_interventions_equip_date", "id_equipement", "date_intervention"),
        # Accélère l'analyse de pannes récurrentes
        Index("ix_interventions_equip_prob", "id_equipement", "probleme"),
    )
