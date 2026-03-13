from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class StashItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    weight: Optional[str] = Field(None, max_length=100)  # e.g. "DK", "Worsted"
    fiber_content: Optional[str] = Field(None, max_length=500)
    color_name: Optional[str] = Field(None, max_length=255)
    colorway: Optional[str] = Field(None, max_length=255)
    yardage: Optional[int] = Field(None, ge=0)
    grams: Optional[int] = Field(None, ge=0)
    skeins: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class StashItemCreate(StashItemBase):
    pass


class StashItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = None
    weight: Optional[str] = None
    fiber_content: Optional[str] = None
    color_name: Optional[str] = None
    colorway: Optional[str] = None
    yardage: Optional[int] = Field(None, ge=0)
    grams: Optional[int] = Field(None, ge=0)
    skeins: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None


class StashItemResponse(StashItemBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StashSearchParams(BaseModel):
    q: Optional[str] = Field(None, description="Full-text search query")
    weight: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[list[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class StashListResponse(BaseModel):
    items: list[StashItemResponse]
    total: int
    limit: int
    offset: int