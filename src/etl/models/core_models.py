"""Core business models: Partner, MicroCluster, PartnerTerritory."""

from sqlmodel import Field, Relationship

from .base_models import BaseAuditModel


class Partner(BaseAuditModel, table=True):
    """Partner - Root business entity managing multiple MC."""

    partner_code: str = Field(primary_key=True)  # "SDP1336"
    partner_name: str = Field(index=True)  # "SDP HAURWANGI CIANJUR"

    # Business contact info
    contact_person: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    email: str | None = Field(default=None)

    # Status tracking
    is_active: bool = Field(default=True)
    setup_completed: bool = Field(default=False)

    # Relationships
    micro_clusters: list["MicroCluster"] = Relationship(back_populates="partner")


class MicroCluster(BaseAuditModel, table=True):
    """Micro Cluster under Partner management."""

    mc_code: str = Field(primary_key=True)  # "MC-CIANJUR-TENGAH"
    mc_name: str = Field(index=True)  # "Micro Cluster Cianjur Tengah"

    # Parent relationship
    partner_code: str = Field(foreign_key="partner.partner_code")

    # Business info
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    # Relationships
    partner: Partner = Relationship(back_populates="micro_clusters")
    partner_territories: list["PartnerTerritory"] = Relationship(
        back_populates="micro_cluster"
    )


class PartnerTerritory(BaseAuditModel, table=True):
    """Partner Territory under MC management."""

    pt_code: str = Field(primary_key=True)  # "PT-HAURWANGI"
    pt_name: str = Field(index=True)  # "Partner Territory Haurwangi"

    # Parent relationship
    mc_code: str = Field(foreign_key="microcluster.mc_code")

    # Geographic scope
    coverage_description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    # Relationships
    micro_cluster: MicroCluster = Relationship(back_populates="partner_territories")
