from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CounterResponse(BaseModel):
    id: int
    project_id: int
    name: str
    value: int
    step: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CounterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    initial_value: int = Field(0)
    step: int = Field(1, ge=1)


class CounterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    step: Optional[int] = Field(None, ge=1)