from __future__ import annotations

import hashlib
import json
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import UUID, uuid4

from app.domains.artifacts.schemas import ArtifactRead
from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field

_MANIFEST_LOCK = Lock()
_ALLOWED_EXTENSIONS = {'.txt', '.csv', '.json', '.pdf', '.png', '.jpg', '.jpeg', '.webp'}
_ALLOWED_MIME_TYPES = {
    'text/plain',
    'text/csv',
    'application/json',
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/webp',
}
_DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024


class ArtifactStorageError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ArtifactNotFoundError(ArtifactStorageError):
    def __init__(self, code: str = 'artifact_not_found', message: str = 'artifact_not_found') -> None:
        super().__init__(code, message, 404)


class ArtifactForbiddenError(ArtifactStorageError):
    def __init__(self, code: str = 'artifact_access_denied', message: str = 'artifact_access_denied') -> None:
        super().__init__(code, message, 403)


class ArtifactValidationError(ArtifactStorageError):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(code, message, status_code)


class ArtifactRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    filename: str = Field(max_length=255)
    content_type: str = Field(max_length=120)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)
    created_at: datetime
    updated_at: datetime
    storage_name: str = Field(max_length=80)
    download_count: int = 0
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    last_downloaded_at: datetime | None = None

    def to_read(self) -> ArtifactRead:
        return ArtifactRead.model_validate(self.model_dump(exclude={'storage_name', 'last_downloaded_at'}))


class ArtifactStorage:
    def __init__(self, root: Path | None = None, max_file_size: int | None = None) -> None:
        project_root = Path(__file__).resolve().parents[3]
        self.root = Path(root) if root is not None else project_root / 'data' / 'artifacts'
        self.private_root = self.root / 'private'
        self.metadata_path = self.root / 'metadata.json'
        self.max_file_size = max_file_size or _DEFAULT_MAX_FILE_SIZE
        self.allowed_extensions = set(_ALLOWED_EXTENSIONS)
        self.allowed_mime_types = set(_ALLOWED_MIME_TYPES)
        self.root.mkdir(parents=True, exist_ok=True)
        self.private_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def default_display_name(filename: str) -> str:
        candidate = Path(filename).name
        if candidate != filename or '..' in Path(filename).parts or '/' in filename or '\\' in filename:
            raise ArtifactValidationError('invalid_filename', 'invalid_filename')
        safe = re.sub(r'[^A-Za-z0-9._-]+', '_', candidate).strip('._')
        if not safe:
            raise ArtifactValidationError('invalid_filename', 'invalid_filename')
        return safe[:255]

    def _ensure_allowed_file(self, filename: str, content_type: str) -> str:
        safe_filename = self.default_display_name(filename)
        suffix = Path(safe_filename).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise ArtifactValidationError('invalid_extension', 'invalid_extension')
        if content_type not in self.allowed_mime_types:
            raise ArtifactValidationError('invalid_mime_type', 'invalid_mime_type')
        return safe_filename

    def _artifact_path(self, storage_name: str) -> Path:
        return self.private_root / storage_name

    def _load_manifest(self) -> dict[str, object]:
        if not self.metadata_path.exists():
            return {'version': 1, 'artifacts': {}}
        with _MANIFEST_LOCK:
            raw = json.loads(self.metadata_path.read_text(encoding='utf-8'))
        if not isinstance(raw, dict):
            return {'version': 1, 'artifacts': {}}
        raw.setdefault('version', 1)
        raw.setdefault('artifacts', {})
        return raw

    def _save_manifest(self, manifest: dict[str, object]) -> None:
        temp_path = self.metadata_path.with_suffix('.json.tmp')
        with _MANIFEST_LOCK:
            temp_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding='utf-8')
            temp_path.replace(self.metadata_path)

    def _read_records(self) -> dict[UUID, ArtifactRecord]:
        manifest = self._load_manifest()
        artifacts = manifest.get('artifacts', {})
        if not isinstance(artifacts, dict):
            return {}
        records: dict[UUID, ArtifactRecord] = {}
        for key, payload in artifacts.items():
            try:
                record = ArtifactRecord.model_validate(payload)
            except Exception:
                continue
            records[UUID(str(key))] = record
        return records

    def _write_records(self, records: dict[UUID, ArtifactRecord]) -> None:
        manifest = {
            'version': 1,
            'artifacts': {str(artifact_id): record.model_dump(mode='json') for artifact_id, record in records.items()},
        }
        self._save_manifest(manifest)

    def _get_record(self, artifact_id: UUID) -> ArtifactRecord:
        record = self._read_records().get(artifact_id)
        if record is None:
            raise ArtifactNotFoundError()
        return record

    def _check_owner(self, record: ArtifactRecord, owner_user_id: UUID, allow_all: bool) -> None:
        if allow_all:
            return
        if record.owner_user_id != owner_user_id:
            raise ArtifactForbiddenError()

    async def save_artifact(
        self,
        upload_file: UploadFile,
        owner_user_id: UUID,
        *,
        max_file_size: int | None = None,
    ) -> ArtifactRecord:
        max_size = max_file_size or self.max_file_size
        if upload_file.filename is None:
            raise ArtifactValidationError('missing_filename', 'missing_filename')
        safe_filename = self._ensure_allowed_file(upload_file.filename, upload_file.content_type or '')
        artifact_id = uuid4()
        storage_name = artifact_id.hex
        blob_path = self._artifact_path(storage_name)
        blob_path.parent.mkdir(parents=True, exist_ok=True)
        hasher = hashlib.sha256()
        size_bytes = 0
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.private_root, prefix=f'{storage_name}.', suffix='.upload')
        temp_path = Path(temp_file.name)
        try:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                size_bytes += len(chunk)
                if size_bytes > max_size:
                    raise ArtifactValidationError('file_too_large', 'file_too_large', 413)
                hasher.update(chunk)
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()
            temp_path.replace(blob_path)
        except ArtifactStorageError:
            temp_file.close()
            temp_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            temp_file.close()
            temp_path.unlink(missing_ok=True)
            raise ArtifactValidationError('artifact_write_failed', 'artifact_write_failed', 500) from exc
        finally:
            try:
                await upload_file.close()
            except Exception:
                pass
        now = datetime.now(UTC)
        record = ArtifactRecord(
            id=artifact_id,
            owner_user_id=owner_user_id,
            filename=safe_filename,
            content_type=upload_file.content_type or 'application/octet-stream',
            size_bytes=size_bytes,
            sha256=hasher.hexdigest(),
            created_at=now,
            updated_at=now,
            storage_name=storage_name,
        )
        records = self._read_records()
        records[artifact_id] = record
        self._write_records(records)
        return record

    async def list_artifacts(self, owner_user_id: UUID, allow_all: bool = False) -> list[ArtifactRecord]:
        records = [record for record in self._read_records().values() if record.deleted_at is None]
        if not allow_all:
            records = [record for record in records if record.owner_user_id == owner_user_id]
        return sorted(records, key=lambda record: (record.created_at, record.id), reverse=True)

    async def get_artifact(self, artifact_id: UUID, owner_user_id: UUID, allow_all: bool = False) -> ArtifactRecord:
        record = self._get_record(artifact_id)
        if record.deleted_at is not None:
            raise ArtifactNotFoundError()
        self._check_owner(record, owner_user_id, allow_all)
        return record

    async def get_artifact_for_token(self, artifact_id: UUID) -> ArtifactRecord:
        record = self._get_record(artifact_id)
        if record.deleted_at is not None:
            raise ArtifactNotFoundError()
        return record

    async def mark_downloaded(self, artifact_id: UUID) -> ArtifactRecord:
        records = self._read_records()
        record = records.get(artifact_id)
        if record is None or record.deleted_at is not None:
            raise ArtifactNotFoundError()
        now = datetime.now(UTC)
        updated = record.model_copy(update={'download_count': record.download_count + 1, 'updated_at': now, 'last_downloaded_at': now})
        records[artifact_id] = updated
        self._write_records(records)
        return updated

    async def delete_artifact(self, artifact_id: UUID, owner_user_id: UUID, allow_all: bool = False) -> ArtifactRecord:
        records = self._read_records()
        record = records.get(artifact_id)
        if record is None or record.deleted_at is not None:
            raise ArtifactNotFoundError()
        self._check_owner(record, owner_user_id, allow_all)
        blob_path = self._artifact_path(record.storage_name)
        blob_path.unlink(missing_ok=True)
        now = datetime.now(UTC)
        updated = record.model_copy(update={'deleted_at': now, 'deleted_by': owner_user_id, 'updated_at': now})
        records[artifact_id] = updated
        self._write_records(records)
        return updated

    @staticmethod
    def public_record(record: ArtifactRecord) -> ArtifactRead:
        return record.to_read()
