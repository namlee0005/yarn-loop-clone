from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.auth import get_current_user
from app.models import User
from app.schemas.stash import StashCreate, StashRead, StashUpdate
from app.services.storage import StashService

router = APIRouter(prefix="/stash", tags=["stash"])


@router.get("/", response_model=List[StashRead])
def list_stash(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return StashService(db).list_for_user(current_user.id)


@router.post("/", response_model=StashRead, status_code=status.HTTP_201_CREATED)
def add_to_stash(payload: StashCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return StashService(db).create(payload, current_user.id)


@router.get("/{stash_id}", response_model=StashRead)
def get_stash_item(stash_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = StashService(db).get(stash_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Stash item not found")
    return item


@router.patch("/{stash_id}", response_model=StashRead)
def update_stash_item(stash_id: int, payload: StashUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return StashService(db).update(stash_id, payload, current_user.id)


@router.delete("/{stash_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stash_item(stash_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    StashService(db).delete(stash_id, current_user.id)