"""Base models with audit capabilities."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class BaseAuditModel(SQLModel):
    """Base model with audit trail and soft delete capability."""

    # Audit timestamp
    created_at: datetime = Field(default=datetime.utcnow, index=True)

    # Soft delete strategy (except retailer)
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: datetime | None = Field(default=None)

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class BaseRetailerModel(SQLModel):
    """Base model for retailer - no soft delete, hard delete only."""

    # Audit timestamp only
    created_at: datetime = Field(default=datetime.utcnow, index=True)

    # NOTE: No soft delete for retailer - business requirement
