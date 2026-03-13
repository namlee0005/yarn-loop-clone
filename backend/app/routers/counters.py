from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.auth import get_current_user
from app.models import User
from app.schemas.projects import CounterCreate, CounterRead, CounterUpdate
from app.services.storage import CounterService

router = APIRouter(prefix="/projects/{project_id}/counters", tags=["counters"])


@router.get("/", response_model=List[CounterRead])
def list_counters(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CounterService(db).list_for_project(project_id, current_user.id)


@router.post("/", response_model=CounterRead)
def create_counter(project_id: int, payload: CounterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CounterService(db).create(project_id, payload, current_user.id)


@router.patch("/{counter_id}", response_model=CounterRead)
def update_counter(project_id: int, counter_id: int, payload: CounterUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CounterService(db).update(counter_id, payload, current_user.id)


@router.delete("/{counter_id}")
def delete_counter(project_id: int, counter_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    CounterService(db).delete(counter_id, current_user.id)