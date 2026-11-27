---
name: feature-lead
description: Run the full delivery protocol (idea to production) as the orchestrating lead - settle spec, task-planner plan, spec-challenger attack, build (single thread for coupled work, file-zoned specialist agents for decoupled chunks), per-feature verify wave with one findings ledger + evaluation gate, release-gatekeeper GO/NO-GO, deploy + live smoke, close-out summary. OPT-IN ONLY - use it only when the user explicitly asks for the agent team or this protocol ("run the team", "use feature-lead", "ใช้ทีม agent"). Never start it on your own because a task looks big: Feature/Risky-tier work runs in the main thread per rules/delivery.md. It spawns several high-tier agents and uses a lot of quota.
---

# feature-lead — delivery protocol for Feature/Risky-tier work
> **Opt-in only.** Run this protocol only when the user asked for it; otherwise follow the Feature/Risky path in `rules/delivery.md` in the main thread.

You (the main session) are the lead: you orchestrate, arbitrate, and hold the whole picture — never delegate that. The protocol exists so a big feature ships **rigorously checked at every seam — not happy-path-only**.

**Single source of truth:** this file owns every stage fact; other flow facts live elsewhere and are linked, never restated.

## Phase gates (each phase ends with an explicit check before the next)

**P1 · Spec** — requirement fuzzy? run `riaproi:grill-with-docs` until settled. UI/layout specs: settle the layout with the user in THIS thread (≤ ~40-line ASCII options) before spawning any spec/issue writer; batch later user changes into ONE revision message. Gate: the user confirms the spec. User away → autonomous-defaults mode: take the conservative option per open decision (one named constant each), list them as DECISION-NEEDED in the plan (P3 GAPS join it), build proceeds — but P6 treats every unruled item as a blocker (defaults ≠ approval).

**P2 · Plan** — spawn `riaproi:task-planner` with the spec (background). Gate: plan has MVP-first phases, checkable acceptance criteria, crew map, and a "not in MVP" list.

**P3 · Challenge** — spawn `riaproi:spec-challenger` on the plan+spec, pasting the planner's open questions/rulings as "already caught — report deltas and escalations only". Fold BLOCKERS into the plan; put GAPS to the user as decisions (one message, all at once — not a drip). Gate: zero unresolved BLOCKERS, the user has ruled on GAPS. Record the settled plan as a GitHub issue per `rules/delivery.md` § Default delivery flow (no remote → commit SPEC/PLAN into the repo before P4).

**P4 · Build** — the token-economics rule governs:
- **Coupled work (default): build in THIS thread**, task by task in the plan's dependency order.
- **Decoupled chunks only** → delegate to the matching specialist (`riaproi:frontend-react`, `riaproi:backend-node`, `riaproi:db-postgres`, `riaproi:devops-cicd`), one chunk each, in parallel where independent, each briefed by a task card (Fan-out rule 2).
- FE⇄BE seam: settle the contract (types/schema) before parallelizing across it; a specialist that reports a dependency stop gets re-scoped, not re-prompted harder.
- Each task lands with its own tests and gate-cleanliness (specialists' definition of done) — never "tests later".

**Fan-out rules (≥2 parallel builders)** — origin: a real run (one helper re-implemented ×6; a build break only the root gate saw; builder time lost to reads/reruns):
1. **Contract first:** the lead writes the shared contract/types file BEFORE fan-out; builders import it, never redefine it.
2. **Task card, not the plan file:** each builder gets a self-contained card as its OWN file (target ≤ ~3k chars — self-containment beats the number; before cutting, grep every instance of each finding/class and draw zones around the class, not the folder tree, or cross-zone leftovers pile into one oversized assembly card; written by the planner as one file per card (its § Output format) and amended in place by the lead; the prompt names that path — never "your card is §N of the plan") — goal, acceptance criteria (verbatim), FILE ZONE (exact paths/globs), contract exports to import (name → file:line), the running "shared helpers" list (path → purpose) to reuse, the package gate command + the repo's committed screenshot/smoke script (none → the lead adds one before fan-out; never one rebuilt per builder), exact file:line ranges worth reading (spec/issue sections too — never "read the issue"), and every plan amendment/ruling already FOLDED IN. Builders read the plan only if the card says so.
3. **Builder contract** (binding): `builder-contract.md` beside this file — zone, batched reads + asserted edits, gate cadence, ≤ ~15-line hand-back. Builder agent files and task cards link it; never restate it.
4. **Worktree per concurrent builder:** builders on the same repo each work in their OWN git worktree off the contract commit (mechanics: `rules/delivery.md` § Ship discipline, concurrent-sessions bullet); the lead merges them.
5. **After builds land:** the LEAD runs the ROOT composite gate on the merged tree (`riaproi:verify-changes` § Locate the package to verify) — per-package green is not enough. While the tree is unchanged this run IS P5's ROOT gate; the dedupe sweep is the P5 code reviewer's job.

**P5 · Verify wave — PER FEATURE, not once at session end** — run concurrently, reviewers by tier:
- always: ROOT gate + applicable gate skills (`riaproi:verify-changes`; `riaproi:i18n-guard` / `riaproi:design-system` / `riaproi:media-lifecycle` / `riaproi:money` as touched) and ONE code review of the diff — `/code-review` after a single-thread build, the `riaproi:code-reviewer` agent after any fan-out (it is also the dedupe sweep)
- `riaproi:qa-engineer` in REPORT-ONLY mode (defined in its agent file). Wall-time lever: it may draft the matrix ∥ P4 once P3 amendments are folded — never ∥ P3 (a pre-amendment draft cost ~40k to reconcile, 0 extra bugs).
- `riaproi:security-auditor` when any of its triggers is touched (its description is the canonical list); mandatory on the Risky tier
- **one lens per reviewer, none overlapping:** code review = diff logic, duplication/reuse/dead code, render/perf, contract skew · qa-engineer = runtime behaviour under adversarial use · security-auditor = exploitability · gate skills = i18n/tokens/money/media. Each brief names the lenses already running (a combined "correctness + quality" brief re-found about a third of QA's findings)
- **lead-written code gets the same reviewers** — no exemption (a past run: HIGH holes in orchestrator-written code caught only by a dedicated reviewer)

**Ledger** — merge every finding into ONE file (scratchpad; name its path in status lines), one row each: `ID · severity (CRITICAL/HIGH/MED/LOW) · finding · owner (by file zone) · status (open/fixed/accepted) · evidence (test name / probe transcript)`. Fixes: each starts with a failing reproduction test (red → fix → green), routed to the zone's owner; for an injection/display-integrity finding the red tests cover the CLASS (every surface rendering that untrusted input × every input category the reviewer probed), not only the reported example. **RESUME that same agent (SendMessage) for its own findings AND every later fix ROUND — never spawn fresh** (~3.8k vs ~57k tokens); respawn only if it was the wrong owner or its context is spent (the task notification's `subagent_tokens` IS its current context; ≳200k → fresh agent + ≤ 15-line handover of its open ledger rows). **Balance fix waves** at ≤ ~8 findings or ~60 turns per agent, heaviest first; split a heavy zone by sub-zone. Security fixes rated MED+ go back to `riaproi:security-auditor` for re-verification (its § Re-verifying a fix); LOW/NOTE security fixes close on their red→green test + the QA re-verify spot check.

**Evaluation gate** — pass only if ALL hold: ROOT gate green · no open CRITICAL/HIGH · every MED fixed or user-accepted · every fix has a test that went red→green · live smoke of the changed entry points passes (local/preview here; prod repeats in P8). Evidence standard: verify by observation, never intention.

**Re-improve loop** — gate fails → another fix round, re-verifying what changed. **HARD CAP 2 rounds** (same as the CI-babysit cap), then STOP and hand the user the ledger. Never weaken, skip, or quarantine a test to pass.

**P6 · Release** — spawn `riaproi:release-gatekeeper`. Gate: **GO**, with accepted risks written down. A NO-GO loops its blockers back to P4/P5 — never argued away.

**P7 · Ship** — PR → CI babysat to green → merge, per `rules/delivery.md` § Ship discipline.

**P8 · Deploy + live smoke + close**
- Name the rollback (exact command/commit) BEFORE deploying; deploy with the repo's health-gated release script.
- Live HTTPS smoke on every new/changed entry point, incl. ≥1 negative case each (404/400/403) — read-only/idempotent probes, canary data only; the post-merge CI/deploy run watched to green.
- Close with a plain-language summary (what shipped, evidence, accepted risks) + a **"NOT verified — needs human eyes"** list (visual/device checks).
- **Close-out**: update the project's docs / README / issue (status, decisions, what shipped) in the same breath.

## Orchestration rules

- **Status discipline:** after each phase, one short status line to the user (phase done, key outcome, next).
- **Human-confirmed, never auto-decided:** P1 spec · P3 GAP rulings · accepting findings (P5) or risks (P6) · scope changes (immediately) · irreversible migration/data deploys · outward writes · visual/device checks. Batch them at phase gates — one message, not a drip.
- **Model routing — escalation ladder (single source — other files point here):** the higher tier PLANS and REVIEWS, the lower tier EXECUTES the plan. Execution (builders, docs) starts on **sonnet** — EXCEPT Risky-tier code chunks (sandbox, permissions/allow-rules, host command execution, auth, secrets handling), which start on **opus** (a miss there costs a review + fix + re-verify cycle, more than the opus run); planning + every correctness check (task-planner, spec-challenger, qa-engineer, security-auditor, code-quality reviewers, ledger verifiers, release-gatekeeper) runs on **opus**. **Escalate one tier when the current tier cannot fix it:** a builder reports it is stuck, OR the same gate/finding is still red after 2 fix attempts, OR a reviewer reopens the same finding after a fix round → re-run that chunk on **opus**; if opus also fails the same way → stop and report to the user. Record each escalation (chunk, starting rung, reason) in the ledger. **Re-tune rule:** if >~30% of sonnet-started chunks escalate to opus across a run, sonnet is not paying for itself — switch the default execution rung to opus (update this line + the builder agents' `model:` frontmatter). Agent files' `model:` frontmatter is the ladder's starting rung; escalate by spawning/resuming with a model override.
- **Scope guard:** work not in the plan doesn't get built silently — it's a plan change the user sees. MVP boundary is defended by you.
- **Context budget** (a measured audit: 238M tokens, 97% context re-send): every turn re-sends the agent's whole context, so cost ≈ turns × context. Size delegated cards to ≤ ~80 turns / ~200k context (split bigger ones — incl. a foundation wave — into sequential or sub-zone cards); log each card's final context · tool calls · minutes in the ledger so the budget is measured, not assumed. `/compact` is user-typed (the lead can't run it): at each feature boundary (after P8, before the next P1) AND once the lead's own context passes ~40% of its window (`rules/delivery.md`'s ~60% is the ceiling, not the target), the lead writes its checkpoint file and asks the user to `/compact <focus>` or open a fresh session — re-asked in every later status line until done; auto-compact is only the fallback (measured: lead mean 540k, max 909k over 266 calls ≈ 144M tokens). Keep the lead's intake lean: hand-backs per the Builder contract; no LSP diagnostics during fan-out (they reach only the lead).
- **No ceremony inflation:** phases collapse when trivially satisfied (a settled spec skips P1; a one-crew build needs no crew table) — but P5, P6 and P8 never collapse, and on the Risky tier neither does P3.
