---
name: project-structure
description: Audit or reshape a codebase's folder structure and layer boundaries. Use when a project's folders have gone flat or ambiguous (a lib/ or utils/ holding dozens of files), when adding a new subsystem and unsure where files go, before a restructure, or when reviewing whether business logic, data access, and UI are actually separated. Maps the backend layers (router/controller/service/model/migration/job/guard/validation) onto whatever the framework calls them, checks that every public entry point has authn + authz + an input contract, and enforces import direction with lint rather than prose. Stack-agnostic; knows Next.js App Router specifics. Rejects over-architecture as firmly as it rejects flat dumping grounds.
---

# project-structure

A folder tree is a **claim about dependencies**. If the tree says "these are separate
layers" but nothing stops layer 3 from importing layer 1, the tree is decoration.

Two failure modes, both common, and this skill rejects both:
- **Flat dumping ground** — `lib/` with 160 files; the layering exists only in filenames.
- **Ceremony cargo-cult** — `repositories/` + `use-cases/` + DI containers copied from a
  framework with a network boundary this codebase doesn't have.

The target is the smallest structure where **every rule is machine-checkable**.

## 0. Detect before proposing (never skip)

- **Framework + routing model.** Does a folder define URLs? (Next.js `app/`, Rails
  `config/routes.rb`, SvelteKit `routes/`.) Routing folders are **not** free to rearrange.
- **Source roots.** `src/`? bare `app/`+`lib/`? monorepo `apps/*` + `packages/*`?
  Don't hardcode `src/`.
- **Existing conventions.** Read the project's own `AGENTS.md`/`CLAUDE.md`/`CONTRIBUTING`/`README`
  first. A convention already written down and followed beats your preferred taxonomy.
- **What already enforces boundaries.** `server-only`, `.server.ts`, ESLint zones,
  build gates, package boundaries. If something is already enforced at runtime, keep it.
- **Scale.** Team size and file count decide how much structure is worth it. A 2-person
  repo does not get a DI container.

## 1. Routing folders are URLs, not organization

In file-routed frameworks the route tree is a **public contract**. Never "tidy" it.

- Reorganize *without* changing URLs using route groups (`(group)` in Next.js).
- Non-route files belong in a private folder (`_components/`, `_lib/`) or outside the
  route tree — never as a bare sibling of real routes. A folder under `app/` that holds
  only assets or only actions is a smell: it reads as a route and isn't one.
- Colocating a route's own components/actions beside its page is **correct**, not clutter.

## 2. Flat-folder budget

**A folder with more than ~20 files must be split.** No exceptions for "it's all utils."
Split by domain, not by file-type — `orders/`, `payroll/`, not `types/`, `constants/`.

Count before you argue:
```
find . -type d \( -name node_modules -o -name .next -o -name dist \) -prune -o -type d -print \
  | while read -r d; do n=$(ls -1 "$d" 2>/dev/null | wc -l); [ "$n" -gt 20 ] && echo "$n $d"; done | sort -rn
```

## 3. Two axes decide every file's home

| | **feature** (one domain) | **cross-feature** | **agnostic** (no business knowledge) |
|---|---|---|---|
| **server** (DB/secrets) | `server/services/<feature>/` | `server/{auth,storage,jobs}/` | — |
| **pure** (no I/O, no UI) | `domain/<feature>/` | `shared/` | `shared/` |
| **view** (UI) | `features/<feature>/components/` | `features/<feature>/components/` | `ui/` |

If a file fits two cells, it does two jobs — **split the file, don't invent a folder.**

## 4. Direction of dependency — one way only

`app/routes → features → domain → shared`, and `app/routes → server → domain → shared`.

Every arrow that points backwards is a defect, especially these three:
- a **shared/design-system** component importing a route's handler or action
- a **data/query module** importing types from a **UI component** (the model layer
  doesn't exist; entities live in React files and can't be tested)
- two sibling **features** importing each other directly (promote to `shared/`/`domain/`)

Enforce with lint, e.g. ESLint `import/no-restricted-paths` zones, Nx tags, or package
boundaries. **A rule that lives only in a markdown file is not a rule.**

## 5. Backend layers — map them before claiming they're missing

Frameworks scatter the backend; that isn't the same as not having one. Fill this table
for the actual repo before proposing anything:

| Layer | Where in THIS repo | Notes |
|---|---|---|
| Router / endpoint | ? | route handlers, server actions, controllers |
| Controller | ? | should be thin: parse → guard → service → respond |
| Service / use-case | ? | owns transactions and business steps |
| Model / entity | ? | ORM schema, CMS collections |
| Migration | ? | schema is owned by migrations, never hand-edited |
| Guard (authn/authz) | ? | one capability map, one choke point |
| Input contract | ? | ← most often **missing entirely** |
| Job / cron | ? | logic in a module; the route only checks the secret |
| Middleware | ? | |

Red flags: a page/route reading the DB directly · a controller with business logic ·
a service that renders text · one schema file over ~500 lines or ~20 tables.

## 6. Every public entry point needs three gates

A server action / route handler is a **public HTTP endpoint**, callable without the UI.

1. **authn** — who is this
2. **authz** — may they do it (from one capability map, not an inline role compare)
3. **input contract** — is the payload the right shape ← **types do not count**

TypeScript types are erased at compile time. `fn(input: CreateOrderInput)` validates
nothing at runtime. Use a runtime schema (zod/valibot/…) at the boundary, colocated as
`contracts/` (or `dto/`) next to the services, and derive the TS type from it.

Guards must be **one idiom**. Count them; a codebase with three (`requireCap()`, hand-rolled
`getUser()+can()`, raw `throw new Error('...')`) will drift. Also check that user-facing
error text survives production — many frameworks redact thrown messages, so user copy has
to be **returned** or carried in a structured error, not thrown as a plain string.

## 7. Public writes need a spam guard

Any endpoint that unauthenticated users may write to — contact form, signup, webhook —
needs rate limiting and/or a honeypot **especially when it triggers email/push/spend**.
Also check field-level access: a public create must not let the caller set `status`,
`role`, `isAdmin`, or any workflow field, and text fields need a max length.

## 8. Types live with their owner

A global `types/` bucket for domain types causes circular imports, drift from the
derived source, and orphaned types nobody dares delete. Reserve `types/` for **ambient
`.d.ts` declarations only**.

| Type | Home |
|---|---|
| DB row (derived) | with the schema |
| Input contract | `contracts/*` (source of truth; infer the TS type from it) |
| Domain entity / value object | `domain/<feature>/*.types.ts` |
| Component props | in the component file |
| Ambient / global | `types/*.d.ts` |

## 9. Naming — pick words with exactly one meaning

Banned as folder names because they all mean "anything": **`utils/` `helpers/` `core/`
`common/` `misc/`**, and `lib/` when it is the catch-all rather than a real boundary.
Keep exactly one cross-cutting bucket and name it once (`shared/`).

Test: *"a new file arrives — is there exactly one folder it belongs in?"* Two answers =
the names are wrong.

## 10. Monorepo drift

Same-named helper in two apps = diff them. If they've diverged, that's a bug already
shipped, not a future risk. Promote to a shared package **only when both apps use it
today** — otherwise the package becomes the new dumping ground.
```
# same basename in two apps → candidates
find apps -name '*.ts' -not -path '*/node_modules/*' -exec basename {} \; | sort | uniq -d
```

## 11. Reject over-architecture, with reasons

Do **not** add repository interfaces, use-case classes, or DI containers when:
- there is a single data source in the same process (an ORM call is already the repository)
- the framework's own model is "the server component/handler fetches" (adding a container
  fights the framework)
- the abstraction would add 3–4 files per query for a team of one or two

Say which specific benefit is being bought and what it costs in files. If the answer is
"testability", check whether a pure-logic split already delivers it more cheaply.

## 12. Migration discipline (when actually restructuring)

1. **Land the lint rules first, as warnings**, on the *current* layout. The violation
   count is the argument for (or against) the restructure.
2. **Fix direction-of-dependency defects before moving anything** — they're real bugs.
3. **One PR per group. Moves only — zero logic changes.** Otherwise review can't tell a
   rename from a behavior change.
4. **Grep for hardcoded paths first** — build gates, codegen configs, test aliases, and
   scripts referencing `src/...` as strings all break silently on a move:
   ```
   grep -rn "src/\(lib\|components\|app\)" scripts/ *.config.* package.json 2>/dev/null
   ```
5. **Check the test runner's aliases.** If unit tests don't share the app's path alias,
   moved files can typecheck and build green while the whole suite fails to import.
6. Re-run every gate after each PR: typecheck · lint · unit · e2e · build.

## The check (before proposing or committing)

```
# 1. oversized folders (see §2)
# 2. backward imports — shared/design-system reaching into routes
grep -rn "from '@/app/\|from '~/app/\|from '\.\./\.\./app/" --include=*.ts --include=*.tsx \
  src/components src/ui src/shared src/lib 2>/dev/null
# 3. data layer importing UI types
grep -rn "from '@/components\|from '@/ui" --include=*.ts src/lib src/server 2>/dev/null
# 4. entry points missing a runtime contract
grep -rln "use server" --include=*.ts src app 2>/dev/null    # then: does each export parse its input?
# 5. banned folder names
find . -type d \( -name node_modules -prune \) -o -type d \
  \( -name utils -o -name helpers -o -name core -o -name common -o -name misc \) -print
```

## Report

- **Layer map** — the §5 table filled in, with real paths.
- **Violations** — counts per rule, with one file:line example each.
- **Verdict** — what to change, what to leave alone (name it explicitly), what was
  rejected as over-architecture and why.
- **Enforcement** — the lint rule or gate that keeps each fix from regressing. A fix
  with no gate is a fix that comes back.

## Anti-patterns (reject these)

- Proposing a restructure without counting the current violations first.
- `utils/` next to `helpers/` next to `shared/`.
- Rearranging route folders (URLs) to "make it tidy".
- A `types/` folder holding every domain type.
- Layer boundaries documented in markdown with no lint rule behind them.
- "Validation" that is only a TypeScript type on a public endpoint.
- A shared package created for code only one app uses.
- Moving files and changing logic in the same PR.
