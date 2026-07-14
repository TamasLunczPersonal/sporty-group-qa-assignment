"""Critical single-bet UI journey."""

from decimal import Decimal
from sporty_qa.api_client import BettingApiClient
from sporty_qa.config import Settings
from sporty_qa.pages.betting_page import BettingPage
from sporty_qa.step_reporter import StepReporter

import re
import pytest


def _normalise(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip().casefold()


@pytest.mark.ui
def test_single_bet_receipt_and_balance_are_financially_consistent(
        browser, api_client: BettingApiClient, settings: Settings, steps: StepReporter) -> None:
    """Automate the core revenue journey and its highest financial risks."""

    with steps.step("Reset the test account balance through the API"):
        reset_response = api_client.reset_balance()

        assert reset_response.status_code == 200, (
            "Test precondition failed: the account balance could not be reset. "
            f"Expected HTTP 200, got HTTP {reset_response.status_code}: "
            f"{reset_response.text[:500]}"
        )

    with steps.step("Read the persisted balance and select an upcoming match"):
        # Persisted state is the executable precondition. The manual report
        # separately documents the reset-response inconsistency.
        balance_before, currency = api_client.get_balance()

        assert currency == "EUR", (
            "Test precondition failed: the account currency must be EUR. "
            f"Received {currency!r}."
        )

        match = api_client.get_upcoming_match()
        home_team = str(match["homeTeam"])
        away_team = str(match["awayTeam"])
        selection = "HOME"
        stake = Decimal("10.00")
        expected_api_odds = Decimal(str(match["odds"]["home"]))

        assert balance_before >= stake, (
            "Test precondition failed: available balance is too low for the "
            f"test stake. Balance={balance_before} EUR, stake={stake} EUR."
        )

    with steps.step("Open the betting page and wait for account data"):
        page = BettingPage(browser, settings.timeout_seconds).load(
            settings.app_url,
            expected_balance=balance_before,
        )

    with steps.step("Verify the initial UI balance against the API"):
        ui_balance_before = page.balance()

        assert ui_balance_before == balance_before, (
            "UI/API balance mismatch before bet placement. "
            f"API balance={balance_before} EUR, UI balance={ui_balance_before} EUR."
        )

    with steps.step(f"Select the HOME outcome for {home_team} vs {away_team}"):
        selected_odds = page.select_outcome(
            match_id=str(match["id"]),
            selection=selection,
        )
        assert selected_odds == expected_api_odds, (
            "Selected UI odds do not match the API catalogue. "
            f"Expected {expected_api_odds}, got {selected_odds}."
        )

    with steps.step(f"Enter a stake of EUR {stake:.2f}"):
        page.set_stake(stake)

    with steps.step("Verify the pre-placement potential payout"):
        expected_payout = stake * selected_odds
        actual_preview_payout = page.potential_payout(expected_payout)

        assert actual_preview_payout == expected_payout, (
            "Pre-placement payout is incorrect. "
            f"Expected {stake} × {selected_odds} = {expected_payout:.2f} EUR, "
            f"but the UI displayed {actual_preview_payout:.2f} EUR."
        )

    with steps.step("Place the single bet and wait for the success receipt"):
        receipt = page.place_bet()

    expected_match = f"{home_team} vs {away_team}"

    with steps.soft_step("Validate the receipt Bet ID format") as check:
        receipt_bet_id = receipt.bet_id()
        check.that(
            re.fullmatch(
                r"#?B-\d+",
                receipt_bet_id,
                flags=re.IGNORECASE,
            )
            is not None,
            f"Receipt Bet ID has an unexpected format: {receipt_bet_id!r}.",
        )

    with steps.soft_step("Validate the receipt match order") as check:
        receipt_match = receipt.match()
        check.that(
            _normalise(receipt_match) == _normalise(expected_match),
            f"Receipt match mismatch: expected {expected_match!r}, "
            f"got {receipt_match!r}.",
        )

    with steps.soft_step("Validate the selected outcome on the receipt") as check:
        receipt_selection = receipt.selection()
        check.that(
            _normalise(receipt_selection) == _normalise(selection),
            f"Receipt selection mismatch: expected {selection!r}, "
            f"got {receipt_selection!r}.",
        )

    with steps.soft_step("Validate the receipt stake") as check:
        receipt_stake = receipt.stake()
        check.that(
            receipt_stake == stake,
            f"Receipt stake mismatch: expected {stake:.2f}, "
            f"got {receipt_stake:.2f}.",
        )

    with steps.soft_step("Validate the receipt odds") as check:
        receipt_odds = receipt.odds()
        check.that(
            receipt_odds == selected_odds,
            f"Receipt odds mismatch: expected {selected_odds}, "
            f"got {receipt_odds}.",
        )

    with steps.soft_step("Validate the receipt potential payout") as check:
        receipt_payout = receipt.payout()
        check.that(
            receipt_payout == expected_payout,
            f"Receipt payout mismatch: expected {expected_payout:.2f}, "
            f"got {receipt_payout:.2f}.",
        )

    with steps.soft_step("Validate the receipt placement timestamp") as check:
        placed_at = receipt.placed_at()
        check.that(
            re.search(r"\b\d{1,2}:\d{2}\b", placed_at) is not None,
            f"Receipt has no recognisable placement timestamp: {placed_at!r}.",
        )

    with steps.step("Close the success receipt"):
        receipt.close()

    with steps.soft_step("Validate the UI balance after bet placement") as check:
        expected_balance_after = balance_before - stake
        actual_balance_after = page.balance()
        check.that(
            actual_balance_after == expected_balance_after,
            "UI balance did not update after placement: "
            f"expected {expected_balance_after:.2f}, "
            f"got {actual_balance_after:.2f}.",
        )

    steps.assert_no_failures()
