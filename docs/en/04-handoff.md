# Handoff — State of the assignment and how to continue

> FDE course · Assignment 01 · [Versión en español](../es/04-handoff.md)
>
> For whoever picks up the assignment from here, person or agent.
> Last updated: 2026-10-19.

## 1. In one sentence

A service that reads orders from Excel and email, validates them, removes
repeats and creates them in Logiwin, sending anything it is unsure about to
review before Luis builds routes at 14:00.

## 2. Where everything is

| What | Where |
| --- | --- |
| Client context and success criteria | [01-brief.md](01-brief.md) |
| Requirements with confirmed / assumed status and open questions | [02-requirements.md](02-requirements.md) |
| As-is and to-be process with diagrams | [03-process.md](03-process.md) |
| Architecture decisions | [adr/README.md](adr/README.md) |
| Code | `src/` (entry point only; canonical model, sources and ERP client come in the next steps) |
| Tests and CI | `test/` (vitest; `acceptance/` and `fixtures/` empty), `.github/workflows/ci.yml` (check `test`: Biome, tsc, vitest) |

Every document exists in Spanish and English and must be kept in sync.

## 3. What we already know that was not in the brief

From the interview with the head of operations (October 2026):

- The ERP is Logiwin. It keeps everything since 2017. It has a free-text
  remarks field.
- The back office is three people (Pili, Rosa, Carmen), not two. Luis builds
  routes. Javier is management and talks to the GDPR advisors.
- The peak is Monday: Agroalimentaria's Excel. The milestone is having it
  fully in by 14:00. Acceptable latency: 1 hour, 2 at most.
- Today 4 in 100 orders have an error (address, weight, repeat). Target: 1 in
  100, and doubtful ones visible before the truck leaves.
- Repeats get into Logiwin today and are invoiced twice.
- Muebles Cifuentes sends private individuals' data (name, address, mobile,
  sensitive remarks). Nobody has decided how long to keep it.
- Office-hour savings are not published. It is a condition set by the head of
  operations.

## 4. Decisions made

- ADR-0001: decisions as ADRs in MADR format. Accepted.
- ADR-0002: Node 22 with strict TypeScript, pnpm, vitest and Biome. Accepted.
  The initial Python skeleton was removed with no logic written. Node runs the
  `.ts` files directly; `tsc` only checks types.
- Precision over coverage: no auto-creation percentage target (RNF-10). The
  brief's "≥ 80 %" was withdrawn.
- Deduplication is ours, not delegated to Logiwin (RF-06).
- Retention: 60 days for originals and consumer orders, 90 for the rest,
  unless the advisors say otherwise (RNF-03).
- Only filtered `notes` reaches Logiwin's remarks field, never the whole
  email (AC-05.4).

## 5. What we do not know and what it blocks

The full list is in [02-requirements.md](02-requirements.md#5-open-questions).
The ones that shape the design before code is written:

| Question | Owner | What it blocks |
| --- | --- | --- |
| Q1 / Q6: does the Logiwin API search by reference and accept repeats? | IT lead, Javier | ERP client and deduplication design |
| Q7: is there a Logiwin test environment? | IT lead | Test plan and first go-live |
| Q3: which templates exist and which carry their own reference? | Back office | Per-customer mapping and fallback duplicate key (AC-06.4) |
| Q8: how many rows does the Monday file carry? | Back office | Whether RNF-05 is realistic |
| Q13: how to tell a home delivery in the Cifuentes file? | Back office | `delivery_is_consumer` and short retention |
| Q14: legal retention period for private individuals' data | Javier and advisors | Confirm or change the 60 days |

For Q3, Q8 and Q13 the fastest route is asking the back office for one real
Excel per customer (anonymised if needed) and three or four real order emails.
They go in `samples/`, which is empty today.

## 6. Recommended next step

1. Obtain real Excel and email samples and put them in `samples/` and
   `test/fixtures/`.
2. Implement in this order, each step with tests: canonical model and
   normalisation (RF-03), Excel parsing (RF-01), validation (RF-04),
   deduplication (RF-06), review queue and notification (RF-07), Logiwin
   client in dry-run mode (RF-05), email (RF-02).
3. First trial with the client: one Monday, in dry-run, against the real
   Agroalimentaria file. Measure how long it takes and how many orders go to
   review.

## 7. Things not to do

- Do not pitch the project as staff savings, in metrics or in reports.
- Do not load an order "just in case". When in doubt, review queue.
- Do not connect IMAP without a cut-off date: the mailbox holds years of
  emails.
- Do not dump the email body into Logiwin's remarks.
- Do not write personal data to logs.
- Do not touch Logiwin's history, the mailbox or the server folders: that
  belongs to management and the advisors.

## 8. Repository conventions

- `main` is protected: changes land only through a PR with the `test`
  check green. Applies to admins too.
- Bilingual docs, same files in `docs/es` and `docs/en`.
- ADRs in MADR format, numbered, with a version in both languages.
- RF-xx, RNF-xx, AC-xx and Qx identifiers are stable: they are cited in
  commits, PRs and ADRs.
- Changes are left staged in the git index; no commits are made unless the
  repository owner asks for them.
