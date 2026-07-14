# Test Plan — Single Bet Placement

## 1. Test Plan Information

| Field | Value |
|---|---|
| Status | Final |
| Test object | Single Bet Placement |
| Platform | Desktop web application |
| Target environment | Latest desktop Chrome |
| Test level / layer | UI system testing and API testing |
| Test basis | *QA Engineer Home Assignment - Scoped*; *Feature Specification - Single Bet Placement* |
| Planned scenarios | 6 |
| Selected for manual execution | TP-01, TP-02, TP-03 |
| Out of scope | Live betting; accumulators/multi-bets; other sports; mobile-specific UX |

## 2. Test Objective and Approach

| Item | Description |
|---|---|
| Objective | Validate the highest-risk behaviours of the documented single pre-match football bet flow. |
| Approach | Risk-based, focused coverage of the critical happy path, financial controls, negative validation, boundary conditions, single-selection behaviour, API validation, and filtering. |
| Design methods | End-to-end scenario testing, boundary value analysis, equivalence partitioning, and state-transition coverage. |
| Test data strategy | Use the assigned user ID, reset balance through the API when deterministic state is required, and record dynamic match and odds data during execution. |
| Exit condition | The top three scenarios are executed and all observed defects, limitations, and clarifications are documented. |

## 3. Product Risk Analysis

> Likelihood is not numerically scored because no production usage, defect history, or incident data was provided. Priorities are based on documented business impact, financial exposure, and the centrality of the behaviour to the feature.

| Risk ID | Product area | Risk / failure mode | Potential impact | Test response | Risk level |
|---|---|---|---|---|---|
| R-01 | Bet placement | A valid single bet cannot be placed or resolves inconsistently. | Core feature unavailable; failed customer journey. | Full successful E2E placement validation. | Critical |
| R-02 | Balance and payout | Stake is deducted incorrectly, more than once, or payout/receipt values disagree. | Direct financial error, disputes, loss of trust. | Cross-check pre-placement values, receipt, and final balance. | Critical |
| R-03 | Available-balance validation | A user can stake more than the available balance. | Invalid or negative financial state. | Test one cent above a deterministic reduced balance. | High |
| R-04 | Stake validation | Invalid minimum, maximum, precision, required, or numeric values are accepted. | Invalid wagers and inconsistent calculations. | Boundary value and equivalence-partition datasets. | High |
| R-05 | Single-selection rule | A new selection does not replace the previous one. | User may place a bet on an unintended outcome. | Verify state replacement and one active selection. | High |
| R-06 | API validation | Invalid selection values are accepted when the UI is bypassed. | Invalid bet records and weakened server-side controls. | Direct API semantic-validation test. | High |
| R-07 | Odds filters | Inclusive boundaries or invalid ranges are handled incorrectly. | Valid opportunities hidden or misleading results shown. | Equal-boundary and min-greater-than-max checks. | Medium |

## 4. Specification Clarification

| ID | Area | Issue | Test handling |
|---|---|---|---|
| CLAR-001 | Minimum stake | Business Rules define **€1.00**, Stake Validation defines **€1.01**, while the required UI message states **“Minimum stake is €1.00”**. | Record observed behaviour for exactly **€1.00**, but do not assign Pass/Fail until clarified. |

## 5. Common Execution Context

| Item | Instruction |
|---|---|
| UI authentication | Append the assigned candidate ID as the `user-id` query parameter. |
| API authentication | Send the assigned candidate ID in the `x-user-id` header. |
| Known balance setup | Use `POST /api/reset-balance`. |
| Persisted balance check | Use `GET /api/balance` when financial state must be confirmed. |
| Dynamic data | Record match, selection, and odds used during execution; do not hard-code catalogue values. |
| Test isolation | Reset balance after scenarios or datasets that place a successful bet. |

## 6. Scenario Summary

| Rank | Test Case ID | Title | Priority | Risk Coverage | Design Method | Execution |
|---:|---|---|---|---|---|---|
| 1 | TP-01 | Successful single-bet placement with financial and receipt consistency | Critical | R-01, R-02 | End-to-end scenario | Execute |
| 2 | TP-02 | Stake exceeding available balance is rejected without financial state change | High | R-03 | Boundary value analysis | Execute |
| 3 | TP-03 | Stake boundary and input-format validation | High | R-04 | Boundary value analysis, equivalence partitioning | Execute |
| 4 | TP-04 | Single active selection and replacement behaviour | High | R-05 | State transition | Design only |
| 5 | TP-05 | API rejects an invalid selection without changing user balance | High | R-06 | Equivalence partitioning | Design only / automation candidate |
| 6 | TP-06 | Odds-filter boundary and invalid-range handling | Medium | R-07 | Boundary value analysis | Design only |

---

# 7. Test Cases

## TP-01 — Successful single-bet placement with financial and receipt consistency

| Field | Value |
|---|---|
| Priority | Critical |
| Risk coverage | R-01, R-02 |
| Requirement references | Feature Specification §§2.1–2.4 and §3; Assignment Domain Context |
| Test type | Positive UI end-to-end |
| Design method | End-to-end scenario |
| Preconditions | Balance reset and verified as **€125.50 EUR**; at least one upcoming match is available. |
| Test data | Stake: **€10.00**; an available outcome with displayed odds containing no more than two decimal places. |
| Risk rationale | Incorrect placement, payout, balance deduction, or receipt data may create direct financial impact, disputes, and loss of trust. |

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Open the application with the candidate `user-id`. | The application loads and displays an available balance of **€125.50**. |
| 2 | Select one outcome and record the match, selection, and displayed odds. | The same match, selection, and odds appear in the bet slip as the only active selection. |
| 3 | Enter a stake of **€10.00**. | The stake is accepted. Potential payout equals **stake × recorded odds**, and balance remains unchanged before placement. |
| 4 | Click **Place Bet** once. | The button displays **`Placing...`**, an in-progress state is shown, and the request resolves to one successful outcome. |
| 5 | Verify the success receipt. | A non-empty Bet ID and timestamp are shown. Match order, selection, stake, odds, and payout match the pre-placement values. |
| 6 | Close the receipt. | The main flow is restored with no active selection. The stake is deducted exactly once, leaving **€115.50**, consistently displayed wherever balance is shown. |

## TP-02 — Stake exceeding available balance is rejected without financial state change

| Field | Value |
|---|---|
| Priority | High |
| Risk coverage | R-03 |
| Requirement references | Feature Specification §§2.2, 4.1 and 4.4 |
| Test type | Negative UI and API state verification |
| Design method | Boundary value analysis |
| Preconditions | Reset balance to **€125.50**. Through the API, place one valid **€100.00** bet and verify a remaining balance of **€25.50**. |
| Test data | Stake under test: **€25.51** |
| Risk rationale | Allowing a stake above available funds could create an invalid financial state and customer disputes. |

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Open the application and confirm the available balance. | The UI displays **€25.50**. |
| 2 | Select one outcome for an upcoming match. | The outcome appears as the only active selection in the bet slip. |
| 3 | Enter **€25.51** and attempt to place the bet. | Placement is blocked or rejected, **`Insufficient balance`** is shown, and no success receipt appears. |
| 4 | Verify the balance in the UI and through `GET /api/balance`. | The balance remains **€25.50** and is consistent between UI and API. |

## TP-03 — Stake boundary and input-format validation

| Field | Value |
|---|---|
| Priority | High |
| Risk coverage | R-04 |
| Requirement references | Feature Specification §§3, 4.1 and 4.4 |
| Test type | Data-driven negative and boundary UI validation |
| Design method | Boundary value analysis and equivalence partitioning |
| Preconditions | Balance is **€125.50**; at least one upcoming match is available; select a fresh outcome before each dataset where needed. |
| Risk rationale | Incorrect validation may allow invalid wagers, calculations, or account states. |

| Dataset | Stake | Classification | Expected Result |
|---:|---|---|---|
| 1 | Empty | Invalid — required | Placement is blocked or rejected; no success receipt appears. |
| 2 | `0.99` | Invalid — below minimum | Placement is blocked or rejected and **`Minimum stake is €1.00`** is shown. |
| 3 | `1.00` | Specification conflict | Record observed behaviour as **Clarification Required**; do not assign Pass/Fail because of CLAR-001. |
| 4 | `1.01` | Valid lower value | The value is accepted and the bet can be placed successfully. |
| 5 | `100.00` | Valid upper boundary | The value is accepted and the bet can be placed successfully. |
| 6 | `100.01` | Invalid — above maximum | Placement is blocked or rejected and **`Maximum stake is €100.00`** is shown. |
| 7 | `10.001` | Invalid — precision | The value is not accepted or placement is rejected because more than two decimal places are not allowed. |
| 8 | `abc` | Invalid — non-numeric | The value is not accepted or placement is rejected because stake must be numeric. |

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Open the application, select an outcome, and confirm the balance is **€125.50**. | The selected outcome appears in the bet slip and the known balance is displayed. |
| 2 | Enter each dataset and attempt to place the bet. | Each dataset is handled according to the matrix above. |
| 3 | Reset balance and select a fresh outcome before the next dataset if the previous dataset may have changed state. | The next dataset starts from a known, isolated state. |
| 4 | After each rejected dataset, verify the UI and `GET /api/balance`. | No success outcome appears and persisted balance remains unchanged. |

## TP-04 — Single active selection and replacement behaviour

| Field | Value |
|---|---|
| Priority | High |
| Risk coverage | R-05 |
| Requirement references | Feature Specification §§2.1–2.2 and §3 |
| Test type | Functional UI |
| Design method | State transition |
| Preconditions | At least one match with all three selectable outcome buttons is available; stake remains empty. |
| Risk rationale | Failure may cause a user to place a bet on an unintended outcome. |

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Select one outcome and record its details. | The match and outcome appear as the only active selection in the bet slip. |
| 2 | Select a different outcome for the same match. | The new outcome replaces the previous selection. |
| 3 | Inspect the match list and bet slip. | Only the second outcome remains active; the first is no longer active or present in the bet slip. |

## TP-05 — API rejects an invalid selection without changing user balance

| Field | Value |
|---|---|
| Priority | High |
| Risk coverage | R-06 |
| Requirement references | Feature Specification §§4.2, 4.3 and 5.3 |
| Test type | Negative API |
| Design method | Equivalence partitioning |
| Preconditions | Reset and record balance through `GET /api/balance`; obtain a valid `matchId` from `GET /api/matches`. |
| Test data | `selection = "INVALID"`, `stake = 10.00` |
| Risk rationale | Server-side validation must protect the system when the UI is bypassed. |

**Request body**

```json
{
  "matchId": "<valid-match-id>",
  "selection": "INVALID",
  "stake": 10.00
}
```

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Send `POST /api/place-bet` with a valid `x-user-id` and the request body above. | The API returns **422** for semantic validation failure and no successful bet response. |
| 2 | Request balance through `GET /api/balance`. | Balance is unchanged from the recorded pre-request value. |

## TP-06 — Odds-filter boundary and invalid-range handling

| Field | Value |
|---|---|
| Priority | Medium |
| Risk coverage | R-07 |
| Requirement references | Feature Specification §2.6 |
| Test type | Functional UI boundary and negative validation |
| Design method | Boundary value analysis |
| Preconditions | At least one match with visible decimal odds is available. |
| Test data | Record one displayed odds value as **O**. |
| Risk rationale | Incorrect filtering may hide valid opportunities or show misleading results. |

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Apply an odds range with **minimum = O** and **maximum = O**. | The recorded odds value **O** remains included; equality at both boundaries does not exclude it. |
| 2 | Apply a range where minimum is greater than maximum. | The range is rejected and clear feedback is shown. |
| 3 | Inspect filter state and displayed results. | The application does not silently accept or apply the invalid range as valid. |

## 8. Design and Maintenance Notes

| Principle | Application |
|---|---|
| Traceability | Each test references the relevant specification section and product risk. |
| Readability | Metadata and steps are presented in a test-management-tool-style table format. |
| Isolation | Known balance setup and cleanup reduce dependencies between tests. |
| Maintainability | Dynamic match and odds data are recorded during execution instead of hard-coded. |
| Reliable oracles | Undefined behaviour is documented as clarification rather than converted into an assumption. |
| Proportionality | The plan remains concise enough for the stated two-hour assignment. |
