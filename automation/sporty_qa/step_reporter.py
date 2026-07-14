"""Lightweight pytest step reporting without an external reporting plugin."""

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

import pytest


@dataclass(frozen=True)
class StepFailure:
    """A failed soft-validation step collected for the final pytest failure."""

    number: int
    title: str
    messages: tuple[str, ...]


@dataclass
class SoftStep:
    """Collect one or more business-validation failures inside a test step."""

    messages: list[str] = field(default_factory=list)

    def that(self, condition: bool, message: str) -> None:
        """Record a readable failure message when a condition is false."""

        if not condition:
            self.messages.append(message)


class StepReporter:
    """Display pytest steps and retain soft business-validation failures."""

    def __init__(self, pytestconfig: pytest.Config) -> None:
        self._pytestconfig = pytestconfig
        self._step_number = 0
        self._failures: list[StepFailure] = []

    def _next_step(self) -> int:
        self._step_number += 1
        return self._step_number

    def _emit(self, message: str) -> None:
        """Write immediately, including under pytest/PyCharm output capture."""

        terminal_reporter = self._pytestconfig.pluginmanager.get_plugin("terminalreporter")

        if terminal_reporter is not None:
            terminal_reporter.write_line(message)
            return

        capture_manager = self._pytestconfig.pluginmanager.get_plugin("capturemanager")

        if capture_manager is None:
            print(message, flush=True)
            return

        with capture_manager.global_and_fixture_disabled():
            print(message, flush=True)

    @staticmethod
    def _label(number: int, status: str, title: str) -> str:
        return f"[STEP {number:02d}] {status:<5} | {title}"

    @contextmanager
    def step(self, title: str) -> Iterator[None]:
        """Run a hard step that stops the test and names the failed step."""

        number = self._next_step()
        self._emit(self._label(number, "START", title))

        try:
            yield

        except Exception as exc:
            self._emit(self._label(number, "FAIL", title))

            raise AssertionError(
                f"STEP {number:02d} FAILED: {title}\n{exc}"
            ) from exc

        self._emit(self._label(number, "PASS", title))

    @contextmanager
    def soft_step(self, title: str) -> Iterator[SoftStep]:
        """Run a validation step, record failures, and continue the journey."""

        number = self._next_step()
        validation = SoftStep()
        self._emit(self._label(number, "START", title))

        try:
            yield validation

        except Exception as exc:
            validation.messages.append(
                f"Step execution failed with {type(exc).__name__}: {exc}"
            )

        if validation.messages:
            self._failures.append(
                StepFailure(
                    number=number,
                    title=title,
                    messages=tuple(validation.messages),
                )
            )
            self._emit(self._label(number, "FAIL", title))
            return

        self._emit(self._label(number, "PASS", title))

    def assert_no_failures(self) -> None:
        """Fail pytest once with all failed step numbers and messages."""

        if not self._failures:
            return

        lines = [
            f"{len(self._failures)} validation step(s) failed:",
        ]

        for failure in self._failures:
            lines.append(self._label(failure.number, "FAIL", failure.title))
            lines.extend(f"  - {message}" for message in failure.messages)

        pytest.fail("\n".join(lines), pytrace=False)
