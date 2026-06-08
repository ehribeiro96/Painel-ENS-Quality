from __future__ import annotations

from app.domains.ai_chat.models import AiChatConversation, AiChatMessage  # noqa: F401
from app.domains.assets.models import Asset  # noqa: F401
from app.domains.audit.models import AuditLog  # noqa: F401
from app.domains.auth.models import AuthSession  # noqa: F401
from app.domains.imports.models import (  # noqa: F401
    ImportConflict,
    ImportJob,
    ImportStagingAsset,
    ImportValidationError,
)
from app.domains.macros.models import MacroAutocompleteHint, MacroGeneration, MacroTemplate  # noqa: F401
from app.domains.movements.models import AssetMovement  # noqa: F401
from app.domains.users.models import User  # noqa: F401
from app.shared.models import Base
