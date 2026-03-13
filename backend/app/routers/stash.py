from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import StashItem  # SQLAlchemy model
from schemas.stash import (
    StashItemCreate,
    StashItemResponse,
    StashItemUpdate,
    StashListResponse,
)
from auth.dependencies import get_current_user  # returns user UUID

router = APIRouter(prefix="/stash", tags=["stash"])


def _owned_or_404(item: StashItem | None, user_id: UUID) -> StashItem:
    if item is None or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Stash item not found")
    return item


@router.get("", response_model=StashListResponse)
async def list_stash(
    q: str | None = Query(None, description="Full-text search"),
    weight: str | None = Query(None),
    brand: str | None = Query(None),
    tags: list[str] | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    stmt = select(StashItem).where(StashItem.user_id == user_id)

    if q:
        # PostgreSQL full-text search on name, brand, fiber_content, notes
        tsquery = func.plainto_tsquery("english", q)
        tsvector = func.to_tsvector(
            "english",
            func.coalesce(StashItem.name, "")
            + " "
            + func.coalesce(StashItem.brand, "")
            + " "
            + func.coalesce(StashItem.fiber_content, "")
            + " "
            + func.coalesce(StashItem.notes, ""),
        )
        stmt = stmt.where(tsvector.op("@@")(tsquery))

    if weight:
        stmt = stmt.where(StashItem.weight.ilike(f"%{weight}%"))
    if brand:
        stmt = stmt.where(StashItem.brand.ilike(f"%{brand}%"))
    if tags:
        # PostgreSQL array overlap: tags && ARRAY[...]
        stmt = stmt.where(StashItem.tags.overlap(tags))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(StashItem.updated_at.desc()).limit(limit).offset(offset)
    items = (await db.execute(stmt)).scalars().all()

    return StashListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=StashItemResponse, status_code=status.HTTP_201_CREATED)
async def create_stash_item(
    payload: StashItemCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    item = StashItem(**payload.model_dump(), user_id=user_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=StashItemResponse)
async def get_stash_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    result = await db.get(StashItem, item_id)
    return _owned_or_404(result, user_id)


@router.patch("/{item_id}", response_model=StashItemResponse)
async def update_stash_item(
    item_id: UUID,
    payload: StashItemUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    result = await db.get(StashItem, item_id)
    item = _owned_or_404(result, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stash_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    result = await db.get(StashItem, item_id)
    _owned_or_404(result, user_id)
    await db.delete(result)
    await db.commit()