"""Clean model imports for ETL package."""

# Base models
from .base_models import BaseAuditModel, BaseRetailerModel

# Core business models
from .core_models import MicroCluster, Partner, PartnerTerritory

# Geographic models
from .geo_models import Desa, Kecamatan

# Business endpoint models
from .retailer_models import Retailer

# Infrastructure models
from .site_models import Site

# Convenient groupings
BASE_MODELS = [BaseAuditModel, BaseRetailerModel]
CORE_MODELS = [Partner, MicroCluster, PartnerTerritory]
GEO_MODELS = [Kecamatan, Desa]
INFRASTRUCTURE_MODELS = [Site]
BUSINESS_MODELS = [Retailer]

# All models for database creation
ALL_MODELS = CORE_MODELS + GEO_MODELS + INFRASTRUCTURE_MODELS + BUSINESS_MODELS

__all__ = [
    # Base models
    "BaseAuditModel",
    "BaseRetailerModel",
    # Individual models
    "Partner",
    "MicroCluster",
    "PartnerTerritory",
    "Kecamatan",
    "Desa",
    "Site",
    "Retailer",
    # Model groups
    "BASE_MODELS",
    "CORE_MODELS",
    "GEO_MODELS",
    "INFRASTRUCTURE_MODELS",
    "BUSINESS_MODELS",
    "ALL_MODELS",
]
