"""Success receipt component object."""

from decimal import Decimal
from sporty_qa.locators.receipt_modal_locators import ReceiptModalLocators
from sporty_qa.pages.base_page import BasePage, Locator

import re


class ReceiptModal:
    """Represent the successful bet receipt modal."""

    locators = ReceiptModalLocators
    EXPECTED_HEADING = "Bet Placed Successfully!"

    def __init__(self, page: BasePage) -> None:
        self.page = page

        assert page.wait_for_visible(self.locators.Containers.ROOT), (
            "The success receipt modal with ID 'modal-success' did not appear "
            f"{page.timeout_description} after placing the bet."
        )

        heading = page.read_text(self.locators.Headings.SUCCESS)
        assert heading is not None, (
            "The success receipt heading was not found inside the "
            f"'modal-success' dialog {page.timeout_description}."
        )
        assert heading == self.EXPECTED_HEADING, (
            "Unexpected success receipt heading. "
            f"Expected {self.EXPECTED_HEADING!r}, got {heading!r}."
        )

    @property
    def text(self) -> str:
        """Return all visible text from the receipt modal."""

        value = self.page.read_text(self.locators.Containers.ROOT)

        assert value is not None, (
            "The success receipt modal text could not be read "
            f"{self.page.timeout_description}."
        )

        return value

    def _text(self, locator: Locator, element_name: str) -> str:
        value = self.page.read_text(locator)

        assert value is not None, (
            f"The '{element_name}' element was not found in the success receipt "
            f"{self.page.timeout_description}."
        )

        assert value, (
            f"The '{element_name}' element was present in the success receipt "
            "but contained no visible text."
        )

        return value

    def _decimal(self, locator: Locator, element_name: str) -> Decimal:
        value = self.page.wait_for_decimal(locator)

        assert value is not None, (
            f"The '{element_name}' value in the success receipt was not found "
            "or did not contain a readable number "
            f"{self.page.timeout_description}."
        )

        return value

    def bet_id(self) -> str:
        """Return the displayed bet identifier."""

        return self._text(self.locators.Values.BET_ID, "Bet ID")

    def match(self) -> str:
        """Return the displayed match name."""

        return self._text(self.locators.Values.MATCH, "Match")

    def stake(self) -> Decimal:
        """Return the displayed stake."""

        return self._decimal(self.locators.Values.STAKE, "Stake")

    def odds(self) -> Decimal:
        """Return the displayed odds."""

        return self._decimal(self.locators.Values.ODDS, "Odds")

    def payout(self) -> Decimal:
        """Return the displayed potential payout."""

        return self._decimal(self.locators.Values.POTENTIAL_PAYOUT, "Potential Payout")

    def placed_at(self) -> str:
        """Return the displayed placement timestamp text."""

        return self._text(self.locators.Values.PLACED_AT, "Placed At")

    def selection(self) -> str | None:
        """Return the selected outcome when the receipt exposes it."""

        match = re.search(
            r"Match Winner:\s*(Home|Draw|Away)",
            self.text,
            flags=re.IGNORECASE,
        )
        return match.group(1) if match else None

    def close(self) -> None:
        """Close the receipt and verify that the modal disappears."""

        assert self.page.press_button(self.locators.Buttons.CLOSE), (
            "The 'Close' button with ID 'modal-success-close' was not found "
            "or was not clickable in the success receipt "
            f"{self.page.timeout_description}."
        )

        assert self.page.wait_for_invisible(self.locators.Containers.ROOT), (
            "The success receipt modal did not disappear after clicking "
            f"'Close' {self.page.timeout_description}."
        )