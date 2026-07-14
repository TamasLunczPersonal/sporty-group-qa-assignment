# Sporty Group QA Engineer Home Assignment

This repository contains a focused QA assessment of the **Single Bet Placement** feature. The submission includes a risk-based manual test plan, completed execution results with defect reports and evidence, a small Selenium/Pytest automation framework, and test strategy recommendations.

## Deliverables

- [Test Plan](docs/test_plan.md) — six prioritised scenarios covering the critical journey, validation, boundaries, and key business rules.
- [Execution Results and Bug Reports](docs/execution_results.md) — the top three scenarios, quick exploratory checks, eight confirmed defects, and two specification clarifications.
- [Test Strategy and Recommendations](docs/test_strategy_and_recommendations.md) — ISTQB-aligned risk-based testing and TMMi-informed process recommendations.
- [Automation Framework](automation/README.md) — Python, Selenium WebDriver, Pytest, and Requests with one critical UI E2E test and one API business-rule test.
- [Evidence](evidence/) — screenshots and API output referenced by the execution report.

## Current Quality Signal

The assessment identified **8 confirmed defects**: 3 Critical, 4 High, and 1 Medium. The most serious findings affect financial integrity, including incorrect receipt payout, inconsistent reset state, and repeated bets being accepted beyond available funds until a negative persisted balance is reached. The feature should not be considered release-ready until the Critical defects are corrected and successfully retested.

## Repository Structure

```text
SportyGroup/
├── README.md
├── .gitignore
├── docs/
│   ├── test_plan.md
│   ├── execution_results.md
│   └── test_strategy_and_recommendations.md
├── evidence/
└── automation/
    ├── README.md
    ├── requirements.txt
    ├── pytest.ini
    ├── .env.example
    ├── sporty_qa/
    └── tests/
```

## Automation Quick Start

```powershell
cd automation
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
pytest
```

Set the assigned candidate user ID in the local `.env` file. The real `.env` file is intentionally excluded from source control. Detailed setup, configuration, execution, and framework design notes are available in the [automation README](automation/README.md).
