# Test Strategy and Recommendations — Single Bet Placement

## 1. Professional Test Approach

I applied an **ISTQB-aligned, risk-based testing approach** and used **TMMi-informed test process practices** to structure the work. These internationally recognized frameworks guided the terminology, prioritization, test design, traceability, execution reporting, defect reporting, and improvement recommendations used in this submission.

The approach is deliberately focused because the assignment is time-boxed. Test effort is concentrated on the product areas with the greatest potential customer and business impact rather than attempting exhaustive coverage.

The submission combines:

- one critical end-to-end UI scenario;
- one API business-rule validation test;
- targeted manual boundary, negative, state-transition, and exploratory checks;
- documented risks, execution evidence, defects, clarifications, and residual coverage gaps.

This statement describes the professional practices I applied. It does not claim that the project or organization has undergone a formal TMMi assessment or achieved a particular maturity level.

## 2. Risk-Based Prioritization

Financial integrity has the highest priority because bet placement is both the main customer transaction and a core revenue-generating function.

Incorrect stake deduction, payout calculation, currency, receipt information, or balance state can cause:

- direct customer loss or incorrect charging;
- operator revenue leakage or incorrect payout liability;
- disputes, refunds, chargebacks, and manual reconciliation;
- increased support and operational costs;
- loss of customer confidence, reduced retention, and reputational damage;
- unreliable financial reporting and audit evidence;
- possible compliance exposure, depending on the applicable jurisdiction and controls.

Trust is fundamental in a betting product. Even a small visible inconsistency may make a customer question whether their funds and winnings are handled correctly. The resulting reputational and retention impact may be much larger than the value of the individual transaction.

For this reason, unresolved Critical financial-integrity defects should be treated as **release blockers**. High-severity defects that misrepresent a transaction should require explicit business risk acceptance before release.

## 3. Why These Two Tests Were Automated

### Critical UI E2E — Single Bet Placement and Financial Consistency

The UI test covers the central customer journey: selecting an upcoming outcome, entering a stake, validating the preview payout, placing the bet, checking the success receipt, and verifying the resulting balance.

It was selected because it covers the highest product risks:

- a valid bet cannot be placed or resolves inconsistently;
- stake, odds, payout, receipt, currency, or balance values disagree;
- the customer receives misleading financial information.

The test crosses the browser flow and API-backed account state, making it suitable as a release smoke test. Its step reporting and soft validations expose multiple related financial defects in one execution while preserving readable failure information and evidence.

### API Test — Invalid Selection Is Rejected Without Balance Change

The API test submits an unsupported selection and verifies both the semantic validation response and the unchanged account balance.

It was selected because server-side controls must remain effective when the UI is bypassed. The API layer provides faster and more precise feedback than the browser for this rule, while the balance assertion verifies the business consequence rather than checking only the HTTP status.

## 4. Coverage Intentionally Left Manual

| Area | Reason | Recommended future treatment |
|---|---|---|
| Stake boundary and input-format matrix | Efficient to explore with multiple datasets, while the minimum-stake requirement contains a contradiction. | Clarify the rule, then add parameterized API/component tests and retain a small UI subset. |
| Insufficient-balance UI behaviour | Manually verified; deterministic setup currently depends on an unreliable reset contract. | Add lower-layer balance tests first, then one UI regression check. |
| Single-selection replacement | Important but narrower than the selected financial E2E journey. | Add a short UI state-transition test. |
| Date and odds filters | Medium risk and interaction-heavy within the assignment time-box. | Add component/API boundary tests and a small UI smoke check. |
| Error modal and retry | No deterministic failure trigger was provided. | Introduce a test hook or mockable failure mode, then automate Rebet, Close, and top-right X behaviour. |

## 5. Recommendations for Scaling

### 5.1 Layered CI/CD Quality Gates

Run unit, component, API, and contract tests on every pull request. After deployment to an isolated test environment, run the critical Chrome UI smoke test. Broader UI regression should run before release or on a schedule.

Use the existing `api` and `ui` pytest markers to separate pipeline stages. Retain screenshots, HTML, logs, and pytest step output for failed runs.

Recommended release criteria:

- no open Critical defects affecting financial calculation or account state;
- no unresolved High defects that misrepresent a transaction without explicit risk acceptance;
- all critical automated checks passing in the target environment;
- known residual risks documented and accepted by the responsible stakeholder.

### 5.2 Deterministic Test Data and State

Provide isolated test users and reliable, idempotent setup endpoints whose responses match persisted state. Seed known upcoming events and keep odds stable for the duration of a test run.

Priority improvements:

- make reset response and persisted balance identical;
- generate events relative to a controlled clock and timezone;
- isolate account state for parallel execution;
- define cleanup behaviour;
- retain stable IDs or dedicated test attributes for interactive elements.

### 5.3 Lower-Layer Financial and Contract Coverage

Financial calculations and state transitions should be tested below the browser layer for faster, more deterministic feedback.

Priority additions:

- payout calculation and explicit rounding rules;
- exactly-once stake deduction;
- duplicate-submit, retry, and idempotency behaviour;
- receipt-to-placement consistency;
- currency consistency across endpoints;
- upcoming-event filtering;
- API/UI balance consistency;
- API schema and error-contract validation.

### 5.4 Auditability and Observability

Each bet should be traceable through a stable transaction identifier across the UI, API response, logs, and persisted account state.

Recommended controls include correlation IDs, structured financial transition logs, immutable transaction history or equivalent audit evidence, automated reconciliation, and alerts for balance, payout, or duplicate-deduction anomalies.

### 5.5 Defect Prevention

The confirmed defects suggest inconsistent data mapping or multiple sources of truth. Root-cause analysis should identify the authoritative source for team order, selection, payout, currency, and balance rather than correcting each UI symptom independently.

Fixes should be protected by unit, API, contract, and UI regression tests at the lowest appropriate layer. Related flows should be reviewed for the same defect pattern.

## 6. Information Needed for a Fuller Quality Assessment

The assignment materials are sufficient for a focused assessment, but the following information would be needed for a more complete quality picture:

- an authoritative decision on the contradictory minimum-stake rule;
- a defined payout precision and rounding policy;
- a reliable test-data reset contract and controlled system clock/timezone;
- the versioned API schema and change history;
- supported browser, operating-system, and device matrix;
- non-functional requirements for performance, security, accessibility, resilience, and concurrency;
- applicable regulatory, audit, and data-retention requirements;
- production usage, incident, defect, and customer-support data for quantitative likelihood assessment;
- architecture, source code, lower-level tests, logs, and monitoring information for root-cause analysis and deeper coverage planning.

These are recorded as information gaps, not as defects in the submitted feature unless the specification explicitly requires them.

## 7. Current Quality Signal

The automated UI test completes the placement journey and fails on confirmed product mismatches rather than framework or locator issues. Current evidence shows reversed match order in the receipt, a missing selected outcome, an incorrect receipt payout, and a stale UI balance after placement. Follow-up exploratory testing also confirmed that repeated placements can bypass the available-balance rule and persist a negative account balance.

The incorrect payout, negative account balance, inconsistent account state, and unreliable reset behaviour are the highest release risks. Based on the available evidence, the feature should not be considered production-ready until the Critical financial-integrity defects are corrected and successfully retested.
