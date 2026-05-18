"""Typed Annotated dependency aliases used by route handlers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.services.ai_providers import AiProvider
from app.services.ai_providers.factory import get_provider

DbSession = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_ai_provider(settings: SettingsDep) -> AiProvider:
    """Default provider builder — tests override via dependency_overrides."""
    return get_provider(settings)


AiProviderDep = Annotated[AiProvider, Depends(get_ai_provider)]
