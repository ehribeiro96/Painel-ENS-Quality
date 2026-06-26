from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from app.services.artifact_signing import ArtifactSigner, ArtifactTokenExpired, ArtifactTokenInvalid
from app.services.artifact_storage import (
    ArtifactForbiddenError,
    ArtifactNotFoundError,
    ArtifactStorage,
    ArtifactValidationError,
)
from starlette.datastructures import UploadFile


class ArtifactSecurityContractTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / 'artifacts'
        self.storage = ArtifactStorage(root=self.root, max_file_size=1024 * 1024)
        self.signer = ArtifactSigner('x' * 64)
        self.owner_id = uuid4()

    async def asyncTearDown(self) -> None:
        self.tempdir.cleanup()

    async def _make_upload(self, filename: str, content: bytes, content_type: str) -> UploadFile:
        import io

        return UploadFile(filename=filename, file=io.BytesIO(content), headers={'content-type': content_type})

    async def test_save_artifact_rejects_path_traversal_extension_and_mime(self) -> None:
        good = await self._make_upload('report.pdf', b'%PDF-1.4 test', 'application/pdf')
        record = await self.storage.save_artifact(good, self.owner_id)
        self.assertEqual(record.filename, 'report.pdf')
        self.assertTrue((self.root / 'private' / record.storage_name).is_file())

        with self.assertRaises(ArtifactValidationError):
            await self.storage.save_artifact(await self._make_upload('../secret.pdf', b'bad', 'application/pdf'), self.owner_id)
        with self.assertRaises(ArtifactValidationError):
            await self.storage.save_artifact(await self._make_upload('secret.exe', b'bad', 'application/octet-stream'), self.owner_id)
        with self.assertRaises(ArtifactValidationError):
            await self.storage.save_artifact(await self._make_upload('secret.pdf', b'bad', 'application/octet-stream'), self.owner_id)

    async def test_save_artifact_enforces_size_limit(self) -> None:
        upload = await self._make_upload('too-large.json', b'{' + b'"x":' + b'"a"' * 4000 + b'}', 'application/json')
        with self.assertRaises(ArtifactValidationError) as ctx:
            await self.storage.save_artifact(upload, self.owner_id, max_file_size=32)
        self.assertEqual(ctx.exception.status_code, 413)

    async def test_access_control_blocks_non_owner_and_admin_override(self) -> None:
        upload = await self._make_upload('safe.json', b'{"ok":true}', 'application/json')
        record = await self.storage.save_artifact(upload, self.owner_id)
        other = uuid4()
        with self.assertRaises(ArtifactForbiddenError):
            await self.storage.get_artifact(record.id, other)
        admin_record = await self.storage.get_artifact(record.id, other, allow_all=True)
        self.assertEqual(admin_record.id, record.id)

    async def test_signed_token_contains_expiration_and_rejects_invalid_or_expired(self) -> None:
        upload = await self._make_upload('signed.txt', b'hello', 'text/plain')
        record = await self.storage.save_artifact(upload, self.owner_id)
        expires_at = datetime.now(UTC) + timedelta(seconds=300)
        token = self.signer.sign_download_token(record.id, record.owner_user_id, expires_at)
        claims = self.signer.verify_download_token(token)
        self.assertEqual(claims.artifact_id, record.id)
        self.assertEqual(claims.owner_user_id, record.owner_user_id)
        self.assertEqual(claims.purpose, 'artifact_download')
        self.assertEqual(int(claims.expires_at.timestamp()), int(expires_at.timestamp()))

        with self.assertRaises(ArtifactTokenInvalid):
            self.signer.verify_download_token(token + 'tamper')
        expired = self.signer.sign_download_token(record.id, record.owner_user_id, datetime.now(UTC) - timedelta(seconds=1))
        with self.assertRaises(ArtifactTokenExpired):
            self.signer.verify_download_token(expired)

    async def test_download_updates_history_without_leaking_internal_paths(self) -> None:
        upload = await self._make_upload('history.txt', b'hello history', 'text/plain')
        record = await self.storage.save_artifact(upload, self.owner_id)
        updated = await self.storage.mark_downloaded(record.id)
        self.assertEqual(updated.download_count, 1)
        self.assertIsNotNone(updated.last_downloaded_at)
        public = updated.to_read().model_dump()
        self.assertNotIn('storage_name', public)
        self.assertNotIn('last_downloaded_at', public)
        self.assertNotIn('private', str(public).lower())
        self.assertNotIn(str(self.root), str(public))

    async def test_delete_removes_blob_and_prevents_future_access(self) -> None:
        upload = await self._make_upload('delete.pdf', b'%PDF-1.4 keep calm', 'application/pdf')
        record = await self.storage.save_artifact(upload, self.owner_id)
        deleted = await self.storage.delete_artifact(record.id, self.owner_id)
        self.assertIsNotNone(deleted.deleted_at)
        self.assertFalse((self.root / 'private' / record.storage_name).exists())
        with self.assertRaises(ArtifactNotFoundError):
            await self.storage.get_artifact_for_token(record.id)


if __name__ == '__main__':
    unittest.main()
