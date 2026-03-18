from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class InterventionBase(BaseModel):
    """
    Schéma logique utilisé par l'API pour représenter une intervention,
    même si les données sont désormais stockées dans la table `maintenance`.
    """

    date_intervention: str = Field(
        ...,
        examples=["2024-01-02"],
        description="Date ISO YYYY-MM-DD",
    )
    intervenant: str = Field(
        ...,
        min_length=1,
        examples=["M. Kabila"],
    )
    probleme: str = Field(
        ...,
        min_length=1,
        examples=["Vibration anormale"],
    )
    solution: str = Field(
        ...,
        min_length=1,
        examples=["Roulements changés"],
    )

    ticket_id: Optional[int] = Field(
        None,
        description="Lien optionnel vers maintenance.id",
    )
    statut: Optional[str] = Field(
        None,
        examples=["Terminé"],
    )
    duree_minutes: Optional[int] = Field(
        None,
        ge=0,
        examples=[90],
    )
    cout: Optional[float] = Field(
        None,
        ge=0,
        examples=[150.0],
    )
    pieces_changees: Optional[str] = Field(
        None,
        examples=["Roulements, joint"],
    )

    @field_validator("date_intervention")
    @classmethod
    def validate_date_iso(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except Exception:
            raise ValueError(
                "date_intervention doit être au format ISO YYYY-MM-DD (ex: 2024-01-02)"
            )
        return v

    @field_validator("intervenant", "probleme", "solution")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if v is None or not v.strip():
            raise ValueError("Ce champ ne doit pas être vide")
        return v.strip()


class InterventionCreate(InterventionBase):
    """
    Payload de création logique d'une intervention.
    Les données seront stockées dans la table `maintenance`.
    """
    pass


class InterventionUpdate(BaseModel):
    date_intervention: Optional[str] = None
    intervenant: Optional[str] = None
    probleme: Optional[str] = None
    solution: Optional[str] = None

    ticket_id: Optional[int] = None
    statut: Optional[str] = None
    duree_minutes: Optional[int] = Field(None, ge=0)
    cout: Optional[float] = Field(None, ge=0)
    pieces_changees: Optional[str] = None

    @field_validator("date_intervention")
    @classmethod
    def validate_date_iso(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except Exception:
            raise ValueError(
                "date_intervention doit être au format ISO YYYY-MM-DD (ex: 2024-01-02)"
            )
        return v

    @field_validator(
        "intervenant",
        "probleme",
        "solution",
        "statut",
        "pieces_changees",
    )
    @classmethod
    def strip_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v if v else None


class InterventionRead(InterventionBase):
    id: int
    id_equipement: str

    class Config:
        from_attributes = True


class ProblemStat(BaseModel):
    probleme: str
    occurrences: int
    premiere_date: str
    derniere_date: str


class AnalyseRead(BaseModel):
    id_equipement: str
    total_interventions: int
    top_problemes: List[ProblemStat]
    periode: Optional[dict] = None