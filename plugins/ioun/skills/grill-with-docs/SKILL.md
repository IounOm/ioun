---
name: grill-with-docs
description: Interview the owner in short rounds until the requirement is actually settled, writing each resolved fact into its durable home the moment it resolves — project vocabulary into the repo's CONTEXT.md glossary, qualifying decisions into docs/adr/. For a brand-new project or standalone capability it opens with a prior-art build-vs-buy sweep (does an existing system already cover this?) before any grilling round. Invoke BEFORE starting a large or fuzzy feature or a new project, or when the user types /grill-with-docs. Skip for small tasks with an obvious spec.
---

# grill-with-docs — settle the requirement before building (formerly grill-me)

Vibe-input is the content-side of vibe-coding: building (or publishing claims) from a
casual telling without interrogating it. This skill is the antidote: a short,
stateful interview that leaves docs on disk as it goes. Inspired by Matt Pocock's
grilling/grill-with-docs/domain-modeling, adapted so the paper trail lands where
the project keeps truth (repo docs, ADRs, the issue tracker).

## Method

1. **Read before asking.** Anything the repo, its docs, or git history can answer, answer
   by reading it. Questions to the owner are only for what lives in their head
   (intent, priorities, real-world facts, taste). Check the repo `docs/` and
   the project's issue / epic first — the answer may already be recorded.
1b. **Prior-art sweep — the build-vs-buy gate (new projects / new standalone
   capabilities only).** Before the first grilling round, research externally
   (WebSearch / a background research subagent — this is a FACT question per 2b,
   it never blocks the owner): does an existing product, OSS project, or template
   already cover the core job? For each serious candidate record its features —
   what it can and cannot do — and how it differs from what the owner wants to
   build. Then put the DECISION to the owner with a recommendation: candidate is
   not meaningfully different, or can be adopted/combined with our system → don't
   build, adopt or integrate instead. Building wins only when (a) the
   differentiation is real (the project IS the product), (b) the goal is
   deliberate learning, or (c) every candidate breaks a hard constraint
   (privacy, cost, solo-manageability). Rationale: self-building pays hidden
   costs — learning curve, trial-and-error, and all maintenance forever — that a
   vendor/OSS maintainer has already paid across many users. The verdict is a
   classic ADR (non-obvious rejected alternative); list the tools evaluated in
   that ADR so the research is never repeated. Skip for
   features inside an existing project — step 1 (reading the repo) covers those.
2. **Ask in rounds, not a dump — and each round is the frontier.** A round contains
   only the questions whose prerequisites are already settled (2–4 of them; use
   AskUserQuestion when interactive, with a recommended option first). Wait. Let the
   answers open the next frontier. Stop when a round produces nothing new.
   Dependent questions in the same round is the failure mode.
2b. **Split facts from decisions.** A FACT question (verifiable in the world, a repo,
   or a doc) goes to a background subagent or a read — never to the owner. Only
   DECISION questions (taste, priority, intent, ground truth of their own life)
   block on the owner. If the blocking knowledge is in a THIRD PARTY's head (client,
   family member, teammate), don't guess and don't grill the owner — emit a short
   questionnaire file (most-important-first, "I don't know" explicitly licensed)
   for the owner to deliver to that person, and mark the plan blocked on it.
3. **Challenge, don't transcribe.** If an answer conflicts with recorded truth
   (a published rule, an earlier decision), surface the conflict now —
   that is the whole point of grilling. Watch especially for scope/role inflation
   and for names that publish rules say cannot appear.
   Three domain-modeling moves belong in every round:
   - **Term-conflict callout.** The owner uses a word that clashes with the repo's
     glossary or an earlier definition → call it out immediately: "CONTEXT.md defines
     'cancellation' as X, but you seem to mean Y — which is it?" Vague or overloaded
     terms ("account", "sync") → propose one canonical term and get it picked.
   - **Cross-reference the code.** When the owner states how something works, check
     whether the code agrees before accepting it. "The code cancels whole orders, but
     you just said partial cancellation exists — which is right?"
   - **Stress-test with scenarios.** When domain relationships come up, invent a
     concrete edge case that forces the boundary to be precise, instead of accepting
     the happy-path description.
4. **Write as it resolves — not at the end.** Each resolved fact goes to its durable
   home immediately:

   | What resolved | Where it lands |
   |---|---|
   | Repo-technical decision (hard to reverse + surprising + real trade-off) | `docs/adr/NNNN-slug.md` (format below) + one line in the project's issue / epic — all three gates or it does not qualify; most sessions produce ZERO ADRs |
   | Project vocabulary the team will reuse | repo `CONTEXT.md` glossary (format below), created lazily on the first resolved term |
   | Everything else | the working plan for THIS task only — restate it in the final plan, never leave it implied |

5. **Close by restating.** End the interview by playing the settled plan back in a
   few sentences. If the owner corrects the restatement, the interview is not done.

## Docs the interview leaves behind (project repos only)

The bulk of what was agreed otherwise exists only in the context window it was
agreed in. Two artifact types survive the session:

**Repo `CONTEXT.md` = glossary, nothing else.** Not a spec, not a scratch pad, no
implementation details. One entry per resolved term:

```md
**Order**:
A confirmed request to purchase, after payment. _Avoid_: purchase, transaction
```

Be opinionated — pick ONE canonical word, list the losers under `_Avoid_`. Tight
definitions (what it IS, 1–2 sentences). Only terms specific to THIS project's
domain; general programming concepts never qualify. Create the file lazily when the
first term resolves.

**`docs/adr/NNNN-slug.md`** — sequential numbering, created lazily. An ADR is 1–3
sentences: context, decision, why. No section boilerplate. Qualifies only when all
three gates pass (hard to reverse + surprising without context + real trade-off).
Typical qualifiers: architectural shape, tech choices with lock-in, boundary
decisions, deliberate deviations from the obvious path, constraints invisible in
the code, non-obvious rejected alternatives (so nobody re-proposes GraphQL in six
months).

## It's working if

- The owner answers fewer questions each round, and the last round is corrections
  to your restatement, not new information.
- Durable files changed DURING the session, one fact at a time.
- At least one question challenged something instead of collecting it.
- Small tasks never see this skill — invoking it on a one-line fix is the failure mode.
- Zero ADRs in most sessions is normal; an ADR for every decision means the three
  gates are not being applied.

## Relationship to the rest of the system

Runs BEFORE plan mode / implementation; it feeds them. The gates
(`ioun:verify-changes`, review, publish rules) remain the last line — this skill
exists so they stop being the first place over-claims get caught.
