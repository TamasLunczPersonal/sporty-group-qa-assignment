"""Page Object for the single-bet placement screen."""

from decimal import Decimal
from sporty_qa.locators.betting_page_locators import BettingPageLocators
from sporty_qa.pages.base_page import BasePage
from sporty_qa.pages.receipt_modal import ReceiptModal

import re


class BettingPage(BasePage):
    """Expose business-level actions through shared browser primitives."""

    locators = BettingPageLocators

    def load(self, app_url: str, *, expected_balance: Decimal | None = None) -> "BettingPage":
        """Open the SPA and verify that asynchronous data has loaded."""

        self.open(app_url)

        assert self.wait_for_document_ready(), (
            "The betting page did not finish browser-level loading "
            f"{self.timeout_description}."
        )

        assert self.wait_for_visible(self.locators.Texts.MATCH_LIST_TITLE), (
            "The 'Upcoming Football Matches' title was not found "
            f"{self.timeout_description}."
        )

        assert self.wait_for_visible(self.locators.Containers.MATCH_LIST), (
            "The match list container was not found "
            f"{self.timeout_description}."
        )

        assert self.wait_for_invisible(self.locators.LoadingIndicators.MATCH_LIST), (
            "The match list loading indicator did not disappear "
            f"{self.timeout_description}."
        )

        self.wait_for_match_catalogue()

        if expected_balance is not None:
            self.wait_until_balance(expected_balance)

        return self

    def wait_for_match_catalogue(self) -> int:
        """Verify that count and rendered cards both contain loaded data."""

        count_text = self.wait_for_text_pattern(
            self.locators.Texts.MATCH_LIST_COUNT,r"Showing\s+(\d+)\s+matches"
        )

        assert count_text is not None, (
            "The match count did not show a valid 'Showing N matches' value "
            f"{self.timeout_description}."
        )

        match = re.fullmatch(r"Showing\s+(\d+)\s+matches", count_text)

        assert match is not None, (
            "The match count text could not be parsed even though it matched "
            f"the expected format. Displayed text: {count_text!r}."
        )

        reported_count = int(match.group(1))

        assert reported_count > 0, (
            "The match catalogue reported zero available matches."
        )

        rendered_count = self.wait_for_minimum_element_count(self.locators.MatchCards.ALL, minimum=1)

        assert rendered_count is not None, (
            "The match catalogue did not finish loading with at least one "
            f"rendered match card {self.timeout_description}."
        )

        return reported_count

    def wait_until_balance(self, expected_balance: Decimal) -> Decimal:
        """Verify that both initial balance locations show the API value."""

        expected = Decimal(str(expected_balance))
        balances = self.wait_for_decimal_values(
            (
                self.locators.Texts.HEADER_BALANCE,
                self.locators.Texts.BET_SLIP_BALANCE
            ),
            expected,
        )
        assert balances is not None, (
            "The header and bet-slip balances did not update to "
            f"{expected} EUR {self.timeout_description}."
        )

        return expected

    def balance(self) -> Decimal:
        """Read the current header balance."""

        value = self.wait_for_decimal(self.locators.Texts.HEADER_BALANCE)

        assert value is not None, (
            "The header balance was not found or did not contain a readable "
            f"numeric value {self.timeout_description}."
        )

        return value

    def select_outcome(self, *, match_id: str, selection: str) -> Decimal:
        """Select one exact outcome by the stable match and button IDs."""

        assert self.wait_for_visible(self.locators.MatchCards.card(match_id)), (
            f"The match card with ID '{match_id}' was not found "
            f"{self.timeout_description}."
        )

        outcome_locator = self.locators.Buttons.outcome(match_id, selection)
        odds = self.wait_for_decimal(outcome_locator)

        assert odds is not None, (
            f"The '{selection.upper()}' odds button for match '{match_id}' "
            "was not found or did not contain readable odds "
            f"{self.timeout_description}."
        )

        assert self.press_button(outcome_locator), (
            f"The '{selection.upper()}' odds button for match '{match_id}' "
            "was not clickable "
            f"{self.timeout_description}."
        )

        assert self.wait_for_visible(self.locators.Fields.STAKE), (
            "The 'Stake' input field did not appear after selecting the "
            f"'{selection.upper()}' outcome for match '{match_id}' "
            f"{self.timeout_description}."
        )

        return odds

    def set_stake(self, stake: Decimal | str) -> None:
        """Enter a stake into the selected bet."""

        stake_text = str(stake)

        assert self.replace_text(self.locators.Fields.STAKE, stake_text), (
            "The 'Stake' input field was not found or did not retain the "
            f"entered value {stake_text!r} {self.timeout_description}."
        )

    def potential_payout(self, expected_payout: Decimal | None = None) -> Decimal:
        """Read the payout, optionally waiting for an expected calculation."""

        expected = Decimal(str(expected_payout)) if expected_payout is not None else None

        value = self.wait_for_decimal(
            self.locators.Values.POTENTIAL_PAYOUT,
            expected
        )

        if expected is None:
            assert value is not None, (
                "The 'Potential Payout' value was not found or was not readable "
                f"{self.timeout_description}."
            )

        else:
            assert value is not None, (
                "The 'Potential Payout' value did not update to "
                f"{expected} EUR {self.timeout_description}."
            )

        return value

    def place_bet(self) -> ReceiptModal:
        """Submit the selected bet and return its success receipt."""

        assert self.press_button(self.locators.Buttons.PLACE_BET), (
            "The 'Place Bet' button was not found or remained disabled "
            f"{self.timeout_description}."
        )

        return ReceiptModal(self)