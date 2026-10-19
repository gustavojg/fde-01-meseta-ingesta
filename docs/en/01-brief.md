# Brief — Order ingestion for Transportes Meseta

> FDE course · Assignment 01 · [Versión en español](../es/01-brief.md)
>
> Transportes Meseta is a fictional course client. Context marked as
> *assumption* must be confirmed with the client before implementation.
> Context marked as *confirmed* comes from the interview with the head of
> operations (October 2026); see [03-process.md](03-process.md).

## 1. The client

Transportes Meseta is a road freight carrier based in Castilla y León, Spain.
It runs its own fleet of about 40 vehicles and serves a stable base of about
60 industrial and distribution customers (*assumption*). Operations run on
**Logiwin**, a sector ERP with order, planning and invoicing modules
(*confirmed*). Logiwin keeps every order since 2017 because they are needed
for invoicing and claims.

The four largest customers are (*confirmed*):

| Customer | What it sends | Delivers to |
| --- | --- | --- |
| Agroalimentaria | One large Excel first thing on Monday | Warehouses and supermarkets |
| Logística Sanz | Excel | Warehouses and supermarkets |
| Cerámicas | Excel | Construction sites and builders' merchants |
| Muebles Cifuentes | Excel and email | Shops and, sometimes, the end customer's home |

## 2. The problem

Customers send transport orders through two channels:

1. **Excel files.** Every customer uses its own template (different columns,
   order, header language and date formats). They arrive as email attachments
   or are dropped into a shared folder.
2. **Email.** Free or semi-structured text in the message body, sometimes
   with the Excel attached, sometimes with the data only in the text. A
   dedicated orders mailbox has existed for years (*confirmed*).

Today three people in the back office (Pili, Rosa and Carmen) read every order
and key it into Logiwin by hand, remarks included, into a free-text field
(*confirmed*). This causes:

- **Transcription errors** in addresses, weights and quantities, discovered
  when the truck is already on the road. Today about 4 in every 100 orders
  have something wrong: address, weight or a repeat (*confirmed*).
- **Duplicate orders** when a customer resends the same email or corrects the
  Excel and sends it again. Logiwin accepts them and they reach invoicing: at
  month end the customer calls about a shipment invoiced twice (*confirmed*).
- **Delays**: on Monday at 14:00 the Agroalimentaria file is still not fully
  keyed in, and at 16:00 Luis builds Tuesday's routes with whatever is there
  (*confirmed*). Afternoon orders go in the next morning.
- **No traceability**: nobody knows whether a given order was loaded, by whom,
  or from which email.

Estimated volume: 80-150 orders per day, with month-end peaks of 300
(*assumption*). The real weekly peak is Monday morning (*confirmed*).

## 3. Goal

Build an ingestion service that reads orders from both channels, normalises
them into a single model, validates them, discards duplicates and creates them
in Logiwin without human intervention in clear cases, routing doubtful ones to
a review queue **before the truck leaves**.

In the head of operations' words: the program should be the one that does not
dare, rather than loading it wrong with a straight face. Precision matters more
than the automation rate.

## 4. Success criteria

Horizon: one month after go-live. Source: interview with the head of
operations, unless stated otherwise.

| Metric | Today | Target |
| --- | --- | --- |
| Monday milestone: whole Agroalimentaria file in Logiwin | still missing at 16:00 | complete by 14:00 and Luis plans routes with everything |
| Time from receipt to creation or review queue | 2-18 h | ≤ 1 h typical, 2 h maximum |
| Orders with an error found after loading (address, weight, repeat) | 4 in 100 | ≤ 1 in 100 |
| Doubtful orders flagged before the truck leaves | 0 % | 100 % of those the system is unsure about |
| Shipments invoiced twice at month end | several per month | 0 |
| Orders with traceable origin (file / email) | 0 % | 100 % (*assumption*, not requested by the client) |

The initial criterion "≥ 80 % of orders created without manual intervention"
is withdrawn: it pushes towards loading doubtful orders, which is exactly what
the client does not want.

**Office hours saved are neither measured nor published.** The head of
operations asked for this explicitly: the figure would become an argument for
cutting staff, and the three back-office people also do everything else in the
office. Metrics are about trucks and customers.

## 5. Scope

**In scope**

- Reading `.xlsx` files from an inbox folder.
- Reading a dedicated IMAP mailbox (body and `.xlsx` attachments).
- Per-customer configurable mapping from template columns to the canonical model.
- Business validation (address, weight, date, quantity) and duplicate detection.
- Creating the order in Logiwin through its API.
- Manual review queue with notification to the back office before mid-morning.
- Audit log for every processed order.
- *Dry-run* mode to test without writing to Logiwin.

**Out of scope (for this assignment)**

- A web UI for the review queue: Logiwin itself or email will be used.
- Orders arriving as PDF, images or phone calls.
- Modifying or cancelling orders already loaded.
- Changes to Logiwin or its master data (customers, addresses).
- Cleaning up the personal-data history already sitting in the mailbox, the
  file server and Logiwin. That is a matter for management and the advisors.

## 6. Stakeholders

| Role | Who | Interest |
| --- | --- | --- |
| Head of operations | (interviewed) | Everything loaded by 14:00 on Monday, and doubtful orders visible before the truck leaves. |
| Route planning | Luis | Building the next day's routes with every order and no wrong addresses or weights. |
| Back office (3 people) | Pili, Rosa and Carmen | Stop typing; review the odd ones and call customers. Not having the project used to cut staff. |
| Management | Javier | Costs and payroll; invoice retention for the tax authority. Liaison with the advisors. |
| External advisors | (GDPR) | Retention periods and legal basis for private individuals' data. |
| IT lead | (to be identified) | A deployable, observable component that never touches Logiwin by hand. |
| End customers | Agroalimentaria, Sanz, Cerámicas, Cifuentes | Not being asked to change how they send orders. |

## 7. Constraints

- Logiwin exposes a REST API with key authentication (*assumption*); writing
  directly to its database is not allowed.
- Customer Excel templates **cannot be changed**.
- Order data contains personal data and is subject to GDPR. For B2B customers
  it is the name and phone of a warehouse manager or site foreman. For Muebles
  Cifuentes it is private individuals' data: full name, address, mobile and
  remarks such as working hours or "third floor, no lift" (*confirmed*).
- One or two months of orders in our system is enough for operations.
  Invoicing and claims live in Logiwin and need not be duplicated (*confirmed*).
- The service will run on a client-owned Linux server, with no mandatory cloud
  dependencies.

## 8. Risks and assumptions

From the initial brief:

- Free-text emails are the most ambiguous channel: the share of orders landing
  in manual review may be high at first.
- The Logiwin API may not expose everything needed (for instance duplicate
  lookup). This must be confirmed in the first week.
- Excel templates change without notice; the mapping must be configuration,
  not code.

Found in the interview:

- **Logiwin does not reject duplicates.** Today repeats get in and are
  invoiced. Deduplication has to be ours and cannot rely on the ERP.
- **It is unknown whether a Logiwin test environment exists.** Without one,
  *dry-run* is the only safety net and the first real creation happens in
  production.
- **Private individuals' data in the flow.** Keeping the original email or
  Excel for audit replicates that data. Retention and log exclusion (RNF-03)
  must also apply to the originals.
- **Nobody owns GDPR.** Nothing is deleted today: mailbox, folders and Logiwin
  accumulate years. The head of operations delegates it to management and the
  advisors. Our system can do its part, but the underlying problem is not ours.
- **The mailbox holds years of history.** Connecting IMAP needs a cut-off date,
  or thousands of old emails get reprocessed on day one.
- **The peak is one large file on a Monday.** The latency target is measured
  on that batch, not on a trickle of emails.
- **Adoption risk.** If the project is pitched as staff savings, the back
  office will see it as a threat. Metrics and messaging must stay operational.
- **Free-text remarks.** Logiwin's remarks field is an uncontrolled data
  channel. We must not dump the raw email body into it.

## 9. Deliverables

1. This brief, the requirements ([02-requirements.md](02-requirements.md)) and
   the as-is / to-be process ([03-process.md](03-process.md)).
2. Architecture decisions recorded as ADRs ([adr/](adr/README.md)).
3. Handoff document ([04-handoff.md](04-handoff.md)).
4. Source code with tests and CI.
5. Deployment and operations guide (pending).
