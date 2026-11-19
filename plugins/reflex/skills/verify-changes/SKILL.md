---
name: verify-changes
description: Run the project's full verification gate before committing — typecheck, lint, test, build, and smoke checks. Auto-detects the package manager / ecosystem and runs only the checks that actually exist (stack-agnostic; JS/TS first-class with fallbacks for Rust/Go/Python/Make). Invoke after making code changes and before committing/pushing.
---

# verify-changes

Verify that code changes are sound by running the **project's own** checks — never
assume a fixed toolchain. Detect first, then run only what exists, in order, and
report each result. The goal: catch type/lint/test/build/runtime breakage before a
commit, in any repo, regardless of stack.

## 1. Locate the package to verify
- Default to the directory where the changes were made.
- **Monorepo:** the per-package gate (inside the workspace package that changed — a
  nested folder with its own manifest: `package.json`, `Cargo.toml`, `go.mod`,
  `pyproject.toml`) is the **inner loop** while iterating (agent builders: § Builder inner-loop gate). **Before pushing, and after
  any multi-package or agent fan-out change, run the ROOT composite gate** (the root
  `verify`/`ci` script) — per-package gates miss cross-package breaks (e.g. an RSC/client
  boundary error only the app build sees).

## 2. Detect the toolchain — do NOT hardcode
Inspect the target dir (walk up for the lockfile):

- **JS/TS package manager** — choose by lockfile, in this order:
  `bun.lock`/`bun.lockb` → `bun` · `pnpm-lock.yaml` → `pnpm` · `yarn.lock` → `yarn`
  · `package-lock.json` → `npm`. If `package.json` has a `packageManager` field,
  prefer it. Derive the commands:
  - run a script = `<pm> run <name>`
  - run a binary = `bun x …` / `pnpm exec …` / `yarn …` / `npx …`
- **No `package.json`?** Detect the ecosystem and use its equivalents:
  `Cargo.toml` → `cargo check`/`clippy`/`test`/`build` · `go.mod` → `go vet`/`go test ./...`/`go build ./...`
  · `pyproject.toml`/`setup.cfg` → `ruff`/`mypy`/`pytest` · `Makefile` → `make check`/`make test`/`make build`.
- **Prefer a project-provided composite** if one exists (a `verify` / `ci` / `check`
  script or `make ci`) — run that instead of re-deriving the steps below.

## 3. Run the gate — only the steps that exist, in order
Read the manifest to discover the **actual** script names (don't assume `lint`/`test`/
`build` exist — some repos use `check`, `typecheck`, `ci`, …). Run each present step;
**stop at the first failure**, surface its output, fix, then re-run from the top.

1. **Typecheck** — JS/TS: if `tsconfig.json` + `typescript` are present →
   `<pm-exec> tsc --noEmit`. (Else: `cargo check`, `go vet`, `mypy`, …)
2. **Lint** — if a lint script exists → `<pm> run <lint-script>`. (Else: `clippy`,
   `ruff check`, `golangci-lint run`, …)
3. **Test** — if a test script exists → `<pm> run <test-script>`. (Else: `cargo test`,
   `go test ./...`, `pytest`, …)
4. **Build** — if a build script exists → `<pm> run <build-script>`. (Else: `cargo build`,
   `go build ./...`, …)
5. **Smoke** — if the repo has smoke scripts (`scripts/smoke*`, or a `smoke`/`smoke:*`
   script), run them. Smoke often needs env/services (a DB URL, a running stack, an
   API key). If the required env is **absent, skip and say so** — do not fail the gate
   on missing local infra, and **never invent credentials**. Surface where the env is
   expected to come from.

## 4. Report
One line per step, e.g.:
```
✓ typecheck   ✓ lint   ✓ test (50 passed)   ✓ build   ⊘ smoke (skipped — no DB env)
```
- All green → state the gate passed and it's safe to commit/push.
- Any failure → show the failing output and **stop; do not commit**.

## Builder inner-loop gate (per package)

Fan-out builders (and any agent iterating inside one package) run ONE per-package gate command, never an ad-hoc chain of greps and pipes. A project-provided script wins; otherwise the lead composes it from the detection above and pastes it into the builder's task card (`reflex:feature-lead` § Fan-out rules).

- **Order:** format-write on the changed files → lint → typecheck → tests. Format/lint caught 0 functional defects in the measured run (one measured run: 38 prettier + 30 eslint runs), so they run ONCE at the end of a change set — fix with `--write`, never a `--check` rerun loop.
- **Limits:** every step under a timeout (outer `timeout`/`gtimeout`; the runner's per-test timeout, e.g. `bun test --timeout 10000`). A timeout or hang is a FAILURE: diagnose open handles (unresolved promises, un-aborted fetches, live timers) — never rerun an unchanged hanging command.
- **Output:** failure-only — one line per passing step; a failing step prints its failing lines + counts (≤ ~30 lines). No `| grep`/`| tail` that can hide the failing line.
- **Cadence:** targeted tests while iterating red → green; the whole gate once per change set, with the FULL package suite (4-11 s measured — never cut it).
- The ROOT composite gate (§ Locate the package to verify) stays the lead's job.
- **Lead only — same tree already green → cite, don't rerun:** when a reviewer already ran the gate green on the exact tree (`git rev-parse HEAD^{tree}` + empty `git status --porcelain` match the logged run), the LEAD cites that run (tree hash + log path) instead of repeating it. Never for builders (their inner-loop gate is their own evidence) and never for CI or the deploy host (different OS, own run).

## Notes
- This is read-then-act: inspect the manifest/lockfile first, then run.
- Keep it the project's checks, not yours — if the repo has no test/build script,
  skip that step rather than inventing one.
- For long steps, prefer running them in the background or with a sensible timeout,
  and report the tail of the output.
- **Scale to the change.** A docs/markdown/comment-only change doesn't need a full
  build+test+smoke — run what the change can actually break (e.g. lint/format) and say
  which steps you skipped and why. Code changes get the full gate. (CI is the backstop.)
- **Enforcement vs guidance:** this skill is the *procedure*. Run it yourself before
  pushing; ask the user before the push itself (unless they already told you to push). The machine-wide `PreToolUse`
  git hook (the reflex git-gate hook) only *reminds* on commit/push (non-blocking).
- Pairs with **i18n-guard**: verify-changes checks the code, i18n-guard checks the words
  (no hardcoded strings, every locale complete). Run both before pushing.
- **Prettier discipline** (rule line in `rules/delivery.md` § Change discipline): every repo ships
  `.prettierrc.json` with
  `"singleAttributePerLine": true` (+ printWidth ≤100). Any JSX element with ≥2 props, and any
  style/sx object that outgrows the line, then breaks onto multiple lines instead of running long.
  `prettier --check .` is wired into the repo's `verify` script and CI. Fix with `bun run format`,
  never by hand-wrapping.
