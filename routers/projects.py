from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import get_db
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from dependencies.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    row = await db.fetchrow(
        """
        INSERT INTO projects (user_id, name, description)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        current_user.id,
        payload.name,
        payload.description,
    )
    return dict(row)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    rows = await db.fetch(
        "SELECT * FROM projects WHERE user_id = $1 ORDER BY created_at DESC",
        current_user.id,
    )
    return [dict(r) for r in rows]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    row = await db.fetchrow(
        "SELECT * FROM projects WHERE id = $1 AND user_id = $2",
        project_id,
        current_user.id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(row)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    row = await db.fetchrow(
        """
        UPDATE projects
        SET
            name        = COALESCE($3, name),
            description = COALESCE($4, description),
            updated_at  = NOW()
        WHERE id = $1 AND user_id = $2
        RETURNING *
        """,
        project_id,
        current_user.id,
        payload.name,
        payload.description,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(row)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(
        "DELETE FROM projects WHERE id = $1 AND user_id = $2",
        project_id,
        current_user.id,
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Project not found")