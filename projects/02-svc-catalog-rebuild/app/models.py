from datetime import datetime,timezone

from sqlmodel import Field, SQLModel


class ReportSpecBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=100)
    sql_template: str = Field(min_length=1)
    description: str | None = Field(default=None, max_length=500)


class ReportSpec(ReportSpecBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class ReportSpecCreate(ReportSpecBase):
    pass


class ReportSpecUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    owner: str | None = Field(default=None, min_length=1, max_length=100)
    sql_template: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, max_length=500)


class ReportSpecRead(ReportSpecBase):
    id: int
    created_at: datetime