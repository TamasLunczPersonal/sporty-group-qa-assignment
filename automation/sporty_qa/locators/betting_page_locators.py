"""DOM-backed locators for :class:`BettingPage`.

Stable IDs from the supplied initial and selected-bet DOM states are used
whenever available. Locators are grouped by UI element type.
"""

from typing import TypeAlias
from selenium.webdriver.common.by import By


Locator: TypeAlias = tuple[str, str]


class BettingPageLocators:
    """Locators grouped by semantic UI element type."""

    class Containers:
        """Top-level page and component containers."""
        APP_SHELL: Locator = (By.ID, "app-shell")
        MAIN_CONTENT: Locator = (By.ID, "main-content")
        MATCH_SECTION: Locator = (By.ID, "match-section")
        MATCH_LIST: Locator = (By.ID, "match-list")
        BET_SLIP_ASIDE: Locator = (By.ID, "bet-slip-aside")
        BET_SLIP: Locator = (By.ID, "bet-slip")
        BET_SLIP_HEADER: Locator = (By.ID, "bet-slip-header")

    class LoadingIndicators:
        """Asynchronous loading indicators."""
        MATCH_LIST: Locator = (By.ID, "match-list-loading")

    class Texts:
        """Read-only text elements."""
        APP_TITLE: Locator = (By.ID, "header-title")
        MATCH_LIST_TITLE: Locator = (By.ID, "match-list-title")
        MATCH_LIST_COUNT: Locator = (By.ID, "match-list-count")
        HEADER_BALANCE: Locator = (By.ID, "header-balance")
        BET_SLIP_TITLE: Locator = (By.ID, "bet-slip-title")
        BET_SLIP_COUNT: Locator = (By.ID, "bet-slip-count")
        BET_SLIP_BALANCE: Locator = (By.ID, "bet-slip-balance")
        EMPTY_BET_SLIP_MESSAGE: Locator = (By.CSS_SELECTOR, "#bet-slip .betSlipBodyEmpty")
        SELECTED_MATCH: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
        SELECTED_MARKET: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionMarket")
        SELECTED_ODDS: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionOdds")

    class Fields:
        """Editable form controls."""
        STAKE: Locator = (By.ID, "bet-slip-stake-input")

    class Values:
        """Calculated values."""
        TOTAL_STAKE: Locator = (By.ID, "bet-slip-total-stake")
        POTENTIAL_PAYOUT: Locator = (By.ID, "bet-slip-potential-payout")

    class Buttons:
        """Static and dynamic action buttons."""
        DATE_FILTER_TOGGLE: Locator = (By.ID, "date-filter-toggle")
        PREVIOUS_MONTH: Locator = (By.ID, "prev-month")
        NEXT_MONTH: Locator = (By.ID, "next-month")
        RESET_DATE: Locator = (By.ID, "reset-date")
        CANCEL_DATE: Locator = (By.ID, "cancel-date")
        APPLY_DATE: Locator = (By.ID, "apply-date")
        ODDS_FILTER_TOGGLE: Locator = (By.ID, "odds-filter-toggle")
        REMOVE_ALL_SELECTIONS: Locator = (By.ID, "bet-slip-remove-all")
        REMOVE_SELECTION: Locator = (By.ID, "bet-slip-selection-remove")
        PLACE_BET: Locator = (By.ID, "bet-slip-place-bet")

        _OUTCOME_SUFFIX = {
            "HOME": "home",
            "DRAW": "draw",
            "AWAY": "away",
        }

        @classmethod
        def outcome(cls, match_id: str, selection: str) -> Locator:
            """Return the exact odds-button ID for a match and selection."""
            normalized_selection = selection.upper()

            try:
                suffix = cls._OUTCOME_SUFFIX[normalized_selection]

            except KeyError as exc:
                raise ValueError(
                    f"Unsupported UI selection: {selection!r}. "
                    "Expected HOME, DRAW, or AWAY."
                ) from exc

            return By.ID, f"odds-{match_id}-{suffix}"

    class MatchCards:
        """Static match-card collection and dynamic match locators."""
        ALL: Locator = (By.CSS_SELECTOR, "#match-list .matchCard[id^='match-card-']")
        TEAM_NAMES: Locator = (By.CSS_SELECTOR, ".teamName")
        ODDS_VALUES: Locator = (By.CSS_SELECTOR, ".oddsButtonValue")

        @staticmethod
        def card(match_id: str) -> Locator:
            """Return the exact card ID generated from the API match ID."""
            return By.ID, f"match-card-{match_id}"
