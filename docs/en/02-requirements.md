# Requirements — Order ingestion for Transportes Meseta

> FDE course · Assignment 01 · [Versión en español](../es/02-requisitos.md)
>
> Identifiers (RF-xx, RNF-xx) are stable and are cited in commits, PRs and ADRs.
> Priority: **M** (must), **S** (should), **C** (could).
>
> Status of each requirement:
> **Confirmed** = backed by the interview with the head of operations
> (October 2026). **Assumed** = comes from the initial brief or our own
> judgement and the client has not validated it. A requirement can be confirmed
> as a need while its acceptance criteria remain assumed; each case says so.

## 1. Canonical order model

Every source is translated into a single `Order` model:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `customer_code` | text | yes | Customer code exactly as it exists in Logiwin. |
| `external_ref` | text | yes | Order reference in the customer's own system. |
| `pickup_address` | text | yes | Pickup address. |
| `delivery_address` | text | yes | Delivery address. |
| `delivery_contact_name` | text | no | Warehouse manager, site foreman or private individual. **Personal data.** |
| `delivery_contact_phone` | text | no | Contact phone at destination. **Personal data.** |
| `delivery_is_consumer` | boolean | yes | `true` when the destination is a private individual's home (e.g. Muebles Cifuentes). Triggers short retention. |
| `requested_date` | date | yes | Requested pickup date. |
| `lines[]` | list | yes (≥ 1) | Description, quantity, optional weight (kg) and volume (m³). |
| `notes` | text | no | Free remarks. May contain personal data ("call first, works mornings"). |
| `source` | enum | yes | `excel` or `email`. |
| `source_id` | text | yes | File path or email `Message-ID`. |

The duplicate key is `(customer_code, external_ref)`.

The contact fields and `delivery_is_consumer` were added after the interview:
the Excel files carry the manager's name and phone and, for Cifuentes, the end
customer's. How to detect that a destination is a private individual is still
open (Q13).

## 2. Functional requirements

### RF-01 · Excel ingestion · M · Confirmed

All four main customers send Excel. The system reads `.xlsx` files dropped
into the inbox folder and extracts one order per row (or per sheet, depending
on customer configuration).

- AC-01.1 A file with N valid rows yields N orders. *(assumed: one order per
  row; we have not seen the templates, Q3)*
- AC-01.2 The column → canonical field mapping is defined per customer in a
  configuration file, with no code changes.
- AC-01.3 A processed file is moved to `processed/`; an unreadable one to
  `rejected/` with a report of the reason.
- AC-01.4 Dates are accepted as `dd/mm/yyyy`, `yyyy-mm-dd` and native Excel dates.
- AC-01.5 Agroalimentaria's Monday file is processed in full within one cycle.
  Its size is pending (Q8). *(confirmed as a need)*

### RF-02 · Email ingestion · M · Confirmed (mailbox), Assumed (format)

A dedicated orders mailbox has existed for years. The system reads it over
IMAP and processes every unread message after a configurable cut-off date.

- AC-02.1 If the email carries an `.xlsx` attachment, it is processed as in RF-01.
- AC-02.2 If the body contains orders in semi-structured form (`field: value`
  per line), they are extracted with the same validation rules. *(assumed: the
  head of operations describes free text; real emails must be reviewed)*
- AC-02.3 The sender identifies the customer through a table of authorised
  addresses; an unknown sender goes to manual review.
- AC-02.4 Each message is processed exactly once (marked as read or moved to a
  `processed` folder).
- AC-02.5 Messages older than `IMAP_SINCE` are never processed. The mailbox
  holds years of history. *(history confirmed; the cut-off date is Q9)*

### RF-03 · Normalisation · M · Assumed

Every order is converted to the canonical model before any other operation.

- AC-03.1 Addresses and references are trimmed and case-normalised by a
  configurable rule.
- AC-03.2 An order that cannot be mapped to all required fields is rejected
  with a list of the missing fields.

### RF-04 · Business validation · M · Confirmed (need), Assumed (rules)

The three errors found on the road today are address, weight and repeat.
Validation must cover them and, when in doubt, **not load**: the head of
operations prefers twelve orders in review to one loaded wrong.

- AC-04.1 `customer_code` must exist in Logiwin (cached lookup).
- AC-04.2 `requested_date` cannot be before today nor more than 90 days ahead.
  *(assumed; past-date orders, Q4)*
- AC-04.3 Every line must have quantity > 0.
- AC-04.4 The order's total weight must fall within a per-customer
  configurable range; out of range, or missing when that customer always sends
  it, goes to review. *(confirmed as a need; the ranges are Q11)*
- AC-04.5 The delivery address must pass a minimum check (recognisable town,
  not empty, not equal to the pickup address); which master data it is checked
  against is Q10. *(confirmed as a need)*
- AC-04.6 An invalid order is not discarded: it goes to the review queue with
  the reasons.

### RF-05 · Logiwin creation · M · Assumed (API)

- AC-05.1 A valid, non-duplicate order is created in Logiwin through its API
  and the returned identifier is stored. *(assumed: the API has not been seen, Q1)*
- AC-05.2 On transient API failure the call is retried with exponential backoff
  (configurable maximum); on permanent failure the order goes to review.
- AC-05.3 With `DRY_RUN=true` nothing is written to Logiwin and what would
  have been created is logged.
- AC-05.4 Only the filtered `notes` field reaches Logiwin's remarks field,
  never the full email body. *(new, derived from the free-text remarks risk)*

### RF-06 · Deduplication · M · Confirmed

Today repeated orders get into Logiwin and are invoiced twice. Logiwin does
not reject them (to be confirmed by IT, Q6), so deduplication is this system's
responsibility.

- AC-06.1 An order whose `(customer_code, external_ref)` key was already
  loaded is not created again.
- AC-06.2 If the duplicate differs from the original in any field, it is
  flagged as a *possible correction* and goes to manual review.
- AC-06.3 Processing the same file or email twice has no additional effect
  (idempotency by `source_id`).
- AC-06.4 If the customer sends no reference of its own, a stable key is
  derived from (customer, date, delivery address, lines) and a match goes to
  review as a *possible repeat*, never loaded. *(assumed: we do not know which
  customers send a reference, Q3)*

### RF-07 · Manual review queue · M · Confirmed

This is the central requirement for the head of operations: doubtful orders
must be visible mid-morning, not discovered in Alcalá. Pili, Rosa and Carmen
review it.

- AC-07.1 Every order that cannot be loaded automatically is recorded with its
  state, reasons and original data.
- AC-07.2 The back office receives an email notification summarising orders
  pending review on every cycle that has any, and in any case before a
  configurable cut-off time (proposed: 11:00). *(confirmed: "at eleven in the
  morning")*
- AC-07.3 A reviewed order can be reprocessed after the source is corrected.
- AC-07.4 The summary states each order's reason in office language ("weight
  out of range", "possible repeat of order 1234"), not codes.

### RF-08 · Traceability and audit · M · Assumed

The client did not ask for it; we keep it because it underpins RF-06 and RF-07.

- AC-08.1 For every order the system stores: source, `source_id`, receipt
  time, outcome (created / review / duplicate), Logiwin identifier and errors.
- AC-08.2 History can be queried by `external_ref` and by `source_id`.

### RF-09 · Command line · S · Assumed

- AC-09.1 `meseta-ingesta run` executes one full cycle; `watch` repeats it
  every `IMAP_POLL_SECONDS`.
- AC-09.2 `meseta-ingesta config` prints the effective configuration with
  secrets masked.

### RF-10 · Status report · C · Confirmed (reworded)

The brief's end-of-day report is replaced by what the head of operations wants
to see: the state of the batch at the time that matters.

- AC-10.1 At a configurable time (proposed: 13:30) operations receives a
  summary: orders received, created, in review and duplicate, per customer,
  plus the list of files received that day that are not yet complete.
- AC-10.2 The summary carries no office-time figures and no per-person counts.

## 3. Non-functional requirements

| Id | Requirement | Priority | Status |
| --- | --- | --- | --- |
| RNF-01 | **Idempotency.** Reprocessing any input never creates additional orders. | M | Confirmed |
| RNF-02 | **Secrets out of code.** Credentials only via environment variables or an unversioned `.env`. | M | Assumed |
| RNF-03 | **GDPR.** Personal data is never written to logs. Original files and emails, and orders with `delivery_is_consumer`, are deleted after 60 days; other orders after 90. Periods subject to the advisors' review. | M | Confirmed (1-2 months is enough) |
| RNF-04 | **Observability.** Structured logs carrying `source_id` on every line; basic metrics of orders per outcome. | S | Assumed |
| RNF-05 | **Performance.** A cycle with 300 orders completes in under 5 minutes. Agroalimentaria's Monday file is finished within one hour of arrival. | S | Confirmed (target), Assumed (size) |
| RNF-06 | **Resilience.** A Logiwin or IMAP outage loses no orders: they are retried in the next cycle. | M | Assumed |
| RNF-07 | **Maintainability.** Test coverage ≥ 80 % on parsing and validation; green CI required to merge. | M | Assumed |
| RNF-08 | **Portability.** Runs on Linux x86-64; no mandatory cloud dependencies. | M | Assumed |
| RNF-09 | **Per-customer configuration.** Template mappings, authorised senders and weight ranges are versioned configuration files. | M | Assumed |
| RNF-10 | **Precision over coverage.** No automation threshold justifies loading a doubtful order. No auto-creation percentage target is defined. | M | Confirmed |

## 4. Out of scope

See section 5 of the [brief](01-brief.md).

## 5. Open questions

| # | Question | Owner | Status |
| --- | --- | --- | --- |
| Q1 | Does the Logiwin API allow searching orders by external reference? | IT lead | Open |
| Q2 | Is there a dedicated mailbox, or must the general one be filtered? | Back office | **Answered**: a dedicated orders mailbox has existed for years |
| Q3 | Which Excel templates exist today, how many customers use each, and which carry a reference of their own? | Back office | Open |
| Q4 | Orders for a past date: reject or load with a warning? | Operations | Open |
| Q5 | Where does it run: internal server, container, cron? | IT lead | Open |
| Q6 | Does Logiwin accept two orders with the same customer reference, or reject them? | Javier / IT | Open (the interview suggests it accepts them) |
| Q7 | Is there a Logiwin test environment, or only production? | IT lead | Open |
| Q8 | How many rows does Agroalimentaria's Monday file carry, and when does it arrive? | Pili, Rosa or Carmen | Open |
| Q9 | Which cut-off date do we apply to the mailbox history at start-up? | Back office | Open |
| Q10 | What is an address validated against: Logiwin master data, geocoding, the customer's site list? | Luis | Open |
| Q11 | Which weight range is suspicious, per customer or per goods type? | Luis | Open |
| Q12 | Should end-customer remarks go into Logiwin verbatim, or only the operational part? | Operations | Open |
| Q13 | How do we tell, in the Cifuentes file, a shop delivery from a home delivery? | Back office | Open |
| Q14 | Retention period and legal basis for private individuals' data (Cifuentes). Is 60 days in our system acceptable? | Javier and the advisors | Open (not an operations decision) |
| Q15 | How are orders spread over the rest of the week and the day? We only know about Monday. | Back office | Open |

## 6. Glossary

- **Order**: a customer request to move goods from A to B on a date.
- **Shipment (porte)**: the transport service performed and invoiced; a duplicate order yields a shipment invoiced twice.
- **Line**: each package or group of packages in an order.
- **External reference**: the order identifier in the customer's system.
- **Review queue**: the set of orders that need a human decision.
- **Logiwin**: Transportes Meseta's ERP where final orders, planning and invoicing live.
- **Cut-off time**: deadline for doubtful orders to be reviewed before routes are built (proposed: 11:00 review, 14:00 full batch).
