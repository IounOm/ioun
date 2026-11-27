---
name: i18n-guard
description: Before committing, verify that any user-facing text you added/changed/removed is properly internationalized — no hardcoded strings, every key present in EVERY supported locale, one single source of truth. Auto-detects the project's i18n setup (library or dictionary) and language set; stack-agnostic. For external-facing projects (websites or anything shipped to other people) it ENFORCES that an i18n layer exists even when there is only one language. Run alongside verify-changes, after touching UI text and before pushing.
---

# i18n-guard

A commit-time gate for translations. When a change touches user-facing text, this
guard makes sure the text lives in the project's single source of truth and that
**every** supported language stays complete — never half-translated, never hardcoded.
Detect the project's setup first, then act. Stack-agnostic (works regardless of
framework or i18n library).

## 1. Classify the project — this sets how strict the rule is
Decide whether the project is **external-facing** or **internal/personal**:

- **External-facing** = a website, web/mobile app, or anything **shipped to or used by
  other people** (customers, staff, clients, the public). Signals: a web framework
  (Next.js, Remix, Vite+React, SvelteKit, Vue/Nuxt, Flutter, native app…), a public
  deploy target, a storefront/landing/marketing site, end-user copy, an admin/ops tool
  other humans log into.
- **Internal/personal** = a CLI, script, library, automation, or a dashboard only the
  author uses.

**The rule:**
- **External-facing → i18n is MANDATORY**, even if there is only one language today.
  All user-facing text must route through an i18n layer (a library or a dictionary
  module) so strings live in one place. **No hardcoded user-facing words.** If the
  project has no i18n layer yet, set one up (§5) before adding/altering copy.
- **Internal/personal → not forced.** A single hardcoded language is acceptable, but
  still prefer one place for strings. If it already has i18n, keep it complete (§4).

If classification is ambiguous, treat it as external-facing (stricter is safer) and say so.

## 2. Detect the i18n setup — do NOT assume
Inspect the repo to learn what's already there:

- **A library?** Check the manifest/deps for one: `next-intl`, `react-i18next`/`i18next`,
  `vue-i18n`, `@lingui/*`, `formatjs`/`react-intl`, `svelte-i18n`, `intl` (Flutter/ARB),
  gettext (`.po`/`.pot`), Rails/Django locale files, etc.
- **Or a hand-rolled dictionary?** Look for `src/i18n/`, `locales/`, `messages/`,
  `lang/`, `translations/`, `dictionaries/`, `*.arb`, `*.po`, `i18n.*`.
- **Determine three things:**
  1. the **source-of-truth locale** (the complete one — often `en` or the team's
     primary language; in dictionary setups the others are usually `Partial` of it),
  2. the **full set of supported locales**,
  3. the **lookup API** used in code (`t('key')`, `<Trans>`, `$t`, `intl.formatMessage`,
     `useTranslations`, an ARB getter, …).

Record these; everything below references them.

## 3. Scan the change for hardcoded user-facing strings
Look at the diff (added + modified lines). Flag any **user-visible literal** that is not
going through the i18n API:

- JSX/HTML text nodes, button/label text, `placeholder`, `title`, `alt`, `aria-label`,
  toast/alert/error messages, validation text, email/notification copy, menu items,
  text built for speech (TTS).
- **Not** flagged: keys themselves, `className`/styles, enum/DB values, log lines, test
  fixtures, code identifiers, URLs, and genuinely non-user-facing strings.
- Mind interpolation (`Hello {name}`) and pluralization — use the i18n layer's
  placeholder/plural mechanism, don't concatenate.

For each flagged literal: replace it with a key lookup and add the key to the source
dictionary (§4). In an internal/personal single-language project this step is advisory;
in an external-facing project it is a **blocker**.

## 4. Sync keys across EVERY locale (parity)
This is the heart of the gate. After your change, the key sets must line up:

- **Added a key** → add it to the **source** locale, then to **every other** locale.
  **Always fill the key now — never block the feature on translation, never ship a
  missing key.** *How* you fill it depends on who reads the copy (see "Translation
  policy" below): for staff/internal screens, machine-assisted translation is an
  acceptable interim; for public/customer-facing copy, fall back to the source language
  and hold that locale until a native review. Report which languages got
  machine-assisted vs fallback vs reviewed values.
- **Removed a string** → remove that key from **all** locales (and the source) so no
  orphans remain.
- **Renamed/edited copy** → update the key (or its value) in **all** locales together.
- **Parity check:** for every supported locale, diff its key set against the source. Any
  key in source but missing from a locale = a gap to fill; any key in a locale but not in
  source = an orphan to delete. Use the project's own structure (nested JSON, flat keys,
  ARB, `.po`, a TS `Record`) — match it, don't reshape it.
- **Dynamic keys** (e.g. ``t(`errors.${code}`)``) → add a test that enumerates the enum and
  asserts a key per value in every locale — key parity can't see a key missing from ALL locales.

**Don't eyeball parity — diff it.** For JSON dictionaries the check is deterministic:
```bash
keys(){ jq -r 'paths(scalars) | join(".")' "$1" | sort; }   # flatten nested → leaf paths
comm -23 <(keys messages/en.json) <(keys messages/th.json)  # in source, MISSING from th → fill
comm -13 <(keys messages/en.json) <(keys messages/th.json)  # in th, ORPHAN not in source → delete
```
Both outputs empty = parity holds. Swap the extractor for the format (`.po` → `grep '^msgid'`;
flat ARB / TS `Record` → adjust the parse). The deterministic part is a natural `pre-commit`
hard block; "no hardcoded string" stays judgment.

Keep the **single source of truth** intact: exactly one canonical place defines the key
set; other locales mirror it. Don't scatter the same string across files.

### Translation policy — follow the project's recorded choice
Keys are **always present in every locale immediately** (never block a feature on
translation). *How* you fill them follows the **MT policy the dev chose at i18n setup**
(§5 step 3), recorded with the i18n config:

- **"Show MT now"** → fill non-source locales with machine-assisted translations and
  surface them, each marked `// TODO(i18n): native review`; report which got MT.
- **"Hold until reviewed"** → fill non-source locales with a **fallback to the source
  language** and keep the locale flagged "needs review / not live" until a native speaker
  signs off.

If no policy is recorded yet, **don't guess silently** — apply the audience default
(internal/staff → show MT · public/customer → hold) and say which you assumed, or ask the
dev to set it. Either way the key set stays complete; only the surfaced value differs.

## 5. External-facing project with no i18n layer → propose, confirm, then establish
If §1 says mandatory but §2 found nothing, an i18n layer is required — but **choosing
and installing one is an architecture decision, not something a commit gate does
silently.** So:

1. **Stop and surface it.** Report that the project is external-facing and has no i18n
   layer, so copy can't be added correctly yet.
2. **Propose an approach + confirm with the user before adding any dependency.** Options:
   the **idiomatic library** for the stack (`next-intl`/`react-i18next` for React,
   `vue-i18n` for Vue, ARB+`intl` for Flutter, gettext for Rails/Django) **or** a small
   **zero-dependency typed dictionary module** (`t(key)` + a source locale). State the
   trade-off; let the user pick. The bar is "strings in one place, typed keys, swappable
   language" — not a specific package.
3. **Also ask the dev to choose the project's translation policy** (same way you offer
   the lib — recommend, but the dev decides). Two options, with your recommendation:
   - **Show machine-assisted translations now, refine later** — recommended for
     internal/staff tools (a readable-but-imperfect string beats none).
   - **Hold non-source locales until native review** (fall back to source meanwhile) —
     recommended for public/customer-facing copy.
   Record the chosen policy with the i18n config so §4 follows it on every later change.
4. **Then scaffold it** with the strings from the current change (and nearby obvious
   ones), wire the lookup, record the source + supported locales + the MT policy. Even a
   single-language (e.g. Thai-only) external project routes copy through this layer so a
   second language drops in later without touching components.
5. This is a real code change — run **verify-changes** afterward.

Do not `install` a framework, pick the MT policy, or commit a new i18n architecture
without that confirm — propose and let the dev choose.

## 6. Report (gate)
One concise block, e.g.:
```
i18n-guard
project: external-facing (Next.js)   setup: dictionary src/i18n (source: en; locales: en, th)
✓ no hardcoded user-facing strings in the diff
✓ +3 keys added to all 4 locales (my/lo machine-assisted — flag for native review)
✓ parity: th 142 · my 142 · lo 142 · en 142
```
- All green → say it's safe to commit/push (then the normal verify-changes gate applies).
- Any hardcoded string in an external-facing project, or any locale missing keys →
  **stop; fix before committing.** Show exactly which strings/keys/locales.

## Notes
- Read-then-act: detect setup + locale set first, then edit.
- Don't invent locales the project doesn't support; don't drop ones it does.
- Out of scope (don't over-reach here): date/number/currency formatting, RTL layout — flag
  if relevant but this gate is about copy.
- **Enforcement vs guidance:** this skill is the *procedure*. Run it yourself before
  pushing; ask the user before the push itself (unless they already told you to push). The machine-wide
  `PreToolUse` git hook (the riaproi git-gate hook) only *reminds* on commit/push
  (non-blocking). The truly deterministic part — locale key-parity — can also be a per-repo
  `pre-commit` lint script for a hard block; "no hardcoded string" / translation quality
  stay judgment.
- Pairs with **verify-changes**: i18n-guard checks the words, verify-changes checks the
  code. Run both before pushing.
