from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID


class ArtifactTokenError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ArtifactTokenExpired(ArtifactTokenError):
    def __init__(self, message: str = 'artifact_download_token_expired') -> None:
        super().__init__('artifact_download_token_expired', message, 410)


class ArtifactTokenInvalid(ArtifactTokenError):
    def __init__(self, message: str = 'artifact_download_token_invalid') -> None:
        super().__init__('artifact_download_token_invalid', message, 403)


@dataclass(frozen=True)
class ArtifactDownloadClaims:
    artifact_id: UUID
    owner_user_id: UUID
    expires_at: datetime
    purpose: str = 'artifact_download'


def _b64encode_json(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    return base64.urlsafe_b64encode(encoded).decode('ascii').rstrip('=')


def _b64decode_json(value: str) -> dict[str, object]:
    padding = '=' * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode((value + padding).encode('ascii'))
    payload = json.loads(decoded.decode('utf-8'))
    if not isinstance(payload, dict):
        raise ArtifactTokenInvalid()
    return payload


class ArtifactSigner:
    def __init__(self, secret: str, api_prefix: str = '/api/v1') -> None:
        normalized_secret = secret.strip()
        if not normalized_secret:
            raise ArtifactTokenInvalid('artifact_signature_secret_missing')
        self.secret = normalized_secret.encode('utf-8')
        self.api_prefix = api_prefix.rstrip('/')

    def _sign_payload(self, payload_b64: str) -> str:
        return hmac.new(self.secret, payload_b64.encode('ascii'), hashlib.sha256).hexdigest()

    def sign_download_token(
        self,
        artifact_id: UUID,
        owner_user_id: UUID,
        expires_at: datetime,
    ) -> str:
        expires_utc = expires_at if expires_at.tzinfo is not None else expires_at.replace(tzinfo=UTC)
        payload = {
            'artifact_id': str(artifact_id),
            'owner_user_id': str(owner_user_id),
            'exp': int(expires_utc.timestamp()),
            'purpose': 'artifact_download',
        }
        payload_b64 = _b64encode_json(payload)
        signature = self._sign_payload(payload_b64)
        return f'{payload_b64}.{signature}'

    def verify_download_token(self, token: str) -> ArtifactDownloadClaims:
        if '.' not in token:
            raise ArtifactTokenInvalid()
        payload_b64, signature = token.split('.', 1)
        expected_signature = self._sign_payload(payload_b64)
        if not hmac.compare_digest(signature, expected_signature):
            raise ArtifactTokenInvalid()
        payload = _b64decode_json(payload_b64)
        try:
            artifact_id = UUID(str(payload['artifact_id']))
            owner_user_id = UUID(str(payload['owner_user_id']))
            expires_at = datetime.fromtimestamp(int(payload['exp']), tz=UTC)
            purpose = str(payload['purpose'])
        except Exception as exc:  # noqa: BLE001 - token parsing must map to invalid token
            raise ArtifactTokenInvalid() from exc
        if purpose != 'artifact_download':
            raise ArtifactTokenInvalid()
        if datetime.now(UTC) >= expires_at:
            raise ArtifactTokenExpired()
        return ArtifactDownloadClaims(
            artifact_id=artifact_id,
            owner_user_id=owner_user_id,
            expires_at=expires_at,
            purpose=purpose,
        )

    def build_download_url(self, token: str) -> str:
        return f'{self.api_prefix}/artifacts/download/{token}'
