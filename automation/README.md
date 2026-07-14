# Sporty Group QA Automation

A deliberately small Python automation project for the **Single Bet Placement** assignment.

## Scope

The framework contains exactly the two requested high-value automated tests:

1. **Critical UI E2E:** places a valid single bet and verifies the pre-placement payout, receipt contents, and post-placement balance.
2. **API business rule:** submits an invalid selection and verifies HTTP `422` plus unchanged balance.

The UI layer uses the **Page Object Model**:

- `BasePage` centralises framework-specific browser interactions and waits.
- `BettingPage` contains page-level user actions and business-readable availability assertions.
- `ReceiptModal` is a component object for the success receipt.
- Tests contain business assertions, not raw locator or WebDriver logic.
- API setup and validation use a separate `BettingApiClient`.

## Project Structure

```text
automation/
├── sporty_qa/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config.py
│   ├── step_reporter.py
│   ├── locators/
│   │   ├── __init__.py
│   │   ├── betting_page_locators.py
│   │   └── receipt_modal_locators.py
│   └── pages/
│       ├── __init__.py
│       ├── base_page.py
│       ├── betting_page.py
│       └── receipt_modal.py
├── tests/
│   ├── conftest.py
│   ├── api/test_invalid_selection.py
│   └── ui/test_single_bet_e2e.py
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+
- Latest desktop Google Chrome
- Network access to the assignment application

Selenium Manager is used through `webdriver.Chrome()`, so a compatible driver is normally resolved automatically.

## Setup — Windows PowerShell

```powershell
cd automation
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```


## Run

Run all tests. When `USER_ID` is not already configured, pytest prompts for it directly:

```powershell
pytest
```

```text
Enter the assigned USER_ID:
```

For non-interactive execution, use an environment variable, `.env`, or the optional CLI argument:

```powershell
pytest --user-id "<assigned-candidate-user-id>"
```

Run only the API test:

```powershell
pytest -m api
```

Run only the UI test:

```powershell
pytest -m ui
```

Run the browser visibly:

```powershell
$env:HEADLESS="false"
pytest -m ui
```

## Numbered Test Steps

Both automated tests use a lightweight pytest step reporter. It writes numbered
`START`, `PASS`, and `FAIL` entries directly to the pytest terminal reporter, so
the steps remain visible in a normal terminal, CI, and the PyCharm pytest runner
without requiring `-s` or an external reporting library.

Example:

```text
[STEP 01] START | Reset the test account balance through the API
[STEP 01] PASS  | Reset the test account balance through the API
[STEP 02] START | Read the persisted balance and select an upcoming match
[STEP 02] PASS  | Read the persisted balance and select an upcoming match
```

Hard setup or interaction failures stop immediately with the failed step number
and title. Business validations on the receipt and post-bet balance are soft
steps: all of them execute, failed step numbers are collected, and pytest fails
once with the complete defect list.

## Configuration

Configuration may come from the current environment or a local `.env` file:

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | **Required; supplied by environment or `.env`** | Application/API base URL |
| `USER_ID` | **Required; no default** | Candidate-specific UI query parameter and API header value |
| `HEADLESS` | `true` | Headless Chrome execution |
| `TEST_TIMEOUT_SECONDS` | `12` | UI wait and HTTP timeout |

Resolution order for `USER_ID`:

1. `--user-id` pytest option;
2. `USER_ID` environment variable or Git-ignored `.env` file;
3. interactive pytest prompt.

Example for a visible browser:

```powershell
$env:HEADLESS="false"
pytest -m ui
```


## Exact `.env` Location

Create the file with the exact name `.env` in the project root, next to
`pytest.ini` and `requirements.txt`:

```text
automation/
├── .env
├── .env.example
├── pytest.ini
├── requirements.txt
├── sporty_qa/
└── tests/
```

Create it from the template and replace the placeholder:

```powershell
Copy-Item .env.example .env
notepad .env
```

```env
BASE_URL=https://qae-assignment-tau.vercel.app
USER_ID=<assigned-candidate-user-id>
HEADLESS=true
TEST_TIMEOUT_SECONDS=12
```

Pytest resolves the file from `pytestconfig.rootpath`, so IDE working-directory
settings do not change which `.env` file is loaded. Shell/CI environment
variables override values from `.env`.

## Security of Configuration and Secrets

The automation source and committed configuration templates contain no
password, token, API key, or candidate-specific fallback. `USER_ID` must be
supplied at runtime. The manual execution report and evidence may identify the
assigned test user because they document the exact execution context; the ID is
treated as test data, not as an authentication secret.

For local development, a Git-ignored `.env` file is supported through
`python-dotenv`. Shell and CI environment variables take precedence, so CI can
inject values from its secret store without modifying files.

The assignment requires `user-id` in the URL and `x-user-id` header. It appears
to be a test identifier rather than a password, but it is still kept outside
source control because the repository is public. Real passwords, bearer tokens,
and API keys must never be placed in URL query parameters or committed to Git.

For GitHub Actions, store candidate-specific or sensitive values in repository
or environment secrets and map them into the test process:

```yaml
env:
  USER_ID: ${{ secrets.SPORTY_USER_ID }}
```

In a production-grade system, use a dedicated secret manager with
least-privilege access, audit logging, and credential rotation.

## Browser Interaction Abstraction

`BasePage` is the framework-facing boundary for browser operations. Page and
component objects call reusable methods such as `press_button()`,
`replace_text()`, `read_text()`, `wait_for_decimal()`, and
`wait_for_minimum_element_count()` rather than using Selenium `WebDriver` or
`WebElement` operations directly.

This keeps explicit waits, element lookup, clicks, keyboard input, attribute
reads, and numeric extraction in one implementation. It simplifies Selenium
upgrades and reduces the scope of a future migration to another browser
automation framework. Such a migration would still require changes to the
driver fixture and locator definitions, but the business-level Page Object
methods and test flow would remain substantially isolated from those changes.

User-facing availability assertions remain in the Page Objects so failures
continue to explain which business element or state was unavailable.

## UI Synchronisation

The shared browser primitives use Selenium explicit waits rather than fixed
sleeps. After navigation, `BettingPage.load()` waits for
`document.readyState`, the page heading, the match catalogue, and the expected
account balance. Later interactions wait for their target element to become
visible or clickable, and the payout reader waits for the expected calculated
value.

Element waits poll dynamically and stop as soon as the condition is met. Their
maximum duration is capped at **10 seconds**. Selenium implicit waits are not
used or mixed with explicit waits.

## Failure Evidence

When a UI test fails, `tests/conftest.py` automatically saves:

- a PNG screenshot;
- the current page source as HTML.

Generated files are written to `automation/artifacts/`. The directory is created only when a UI test fails and is ignored by Git.

## Test Data and Isolation

Each test resets the user balance before execution. The UI test then reads the **persisted** balance through `GET /api/balance` and uses a dynamically selected upcoming match. This keeps the automated journey executable while the manually documented reset-response inconsistency remains visible in the defect report.

The same user ID should not be used by parallel test workers because tests share account state.

## Known Current Findings

The current application may cause the critical UI test to fail because the manual run identified receipt and UI balance inconsistencies. Those failures are intentional signals from the automated oracle, not framework errors. See:

```text
../docs/execution_results.md
```

## Design Trade-offs

- No external reporting library was added; the built-in pytest terminal reporter shows numbered steps, while automatic screenshot/HTML capture provides failure evidence.
- Locators are stored separately from Page Objects and grouped by UI element type.
- The API test remains independent of the UI.
- Dynamic catalogue data is preferred over hard-coded match IDs.


## Assertion Diagnostics

Page Objects own element/state availability assertions and provide component-specific messages, while tests keep the business-value assertions. A failed CI or IDE run states:

- the numbered step that failed;
- the step title and execution status;
- which business expectation failed;
- the expected and actual values;
- whether the failure is a test precondition, API contract, UI consistency, or financial-state problem.

Receipt and post-bet validations are reported as separate soft steps, so one UI
journey can surface every confirmed defect instead of stopping at the first
business mismatch.

HTTP diagnostics include status, content type, and a truncated response body. Request headers and candidate identifiers are not printed.

## Locator Strategy

Locators are separated from Page Object behaviour under `sporty_qa/locators/`.
Each Page Object has a correspondingly named locator module:

- `BettingPage` → `betting_page_locators.py`
- `ReceiptModal` → `receipt_modal_locators.py`

Inside each locator class, selectors are grouped by UI element type, such as
`Containers`, `LoadingIndicators`, `Texts`, `Fields`, `Values`, `Buttons`, and `MatchCards`.
Dynamic selectors remain in the relevant group, for example
`BettingPageLocators.MatchCards.card(match_id)` and
`BettingPageLocators.Buttons.outcome(match_id, selection)`.

Selectors prefer stable application IDs from the supplied DOM, including
`header-balance`, `match-list`, `match-card-<matchId>`,
`odds-<matchId>-<selection>`, `bet-slip-stake-input`,
`bet-slip-potential-payout`, and `bet-slip-place-bet`.
