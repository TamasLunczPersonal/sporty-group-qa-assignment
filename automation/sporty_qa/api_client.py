"""Small API client used for test setup and direct API validation."""

from datetime import date
from decimal import Decimal
from typing import Any

import requests


class BettingApiClient:
    """Wrap the assignment API and keep authentication in one place."""

    def __init__(self, base_url: str, user_id: str, timeout_seconds: float = 12) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-user-id": user_id,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def close(self) -> None:
        self.session.close()

    def reset_balance(self) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/reset-balance",
            timeout=self.timeout_seconds,
        )

    def get_balance_response(self) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/balance",
            timeout=self.timeout_seconds,
        )

    def get_balance(self) -> tuple[Decimal, str]:
        response = self.get_balance_response()
        response.raise_for_status()
        payload = response.json()
        return Decimal(str(payload["balance"])), str(payload["currency"])

    def get_matches(self) -> list[dict[str, Any]]:
        response = self.session.get(
            f"{self.base_url}/api/matches",
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise AssertionError(
                f"Expected /api/matches to return a list, got: {type(payload).__name__}"
            )
        return payload

    def get_upcoming_match(self, on_or_after: date | None = None) -> dict[str, Any]:
        """Return the earliest catalogue match that is not before the reference date."""

        reference_date = on_or_after or date.today()
        upcoming: list[dict[str, Any]] = []

        for match in self.get_matches():

            try:
                kickoff = date.fromisoformat(str(match["kickoffDate"]))

            except (KeyError, TypeError, ValueError):
                continue

            if kickoff >= reference_date:
                upcoming.append(match)

        if not upcoming:
            raise AssertionError(
                f"No upcoming match exists in the catalogue on or after {reference_date}."
            )

        return min(upcoming, key=lambda match: str(match["kickoffDate"]))

    def place_bet(self, *, match_id: str, selection: str, stake: Decimal | float | str) -> requests.Response:

        return self.session.post(
            f"{self.base_url}/api/place-bet",
            json={
                "matchId": match_id,
                "selection": selection,
                "stake": float(Decimal(str(stake))),
            },
            timeout=self.timeout_seconds,
        )
