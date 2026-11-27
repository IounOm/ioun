# Delivery discipline (machine-wide)

> Loaded every session by the riaproi plugin. Tier router, gates, ship and context rules.

## Default delivery flow — tier router, chain it yourself  ⭐

Tier every task before the first edit; raise mid-flight, never lower. Fuzzy spec → `riaproi:grill-with-docs` first (the user can force it); big/risky → GitHub issue first; one issue → one PR, unrelated work → its own PR.

| Tier | When | Path |
|---|---|---|
| Trivial | docs/copy/config, no behavior change | format/lint → commit |
| Small | one behavior, obvious spec | main thread → ROOT verify gate + gate skills as touched → `/code-review` (low/medium) → CI green → live smoke if a deployed path changed |
| Feature | new capability, several packages | plan first (plan mode; `riaproi:task-planner` for big or fuzzy work) → build in the main thread → ROOT verify gate + gate skills as touched → `/code-review` → CI green. `riaproi:feature-lead` (agent team) ONLY when the user explicitly asks for it |
| Risky | any `riaproi:security-auditor` trigger (list: its description) — incl. granting an agent/automation NEW tool/file/permission access — or a migration | Feature path + mandatory `riaproi:spec-challenger` (on the plan) and `riaproi:security-auditor` (on the diff); `riaproi:feature-lead` only when the user asks (then `riaproi:release-gatekeeper` runs too) |

Lead-written code gets the same reviewers. Ignore mid-edit IDE diagnostics; trust the gate.

## Change discipline — gates before committing  ⭐ IMPORTANT

After any add/edit/delete, run the gates before committing/pushing. **Invoke each skill — its full criteria live there; don't reconstruct from memory:**

- **`riaproi:i18n-guard`** (always) — every user-facing string through ONE i18n layer, no hardcoded words, key-set parity across locales; external-facing projects need the layer even with one language.
- **`riaproi:verify-changes`** (always) — the project's own typecheck / lint / test / build / smoke gate.
- **`format` / Prettier discipline** (always, all repos) — style is a GATE, not taste: every repo ships `.prettierrc.json` with `"singleAttributePerLine": true` + printWidth ≤100, and `prettier --check .` in its `verify` script + CI; fix with `bun run format`, never by hand-wrapping. Python code → `ruff format --check` instead; a Python-only repo adds no `package.json` just for Prettier (detail: `riaproi:verify-changes` § Notes).
- **README discipline** (always — new project, or any code change that alters setup, config, API, user-facing features, structure, deploy or data flow): update `README.md` in the same PR, following `standards/readme-and-diagram-standard.md` — language follows the readers, the standard section order, diagrams in **Mermaid** (never ASCII art), check every claim against the code.
- **`riaproi:media-lifecycle`** (only when user-uploaded media is touched) — stage, don't eager-upload · no orphan storage objects · every shown image = lightbox.
- **`riaproi:design-system`** (only when UI styling is touched) — every color/font via the project's design tokens, never hardcoded; missing role → add a token at the single source of truth.
- **`riaproi:money` / price discipline** (whenever money/price is calculated OR displayed — matters a lot, don't let it slide) — ALL money via ONE helper per app (`lib/money.ts` or equiv): **2 decimals always**, **Half-Up `ROUND(x,2)`**, the helper owns currency **symbol + decimals** (default THB; never raw `฿`/`$` strings), price inputs `type=number step=0.01` parsed via the helper; enforce with a `check:money` build gate. Spec: `standards/money-rounding-standard.md`.

**Run the gates yourself. Before any `git push`, show the user what will be pushed and ask them to confirm** — unless they already told you to push in this task. (The git-gate hook on commit/push is only a non-blocking reminder.)

## Ship discipline — CI / build / deploy frugality  ⭐ IMPORTANT

**Never trigger a build/CI/deploy for a change that can't affect the build output** (CI minutes and cloud builds cost real money). Wiring is per-project: bake it into the project scaffold, retrofit older repos as touched; each repo's `AGENTS.md` documents its specifics.

- **Doc/config-only edits must not build** — `paths-ignore` (GitHub Actions) + per-app "Ignored Build Step" (Vercel/monorepo). A cheap lint/format/test `verify` job may still run on every PR (it checks docs too): skip the build and deploy, not the gate.
- **Verify locally before push** — `riaproi:verify-changes` green locally first; CI is the *last* gate.
- **Never push directly to a branch that auto-deploys prod** — branch → PR → CI → merge — guard it with a local `pre-push` hook. Non-deploying branches: direct trivial edits are fine.
- **CI babysit — the session that pushes a PR OWNS its checks:** watch every push to green (`gh pr checks --watch`) before moving on. Red → `gh run view <id> --log-failed`, rerun once (flaky vs real), then fix + push — **max 2 fix attempts**, then stop and report. Never weaken/skip a test to force green.
- **Pick a merge method on purpose** — solo + live-prod default = **merge-commit** (blame/bisect history, `revert -m 1` per feature, `log --first-parent` for the clean view).
- **Concurrent sessions → one `git worktree` each, never share a working tree** (builder agents too: `riaproi:feature-lead` § Fan-out rules). **AUTO-CHECK — every session, unprompted**, before the first edit/branch/commit in any repo: (a) `git status` changes you didn't make · (b) a branch you didn't create · (c) user mentions parallel work / another session known active here · (d) other worktrees in `git worktree list`. ANY signal → tell the user and propose a worktree (`EnterWorktree`); create it once they agree (`.claude/worktrees/<name>` off `origin/<default>`, one branch = one worktree; fresh tree → `bun install` + copy the gitignored `.env` before gates; rename the auto `worktree-*` branch to `feat/...` before the PR); no signal + clean tree → main checkout is fine. Remove a worktree once its PR merges. Why + raw git: `standards/git-worktree-parallel-sessions.md`.
- **Issue claim protocol — GitHub is the lock (multi-session repos).** Before starting ANY issue, verify it's unclaimed — an `in-progress` label or an existing `*-<n>` branch (`gh issue view <n>` labels/comments/linked branches, `git branch -a | grep -- "-<n>"`) = taken → pick another (the user's explicit routing overrides). Claim BEFORE coding so every session/machine sees it before the first edit: add the `in-progress` label (create it once per repo) AND, once the user agrees, push `<type>/<slug>-<n>` to origin. Label off on PR merge, or when you abandon it.
- **Building ANY automation/loop → follow the loop litmus, unprompted**: machine-checkable gate, never taste-based work · run it manually once before automating · always a budget/iteration cap · deterministic steps = shell script, LLM only where judgment is needed · climb **L1 Report → L2 Assisted → L3 Unattended**, never start at L3 · content-synthesis writes (knowledge notes, money/trading, prod data) stay human-confirmed · **no comprehension debt**: an entry in the scripts README + an explanation the user can repeat back, or it doesn't ship.

## Context / token hygiene — every session  ⭐

Context is the budget — bloat costs tokens AND quality (lost-in-the-middle).

- **One session = one task** — `/clear` when switching topics, don't drag unrelated history; `/compact` (with a focus) at ~60%, not at the 95% auto-trigger.
- **Surgical context** — `@file` / a specific function, not "the whole project"; paste only the relevant slice; cap verbose command output.
- **Delegate read-heavy work** (broad search, audits, log/test processing) to a subagent — only the summary returns; Haiku for trivial/scan/format subagents; skip it for 1–2 known files (startup isn't free; nested agents ≈ 7–10× tokens).
- **Right model** — start on a cheaper model, the higher tier plans + reviews; climb one rung only when the current one cannot fix or answer correctly, then step back down. Agent routing + escalation triggers: `riaproi:feature-lead` § Orchestration rules. Mechanical execution → suggest lowering `/effort`.
- **AGENTS.md = lean index (<200 lines)** — stack, key commands, conventions; **link** to docs/code, don't copy. Durable decisions → `docs/adr/`, not AGENTS.md.
- **English-only is mandatory for the whole AI-instruction layer** — every `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, tooling `README.md`, and command/skill definition (`.claude*/commands|skills/**`), independent of the conversation language. Other languages stay ONLY in: doc bodies + `docs/*`, a project `README.md` whose readers use that language, script user-facing output, and proper nouns.
- **CLI > MCP** where one exists; scope a project's MCP to its `.mcp.json`, not global.
- **Plan before big edits** (plan mode); don't edit until confident — ask first.
