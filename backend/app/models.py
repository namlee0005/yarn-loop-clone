from sqlalchemy import String, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric
from app.core.database import Base
import uuid

def _uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    owner: Mapped["User"] = relationship(back_populates="projects")
    counters: Mapped[list["Counter"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Counter(Base):
    __tablename__ = "counters"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    max_value: Mapped[int | None] = mapped_column(Integer)
    project: Mapped["Project"] = relationship(back_populates="counters")

class Pattern(Base):
    __tablename__ = "patterns"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gauge_stitches: Mapped[object] = mapped_column(Numeric(10, 2))   # stitches per 10cm
    gauge_rows: Mapped[object] = mapped_column(Numeric(10, 2))       # rows per 10cm
    needle_size_mm: Mapped[object] = mapped_column(Numeric(5, 2))
    yarn_weight_g: Mapped[object] = mapped_column(Numeric(8, 2))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    content: Mapped[str | None] = mapped_column(Text)