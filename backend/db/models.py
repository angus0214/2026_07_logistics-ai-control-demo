from sqlmodel import Field, SQLModel
from typing import Optional

class LogisticsRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(index=True)
    status: str
    location: str
    weight: float
