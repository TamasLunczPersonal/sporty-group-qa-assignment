"""Runtime configuration for local and CI test execution."""

from dataclasses import dataclass
from urllib.parse import urlencode

import os


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


_PLACEHOLDER_USER_IDS = {
    "replace-with-the-assigned-candidate-user-id",
    "<assigned-candidate-user-id>",
}


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _validate_user_id(value: str | None) -> str:
    """Validate the externally supplied candidate identifier."""

    resolved = (value or "").strip()

    if not resolved:
        raise ConfigurationError("USER_ID is required.")

    if resolved.casefold() in {item.casefold() for item in _PLACEHOLDER_USER_IDS}:
        raise ConfigurationError(
            "USER_ID still contains the example placeholder. "
            "Replace it with the assigned candidate user ID."
        )

    return resolved

def _validate_base_url(value: str | None) -> str:
    if not value:
        raise ValueError("BASE_URL is required.")
    return value.rstrip("/")


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings for UI and API tests."""

    base_url: str
    user_id: str
    timeout_seconds: float
    headless: bool

    @classmethod
    def from_sources(cls, *, user_id: str | None = None) -> "Settings":
        """Build settings after pytest has loaded external configuration."""

        return cls(
            base_url=_validate_base_url(os.getenv("BASE_URL")),
            user_id=_validate_user_id(user_id or os.getenv("USER_ID")),
            timeout_seconds=float(os.getenv("TEST_TIMEOUT_SECONDS", "12")),
            headless=_as_bool(os.getenv("HEADLESS", "true")),
        )

    @property
    def app_url(self) -> str:
        # Required by the assignment contract. Real passwords, API keys, and
        # bearer tokens must never be passed through URL query parameters.
        return f"{self.base_url}/?{urlencode({'user-id': self.user_id})}"
