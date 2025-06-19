"""model dan entitas for project Bussiness Dashboard."""

from sqlmodel import Field, SQLModel, create_engine


class Partner(SQLModel, table=True):
    """Model for Partner entity."""

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    organization_id: str = Field(index=True, nullable=False, unique=True)
    status: str = Field(default="active", index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
