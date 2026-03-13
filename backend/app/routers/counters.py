from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import get_db
from schemas.projects import CounterCreate, CounterUpdate, CounterResponse
from dependencies.auth import get_current_user

router = APIRouter(prefix="/projects/{project_id}/counters", tags=["counters"])


async def _assert_project_owned(project_id: int, user_id: int, db):
    """Guard: ensures the project belongs to the requesting user."""
    row = await db.fetchrow(
        "SELECT id FROM projects WHERE id = $1 AND user_id = $2",
        project_id,
        user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/", response_model=CounterResponse, status_code=status.HTTP_201_CREATED)
async def create_counter(
    project_id: int,
    payload: CounterCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    row = await db.fetchrow(
        """
        INSERT INTO counters (project_id, name, value, step)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        project_id,
        payload.name,
        payload.initial_value,
        payload.step,
    )
    return dict(row)


@router.get("/", response_model=List[CounterResponse])
async def list_counters(
    project_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    rows = await db.fetch(
        "SELECT * FROM counters WHERE project_id = $1 ORDER BY created_at ASC",
        project_id,
    )
    return [dict(r) for r in rows]


@router.post("/{counter_id}/increment", response_model=CounterResponse)
async def increment_counter(
    project_id: int,
    counter_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    row = await db.fetchrow(
        """
        UPDATE counters
        SET value = value + step, updated_at = NOW()
        WHERE id = $1 AND project_id = $2
        RETURNING *
        """,
        counter_id,
        project_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Counter not found")
    return dict(row)


@router.post("/{counter_id}/decrement", response_model=CounterResponse)
async def decrement_counter(
    project_id: int,
    counter_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    row = await db.fetchrow(
        """
        UPDATE counters
        SET value = value - step, updated_at = NOW()
        WHERE id = $1 AND project_id = $2
        RETURNING *
        """,
        counter_id,
        project_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Counter not found")
    return dict(row)


@router.patch("/{counter_id}", response_model=CounterResponse)
async def update_counter(
    project_id: int,
    counter_id: int,
    payload: CounterUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    row = await db.fetchrow(
        """
        UPDATE counters
        SET
            name       = COALESCE($3, name),
            step       = COALESCE($4, step),
            updated_at = NOW()
        WHERE id = $1 AND project_id = $2
        RETURNING *
        """,
        counter_id,
        project_id,
        payload.name,
        payload.step,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Counter not found")
    return dict(row)


@router.delete("/{counter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_counter(
    project_id: int,
    counter_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    await _assert_project_owned(project_id, current_user.id, db)
    result = await db.execute(
        "DELETE FROM counters WHERE id = $1 AND project_id = $2",
        counter_id,
        project_id,
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Counter not found")