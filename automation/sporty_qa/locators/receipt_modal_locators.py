"""DOM-backed locators for :class:`ReceiptModal`.

The success-receipt DOM exposes stable IDs for the modal root, values, and
buttons. Those IDs are preferred over text-based or ancestor XPath selectors.
"""

from typing import TypeAlias

from selenium.webdriver.common.by import By


Locator: TypeAlias = tuple[str, str]


class ReceiptModalLocators:
    """Success-receipt locators grouped by UI element type."""

    class Containers:
        """Modal containers."""
        ROOT: Locator = (By.ID, "modal-success")
        PANEL: Locator = (By.CSS_SELECTOR, "#modal-success .modalPanel")
        SUMMARY: Locator = (By.CSS_SELECTOR, "#modal-success .modalSummary")

    class Headings:
        """Modal headings."""
        SUCCESS: Locator = (By.CSS_SELECTOR, "#modal-success .modalTitle")

    class Values:
        """Receipt values exposed through stable DOM IDs."""
        BET_ID: Locator = (By.ID, "modal-success-bet-id")
        MATCH: Locator = (By.ID, "modal-success-match")
        STAKE: Locator = (By.ID, "modal-success-stake")
        ODDS: Locator = (By.ID, "modal-success-odds")
        POTENTIAL_PAYOUT: Locator = (By.ID, "modal-success-payout")
        PLACED_AT: Locator = (By.ID, "modal-success-placed-at")

    class Buttons:
        """Receipt action buttons."""
        CLOSE: Locator = (By.ID, "modal-success-close")
        CLOSE_ICON: Locator = (By.ID, "modal-success-close-x")
