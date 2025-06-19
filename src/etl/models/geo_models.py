"""Geographic models: Kecamatan, Desa administrative boundaries."""

from sqlmodel import Field, Relationship

from .base_models import BaseAuditModel


class Kecamatan(BaseAuditModel, table=True):
    """Administrative kecamatan assigned to PT."""

    kecamatan_id: str = Field(primary_key=True)  # "HAURWANGI"
    kecamatan_name: str = Field(index=True)  # "Haurwangi"

    # Business assignment
    pt_code: str = Field(foreign_key="partnerterritory.pt_code")

    # Additional info
    postal_code: str | None = Field(default=None)
    population: int | None = Field(default=None)

    # Relationships
    desa_list: list["Desa"] = Relationship(back_populates="kecamatan")


class Desa(BaseAuditModel, table=True):
    """Villages under kecamatan."""

    desa_id: str = Field(primary_key=True)  # "HAURWANGI_001"
    desa_name: str = Field(index=True)  # "Haurwangi Timur"

    # Parent relationship
    kecamatan_id: str = Field(foreign_key="kecamatan.kecamatan_id")

    # Geographic info
    postal_code: str | None = Field(default=None)
    population: int | None = Field(default=None)
    area_km2: float | None = Field(default=None)

    # Relationships
    kecamatan: Kecamatan = Relationship(back_populates="desa_list")
