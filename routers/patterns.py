import magic
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models.pattern import Pattern
from schemas.patterns import PatternCreate, PatternRead, PatternList
from services.storage import storage

router = APIRouter(prefix="/patterns", tags=["patterns"])

MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB hard limit
ALLOWED_MIME = "application/pdf"


async def _validate_pdf(data: bytes) -> None:
    """Raise 415 if bytes are not a real PDF (magic-bytes check, not extension)."""
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")
    detected = magic.from_buffer(data, mime=True)
    if detected != ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected application/pdf, got {detected}.",
        )


@router.post("/", response_model=PatternRead, status_code=status.HTTP_201_CREATED)
async def upload_pattern(
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    data = await file.read()
    await _validate_pdf(data)

    key = await storage.save(data, file.filename or "pattern.pdf")

    pattern = Pattern(
        title=title,
        original_filename=file.filename,
        file_key=key,
        file_size_bytes=len(data),
    )
    db.add(pattern)
    await db.commit()
    await db.refresh(pattern)
    return pattern


@router.get("/{pattern_id}/download")
async def download_pattern(
    pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    pattern = await db.get(Pattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found.")

    data = await storage.load(pattern.file_key)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{pattern.original_filename}"',
            "Content-Length": str(len(data)),
        },
    )


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern(
    pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    pattern = await db.get(Pattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found.")

    await storage.delete(pattern.file_key)
    await db.delete(pattern)
    await db.commit()