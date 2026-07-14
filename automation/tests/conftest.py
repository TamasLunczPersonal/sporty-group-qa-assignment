"""Shared pytest configuration and fixtures for UI and API tests."""

from contextlib import nullcontext
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from sporty_qa.api_client import BettingApiClient
from sporty_qa.config import ConfigurationError, Settings
from sporty_qa.step_reporter import StepReporter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import sys
import pytest


ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
_SETTINGS_KEY = pytest.StashKey[Settings]()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Expose optional runtime configuration through standard pytest CLI options."""

    group = parser.getgroup("sporty assignment")
    group.addoption(
        "--user-id",
        action="store",
        default=None,
        help=(
            "Assigned candidate USER_ID. When omitted, pytest uses USER_ID from "
            "the environment/.env or prompts in an interactive terminal."
        ),
    )


def _prompt_for_user_id(config: pytest.Config) -> str:
    """Prompt interactively while temporarily disabling pytest output capture."""

    if not sys.stdin.isatty():
        raise pytest.UsageError(
            "USER_ID is not configured and the current session is non-interactive. "
            "Set USER_ID in the environment/.env or run pytest with --user-id."
        )

    capture_manager = config.pluginmanager.getplugin("capturemanager")
    capture_context = (
        capture_manager.global_and_fixture_disabled()
        if capture_manager is not None
        else nullcontext()
    )

    with capture_context:
        value = input("Enter the assigned USER_ID: ").strip()

    if not value:
        raise pytest.UsageError("USER_ID cannot be empty.")

    return value


def pytest_configure(config: pytest.Config) -> None:
    """Load project-root .env, then resolve configuration before collection."""

    env_path = config.rootpath / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    cli_user_id = config.getoption("--user-id")
    configured_user_id = cli_user_id or os.getenv("USER_ID")
    user_id = configured_user_id.strip() if configured_user_id else None

    if not user_id:
        if sys.stdin.isatty():
            user_id = _prompt_for_user_id(config)
        else:
            raise pytest.UsageError(
                "USER_ID is not configured. Create "
                f"{env_path} with USER_ID=<assigned-candidate-user-id>, "
                "set USER_ID in the environment, or run pytest with --user-id."
            )

    try:
        config.stash[_SETTINGS_KEY] = Settings.from_sources(user_id=user_id)
    except ConfigurationError as exc:
        raise pytest.UsageError(f"Configuration error in {env_path}: {exc}") from None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    """Expose each test phase result to fixtures during teardown."""

    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return pytestconfig.stash[_SETTINGS_KEY]


@pytest.fixture
def steps(pytestconfig: pytest.Config) -> StepReporter:
    """Provide visible numbered steps and aggregated soft validations."""

    return StepReporter(pytestconfig)


@pytest.fixture
def api_client(settings: Settings):
    client = BettingApiClient(
        base_url=settings.base_url, user_id=settings.user_id, timeout_seconds=settings.timeout_seconds
    )

    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def browser(request: pytest.FixtureRequest, settings: Settings):
    options = Options()

    if settings.headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.timeout_seconds)

    try:
        yield driver

    finally:
        call_report = getattr(request.node, "rep_call", None)

        if call_report and call_report.failed:
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
            driver.save_screenshot(str(ARTIFACTS_DIR / f"{safe_name}.png"))
            (ARTIFACTS_DIR / f"{safe_name}.html").write_text(
                driver.page_source,
                encoding="utf-8",
            )
        driver.quit()
