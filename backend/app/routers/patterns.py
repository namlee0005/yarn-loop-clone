from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.auth import get_current_user
from app.models import User
from app.schemas.patterns import PatternCreate, PatternRead, PatternUpdate
from app.services.storage import PatternService

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.get("/", response_model=List[PatternRead])
def list_patterns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PatternService(db).list_for_user(current_user.id)


@router.post("/", response_model=PatternRead, status_code=status.HTTP_201_CREATED)
def create_pattern(payload: PatternCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PatternService(db).create(payload, current_user.id)


@router.get("/{pattern_id}", response_model=PatternRead)
def get_pattern(pattern_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pattern = PatternService(db).get(pattern_id, current_user.id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern


@router.patch("/{pattern_id}", response_model=PatternRead)
def update_pattern(pattern_id: int, payload: PatternUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PatternService(db).update(pattern_id, payload, current_user.id)


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pattern(pattern_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    PatternService(db).delete(pattern_id, current_user.id)