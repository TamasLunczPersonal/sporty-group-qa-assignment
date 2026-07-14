"""Framework-facing abstraction for browser interactions.

Page Objects depend on these reusable interaction primitives instead of calling
Selenium directly. Centralising navigation, explicit waits, element lookup,
clicks, text entry, attribute reads, and numeric extraction provides a stable
interaction contract for every page and component.

This design simplifies Selenium upgrades and reduces the scope of changes
required for a future migration to another browser automation framework, such
as Playwright. Framework-specific behaviour remains concentrated in this
layer, the driver setup, and the locator definitions. User-facing assertions
stay in the Page Objects where failures can include business-readable context.
"""
from collections.abc import Callable, Sequence
from decimal import Decimal
import re
from typing import TypeVar

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


Locator = tuple[str, str]
T = TypeVar("T")
MAX_ELEMENT_WAIT_SECONDS = 10.0
POLL_FREQUENCY_SECONDS = 0.2


class BasePage:
    """Low-level browser operations shared by user-facing Page Objects."""

    def __init__(self, driver: WebDriver, timeout_seconds: float = MAX_ELEMENT_WAIT_SECONDS) -> None:
        self._driver = driver
        self.timeout_seconds = min(
            max(float(timeout_seconds), POLL_FREQUENCY_SECONDS),
            MAX_ELEMENT_WAIT_SECONDS,
        )
        self._wait = WebDriverWait(
            driver,
            self.timeout_seconds,
            poll_frequency=POLL_FREQUENCY_SECONDS,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    @property
    def timeout_description(self) -> str:
        """Return a reusable human-readable timeout phrase."""

        return f"within {self.timeout_seconds:g} seconds"

    def open(self, url: str) -> None:
        """Navigate the active browser to ``url``."""

        self._driver.get(url)

    def _wait_until(self, condition: Callable[[WebDriver], T | bool]) -> T | None:
        """Return a successful condition result, or ``None`` after timeout."""

        try:
            return self._wait.until(condition)

        except TimeoutException:
            return None

    def wait_for_document_ready(self) -> bool:
        """Return whether browser navigation reached ``readyState=complete``."""

        result = self._wait_until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

        return result is True

    def _visible_element(self, locator: Locator) -> WebElement | None:
        """Return a visible element for internal framework operations."""

        result = self._wait_until(EC.visibility_of_element_located(locator))

        return result if isinstance(result, WebElement) else None

    def _clickable_element(self, locator: Locator) -> WebElement | None:
        """Return a clickable element for internal framework operations."""

        result = self._wait_until(EC.element_to_be_clickable(locator))

        return result if isinstance(result, WebElement) else None

    def wait_for_visible(self, locator: Locator) -> bool:
        """Return whether an element becomes visible before timeout."""

        return self._visible_element(locator) is not None

    def wait_for_clickable(self, locator: Locator) -> bool:
        """Return whether an element becomes visible and enabled."""

        return self._clickable_element(locator) is not None

    def wait_for_invisible(self, locator: Locator) -> bool:
        """Return whether an element becomes absent or invisible."""

        result = self._wait_until(EC.invisibility_of_element_located(locator))

        return bool(result)

    def press_button(self, locator: Locator) -> bool:
        """Wait for a clickable control, click it, and report success."""

        def _click_when_ready(driver: WebDriver) -> bool:
            try:
                element = EC.element_to_be_clickable(locator)(driver)

                if not isinstance(element, WebElement):
                    return False

                element.click()
                return True

            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
                return False

        return self._wait_until(_click_when_ready) is True

    def replace_text(self, locator: Locator, text: str) -> bool:
        """Set and verify an input value."""

        expected = str(text)

        def _set_value(driver: WebDriver) -> bool:
            try:
                element = EC.element_to_be_clickable(locator)(driver)

                if not isinstance(element, WebElement):
                    return False

                current = element.get_attribute("value") or ""

                if current == expected:
                    return True

                element.click()

                if current:
                    element.send_keys(Keys.CONTROL, "a")
                    element.send_keys(Keys.DELETE)

                if expected:
                    element.send_keys(expected)

                return (element.get_attribute("value") or "") == expected

            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
                return False

        return bool(self._wait_until(_set_value))

    def read_attribute(self, locator: Locator, attribute: str) -> str | None:
        """Return an attribute from a visible element, or ``None`` on timeout."""

        element = self._visible_element(locator)

        if element is None:
            return None

        return element.get_attribute(attribute)

    def wait_for_attribute_value(self, locator: Locator, attribute: str, expected_value: str) -> bool:
        """Wait until a visible element attribute equals the expected value."""

        def _attribute_matches(driver: WebDriver) -> bool:
            try:
                element = driver.find_element(*locator)

            except NoSuchElementException:
                return False

            if not element.is_displayed():
                return False

            return element.get_attribute(attribute) == expected_value

        return self._wait_until(_attribute_matches) is True

    def read_text(self, locator: Locator) -> str | None:
        """Return stripped visible text, or ``None`` when unavailable."""

        element = self._visible_element(locator)

        if element is None:
            return None

        return element.text.strip()

    def wait_for_text_pattern(self, locator: Locator, pattern: str, *, flags: int = 0) -> str | None:
        """Return visible text once it fully matches a regular expression."""

        compiled_pattern = re.compile(pattern, flags)

        def _text_matches(driver: WebDriver) -> str | bool:
            try:
                element = driver.find_element(*locator)

            except NoSuchElementException:
                return False

            if not element.is_displayed():
                return False

            text = element.text.strip()

            return text if compiled_pattern.fullmatch(text) else False

        result = self._wait_until(_text_matches)

        return result if isinstance(result, str) else None

    def wait_for_minimum_element_count(self, locator: Locator, minimum: int = 1) -> int | None:
        """Return the rendered element count once it reaches ``minimum``."""

        if minimum < 1:
            raise ValueError("minimum must be at least 1")

        def _enough_elements(driver: WebDriver) -> int | bool:
            count = len(driver.find_elements(*locator))

            return count if count >= minimum else False

        result = self._wait_until(_enough_elements)

        if isinstance(result, int) and not isinstance(result, bool):
            return result

        return None

    def read_decimal(self, locator: Locator) -> Decimal | None:
        """Return the final decimal-looking value from a visible element."""

        text = self.read_text(locator)
        if text is None:
            return None

        try:
            return self.decimal_from_text(text)

        except ValueError:
            return None

    def wait_for_decimal(self, locator: Locator, expected_value: Decimal | None = None) -> Decimal | None:
        """Wait for a readable decimal, optionally requiring an exact value."""

        expected = (Decimal(str(expected_value)) if expected_value is not None else None)

        def _decimal_is_ready(driver: WebDriver) -> tuple[Decimal] | bool:
            try:
                element = driver.find_element(*locator)

            except NoSuchElementException:
                return False

            if not element.is_displayed():
                return False

            try:
                value = self.decimal_from_text(element.text)

            except ValueError:
                return False

            if expected is not None and value != expected:
                return False

            return (value,)

        result = self._wait_until(_decimal_is_ready)

        if not isinstance(result, tuple) or len(result) != 1:
            return None

        return result[0]

    def wait_for_decimal_values(
            self, locators: Sequence[Locator], expected_value: Decimal) -> tuple[Decimal, ...] | None:
        """Wait until every locator displays the same expected decimal value."""

        if not locators:
            raise ValueError("locators must contain at least one locator")

        expected = Decimal(str(expected_value))

        def _all_decimals_match(driver: WebDriver) -> tuple[Decimal, ...] | bool:
            values: list[Decimal] = []

            for locator in locators:
                try:
                    element = driver.find_element(*locator)

                except NoSuchElementException:
                    return False

                if not element.is_displayed():
                    return False

                try:
                    value = self.decimal_from_text(element.text)

                except ValueError:
                    return False

                if value != expected:
                    return False
                values.append(value)

            return tuple(values)

        result = self._wait_until(_all_decimals_match)

        return result if isinstance(result, tuple) else None

    @staticmethod
    def decimal_from_text(text: str) -> Decimal:
        """Extract the final decimal-looking value from text."""

        matches = re.findall(r"-?\d+(?:[.,]\d+)?", text.replace("\u00a0", " "))

        if not matches:
            raise ValueError(f"No numeric value was found in {text!r}.")

        return Decimal(matches[-1].replace(",", "."))