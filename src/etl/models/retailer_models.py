"""Retailer models: Business endpoints with complete hierarchy relationships."""

from datetime import datetime

from sqlmodel import Field

from .base_models import BaseRetailerModel


class Retailer(BaseRetailerModel, table=True):
    """Individual retail outlets with complete business hierarchy assignment."""

    organization_id: str = Field(primary_key=True)  # "17302774"
    organization_name: str = Field(index=True)  # "Daun Mas Cihea"
    outlet_type: str  # "Outlet Regular" | "Outlet Server"

    # Complete business hierarchy relationships
    partner_code: str = Field(foreign_key="partner.partner_code")
    site_id: str = Field(foreign_key="site.site_id")

    # Data source tracking
    data_source: str = Field(default="etl")  # "etl" | "manual"

    # Contact information
    phone: str | None = Field(default=None)
    email: str | None = Field(default=None)
    address: str | None = Field(default=None)

    # Geographic coordinates (if available)
    coordinates: str | None = Field(default=None)  # "lat,lng" format

    # Business operational info
    is_active: bool = Field(default=True)
    registration_date: datetime | None = Field(default=None)

    # NOTE: No soft delete for retailers - hard delete only per business requirement
    # Cross-module relationships handled via FK only for loose coupling
