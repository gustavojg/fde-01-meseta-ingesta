# Brief — Order ingestion for Transportes Meseta

> FDE course · Assignment 01 · [Versión en español](../es/01-brief.md)
>
> Transportes Meseta is a fictional course client. Context marked as
> *assumption* must be confirmed with the client before implementation.

## 1. The client

Transportes Meseta is a road freight carrier based in Castilla y León, Spain.
It runs its own fleet of about 40 vehicles and serves a stable base of about
60 industrial and distribution customers (*assumption*). Operations run on a
sector ERP that already has order, planning and invoicing modules.

## 2. The problem

Customers send transport orders through two channels:

1. **Excel files.** Every customer uses its own template (different columns,
   order, header language and date formats). They arrive as email attachments
   or are dropped into a shared folder.
2. **Email.** Free or semi-structured text in the message body, sometimes
   with the Excel attached, sometimes with the data only in the text.

Today two people in the back office read every order and key it into the ERP
by hand. This causes:

- **Transcription errors** in addresses, dates and quantities, discovered when
  the truck is already on the road.
- **Duplicate orders** when a customer resends the same email or corrects the
  Excel and sends it again.
- **Delays**: orders arriving in the afternoon are not in the ERP until the
  next morning and miss that day's planning.
- **No traceability**: nobody knows whether a given order was loaded, by whom,
  or from which email.

Estimated volume: 80-150 orders per day, with month-end peaks of 300
(*assumption*).

## 3. Goal

Build an ingestion service that reads orders from both channels, normalises
them into a single model, validates them, discards duplicates and creates them
in the ERP without human intervention in clear cases, routing doubtful ones to
a review queue.

## 4. Success criteria

| Metric | Today | Target |
| --- | --- | --- |
| Orders created without manual intervention | 0 % | ≥ 80 % |
| Time from receipt to ERP creation | 2-18 h | < 15 min |
| Duplicate orders in the ERP | several per week | 0 |
| Orders with traceable origin (file / email) | 0 % | 100 % |

## 5. Scope

**In scope**

- Reading `.xlsx` files from an inbox folder.
- Reading a dedicated IMAP mailbox (body and `.xlsx` attachments).
- Per-customer configurable mapping from template columns to the canonical model.
- Business validation and duplicate detection.
- Creating the order in the ERP through its API.
- Manual review queue with notification to operations.
- Audit log for every processed order.
- *Dry-run* mode to test without writing to the ERP.

**Out of scope (for this assignment)**

- A web UI for the review queue: the ERP itself or email will be used.
- Orders arriving as PDF, images or phone calls.
- Modifying or cancelling orders already loaded.
- Changes to the ERP or its master data (customers, addresses).

## 6. Stakeholders

| Role | Interest |
| --- | --- |
| Head of operations | Having every order in the day's planning first thing in the morning. |
| Back office (2 people) | Stop typing; review only the exceptions. |
| IT lead | A deployable, observable component that never touches the ERP by hand. |
| End customers | Not being asked to change how they send orders. |

## 7. Constraints

- The ERP exposes a REST API with key authentication (*assumption*); writing
  directly to its database is not allowed.
- Customer Excel templates **cannot be changed**.
- Order data contains personal data (contacts, addresses) and is subject to GDPR.
- The service will run on a client-owned Linux server, with no mandatory cloud
  dependencies.

## 8. Risks and assumptions

- Free-text emails are the most ambiguous channel: the share of orders landing
  in manual review may be high at first.
- The ERP API may not expose everything needed (for instance duplicate lookup).
  This must be confirmed in the first week.
- Excel templates change without notice; the mapping must be configuration,
  not code.

## 9. Deliverables

1. This brief and the requirements ([02-requirements.md](02-requirements.md)).
2. Architecture decisions recorded as ADRs ([adr/](adr/README.md)).
3. Source code with tests and CI.
4. Deployment and operations guide (pending).
