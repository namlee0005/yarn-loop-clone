from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class PatternBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class PatternCreate(PatternBase):
    pass


class PatternUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None


class PatternRead(PatternBase):
    id: UUID
    owner_id: UUID
    file_key: str
    original_filename: str
    file_size_bytes: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatternList(BaseModel):
    items: list[PatternRead]
    total: int
    page: int
    page_size: int