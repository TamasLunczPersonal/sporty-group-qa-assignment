"""High-value API business-rule validation."""

from decimal import Decimal
from sporty_qa.api_client import BettingApiClient
from sporty_qa.step_reporter import StepReporter

import pytest
import requests


def _response_summary(response: requests.Response) -> str:
    """Return concise response diagnostics without dumping request headers."""

    body = response.text.strip()
    if len(body) > 500:
        body = f"{body[:500]}... [truncated]"

    return (
        f"HTTP {response.status_code}; "
        f"content-type={response.headers.get('content-type', 'unknown')}; "
        f"body={body or '<empty>'}"
    )


@pytest.mark.api
def test_invalid_selection_is_rejected_without_balance_change(
        api_client: BettingApiClient, steps: StepReporter) -> None:
    """Server-side validation protects balance when the UI is bypassed."""

    with steps.step("Reset the test account balance"):
        reset_response = api_client.reset_balance()

        assert reset_response.status_code == 200, (
            "Test precondition failed: the account balance could not be reset. "
            f"Expected HTTP 200, received {_response_summary(reset_response)}"
        )

    with steps.step("Read the initial balance and an upcoming match"):
        balance_before, currency_before = api_client.get_balance()
        match = api_client.get_upcoming_match()

        assert currency_before == "EUR", (
            "Test precondition failed: the account currency was expected to be "
            f"EUR, but was {currency_before!r}."
        )

    with steps.step("Submit a bet with an invalid selection"):
        response = api_client.place_bet(
            match_id=str(match["id"]),
            selection="INVALID",
            stake=Decimal("10.00"),
        )

    with steps.step("Verify the API rejects the invalid selection with HTTP 422"):
        assert response.status_code == 422, (
            "Invalid selection was not rejected with the expected validation "
            f"status. Expected HTTP 422, received {_response_summary(response)}"
        )

    with steps.step("Verify the rejected bet did not change account state"):
        balance_after, currency_after = api_client.get_balance()

        assert currency_after == "EUR", (
            "Account currency changed or became invalid after the rejected bet. "
            f"Expected 'EUR', but received {currency_after!r}."
        )
        assert balance_after == balance_before, (
            "Rejected bet changed the account balance. "
            f"Expected the balance to remain {balance_before} EUR, "
            f"but it became {balance_after} EUR."
        )
