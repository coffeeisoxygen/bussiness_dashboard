"""Site models: Independent infrastructure sites/towers."""

from datetime import datetime

from sqlmodel import Field

from .base_models import BaseAuditModel


class Site(BaseAuditModel, table=True):
    """Physical sites/towers with coverage area - independent entity."""

    site_id: str = Field(primary_key=True)  # "SITE001"
    site_name: str = Field(index=True)  # "Tower Haurwangi Central"

    # Geographic coordinates
    longitude: float  # 106.8456
    latitude: float  # -6.2088

    # Coverage specification
    category: str = Field(index=True)  # "addressable" | "technical"
    reach_km: float = Field(default=2.0)  # Coverage radius in KM
    status: str = Field(default="active")  # "active" | "inactive" | "maintenance"

    # Location reference (but independent)
    desa_name: str = Field(index=True)  # "Haurwangi Timur"

    # Technical specifications
    tower_height: float | None = Field(default=None)
    power_source: str | None = Field(default=None)  # "PLN" | "Genset" | "Solar"

    # Operational info
    installation_date: datetime | None = Field(default=None)
    last_maintenance: datetime | None = Field(default=None)

    # NOTE: Deliberately no FK relationships - independent entity
    # Relationships handled at application level for flexibility
