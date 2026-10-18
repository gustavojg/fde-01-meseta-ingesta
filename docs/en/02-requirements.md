# Requirements — Order ingestion for Transportes Meseta

> FDE course · Assignment 01 · [Versión en español](../es/02-requisitos.md)
>
> Identifiers (RF-xx, RNF-xx) are stable and are cited in commits, PRs and ADRs.
> Priority: **M** (must), **S** (should), **C** (could).

## 1. Canonical order model

Every source is translated into a single `Order` model:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `customer_code` | text | yes | Customer code exactly as it exists in the ERP. |
| `external_ref` | text | yes | Order reference in the customer's own system. |
| `pickup_address` | text | yes | Pickup address. |
| `delivery_address` | text | yes | Delivery address. |
| `requested_date` | date | yes | Requested pickup date. |
| `lines[]` | list | yes (≥ 1) | Description, quantity, optional weight (kg) and volume (m³). |
| `notes` | text | no | Free remarks. |
| `source` | enum | yes | `excel` or `email`. |
| `source_id` | text | yes | File path or email `Message-ID`. |

The duplicate key is `(customer_code, external_ref)`.

## 2. Functional requirements

### RF-01 · Excel ingestion · M

The system reads `.xlsx` files dropped into the inbox folder and extracts one
order per row (or per sheet, depending on customer configuration).

- AC-01.1 A file with N valid rows yields N orders.
- AC-01.2 The column → canonical field mapping is defined per customer in a
  configuration file, with no code changes.
- AC-01.3 A processed file is moved to `processed/`; an unreadable one to
  `rejected/` with a report of the reason.
- AC-01.4 Dates are accepted as `dd/mm/yyyy`, `yyyy-mm-dd` and native Excel dates.

### RF-02 · Email ingestion · M

The system reads a dedicated IMAP mailbox and processes every unread message.

- AC-02.1 If the email carries an `.xlsx` attachment, it is processed as in RF-01.
- AC-02.2 If the body contains orders in semi-structured form (`field: value`
  per line), they are extracted with the same validation rules.
- AC-02.3 The sender identifies the customer through a table of authorised
  addresses; an unknown sender goes to manual review.
- AC-02.4 Each message is processed exactly once (marked as read or moved to a
  `processed` folder).

### RF-03 · Normalisation · M

Every order is converted to the canonical model before any other operation.

- AC-03.1 Addresses and references are trimmed and case-normalised by a
  configurable rule.
- AC-03.2 An order that cannot be mapped to all required fields is rejected
  with a list of the missing fields.

### RF-04 · Business validation · M

- AC-04.1 `customer_code` must exist in the ERP (cached lookup).
- AC-04.2 `requested_date` cannot be before today nor more than 90 days ahead.
- AC-04.3 Every line must have quantity > 0.
- AC-04.4 An invalid order is not discarded: it goes to the review queue with
  the reasons.

### RF-05 · ERP creation · M

- AC-05.1 A valid, non-duplicate order is created in the ERP through its API
  and the returned identifier is stored.
- AC-05.2 On transient API failure the call is retried with exponential backoff
  (configurable maximum); on permanent failure the order goes to review.
- AC-05.3 With `DRY_RUN=true` nothing is written to the ERP and what would
  have been created is logged.

### RF-06 · Deduplication · M

- AC-06.1 An order whose `(customer_code, external_ref)` key was already
  loaded is not created again.
- AC-06.2 If the duplicate differs from the original in any field, it is
  flagged as a *possible correction* and goes to manual review.
- AC-06.3 Processing the same file or email twice has no additional effect
  (idempotency by `source_id`).

### RF-07 · Manual review queue · M

- AC-07.1 Every order that cannot be loaded automatically is recorded with its
  state, reasons and original data.
- AC-07.2 Operations receives an email notification summarising orders
  pending review.
- AC-07.3 A reviewed order can be reprocessed after the source is corrected.

### RF-08 · Traceability and audit · M

- AC-08.1 For every order the system stores: source, `source_id`, receipt
  time, outcome (created / review / duplicate), ERP identifier and errors.
- AC-08.2 History can be queried by `external_ref` and by `source_id`.

### RF-09 · Command line · S

- AC-09.1 `meseta-ingesta run` executes one full cycle; `watch` repeats it
  every `IMAP_POLL_SECONDS`.
- AC-09.2 `meseta-ingesta config` prints the effective configuration with
  secrets masked.

### RF-10 · Daily report · C

- AC-10.1 At the end of the day a summary is sent: orders received, created,
  in review and duplicate, per customer.

## 3. Non-functional requirements

| Id | Requirement | Priority |
| --- | --- | --- |
| RNF-01 | **Idempotency.** Reprocessing any input never creates additional orders. | M |
| RNF-02 | **Secrets out of code.** Credentials only via environment variables or an unversioned `.env`. | M |
| RNF-03 | **GDPR.** Personal data is never written to logs; original files are kept for at most 90 days. | M |
| RNF-04 | **Observability.** Structured logs carrying `source_id` on every line; basic metrics of orders per outcome. | S |
| RNF-05 | **Performance.** A cycle with 300 orders completes in under 5 minutes. | S |
| RNF-06 | **Resilience.** An ERP or IMAP outage loses no orders: they are retried in the next cycle. | M |
| RNF-07 | **Maintainability.** Test coverage ≥ 80 % on parsing and validation; green CI required to merge. | M |
| RNF-08 | **Portability.** Runs on Linux x86-64 with Python 3.12+; no mandatory cloud dependencies. | M |
| RNF-09 | **Per-customer configuration.** Template mappings and authorised senders are versioned configuration files. | M |

## 4. Out of scope

See section 5 of the [brief](01-brief.md).

## 5. Open questions

| # | Question | Owner | Status |
| --- | --- | --- | --- |
| Q1 | Does the ERP API allow searching orders by external reference? | IT lead | Open |
| Q2 | Is there a dedicated mailbox, or must the general one be filtered? | Back office | Open |
| Q3 | Which Excel templates exist today and how many customers use each? | Back office | Open |
| Q4 | Orders for a past date: reject or load with a warning? | Operations | Open |
| Q5 | Where does it run: internal server, container, cron? | IT lead | Open |

## 6. Glossary

- **Order**: a customer request to move goods from A to B on a date.
- **Line**: each package or group of packages in an order.
- **External reference**: the order identifier in the customer's system.
- **Review queue**: the set of orders that need a human decision.
- **ERP**: Transportes Meseta's management system where final orders live.
