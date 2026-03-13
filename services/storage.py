"""
Local filesystem storage with a clean interface designed for S3 swap.

To migrate to S3, implement StorageBackend with boto3 and swap the
STORAGE_BACKEND env var — no call-site changes needed.
"""
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads/patterns"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, data: bytes, filename: str) -> str:
        """Persist bytes and return an opaque storage key."""

    @abstractmethod
    async def load(self, key: str) -> bytes:
        """Retrieve raw bytes by storage key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove stored object by key."""

    @abstractmethod
    def public_url(self, key: str) -> str | None:
        """Return a public URL if applicable, else None."""


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: Path = UPLOAD_DIR):
        self._base = base_dir

    def _safe_path(self, key: str) -> Path:
        # Prevent path traversal: key must be a bare filename
        resolved = (self._base / Path(key).name).resolve()
        if not str(resolved).startswith(str(self._base.resolve())):
            raise ValueError(f"Path traversal detected for key: {key}")
        return resolved

    async def save(self, data: bytes, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        key = f"{uuid4().hex}{suffix}"
        dest = self._safe_path(key)
        dest.write_bytes(data)
        return key

    async def load(self, key: str) -> bytes:
        path = self._safe_path(key)
        if not path.exists():
            raise FileNotFoundError(f"No file for key: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self._safe_path(key)
        if path.exists():
            path.unlink()

    def public_url(self, key: str) -> str | None:
        return None  # Local storage has no public URL; served via API


# Singleton — swap this binding for S3StorageBackend in production
storage: StorageBackend = LocalStorageBackend()