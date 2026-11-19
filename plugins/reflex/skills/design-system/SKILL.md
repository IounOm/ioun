---
name: design-system
description: Before committing UI work, verify every color and font goes through the project's design tokens — never hardcoded. No raw Tailwind palette utilities, no inline hex/rgb/hsl in className or style, no ad-hoc font-family; colors use the semantic token set, fonts use the configured font variable. Missing a role → ADD a token in the one source of truth, don't inline. Auto-detects the token layer; stack-agnostic. Run alongside verify-changes and i18n-guard before pushing.
---

# design-system

A commit-time gate for the **theme**. The app's colors and fonts live in ONE place
(design tokens) so the whole UI can be re-skinned — brand color, dark/light, font —
by editing a single file. A hardcoded `amber-500` / `#111` / `font-family: Inter`
in a component silently breaks that promise. When a change touches UI, make it use
tokens. Stack-agnostic — detect the setup first, then act.

## 0. Detect the token layer (before touching anything)

- **Where are the tokens?** Find the single source of truth: CSS custom properties
  (`:root { --bg: …; --accent: … }`) mapped into the framework theme (e.g. Tailwind
  `theme.colors` referencing `rgb(var(--x) / <alpha-value>)`), a theme object, or
  SCSS/Style-Dictionary tokens. Note the **semantic names** available
  (bg, surface, fg/muted/faint, line, accent, warn, danger, success, info, …).
- **Where is the font?** Find the font setup (e.g. `next/font` → `--font-sans` →
  `fontFamily.sans`, or a `@font-face` + var). There should be ONE place to change it.
- **No token layer yet?** For any project shipped to people, set one up (CSS vars +
  theme mapping + a font var) before adding more UI — that's the fix, not an excuse
  to keep hardcoding. (A throwaway internal script can stay raw.)

## 1. Colors — semantic tokens only

Every color in a component resolves to a **named token**, never a raw value:

- ❌ Tailwind raw palette: `bg-amber-500`, `text-neutral-400`, `ring-white/10`,
  `bg-black/70`, `text-red-400`, `border-white/5`.
- ❌ Inline literals: `className="… text-[#F97316]"`, `style={{ color: '#111' }}`,
  `style={{ background: 'rgb(17 17 17)' }}`, `hsl(...)`.
- ✅ Tokens: `bg-surface`, `text-fg-muted`, `ring-line/10`, `bg-scrim/70`,
  `text-danger`, `bg-accent/15` (opacity modifiers still work because tokens are
  defined as `rgb(var(--x) / <alpha-value>)`).

Map by **meaning**, not by hue: warn (amber), danger (red), success (green), info
(blue), accent (brand), plus surfaces (bg/surface/surface-2), text ramp
(fg → fg-muted → fg-faint → fg-dim → fg-ghost), hairlines (line, used with opacity),
overlays (scrim), on-accent text (ink). Domain colors (e.g. per-status) get their
own tokens.

**Missing a color/role?** Add it to the token source (one CSS var + one theme entry),
then use it. Never inline "just this once" — that's how 300 hardcoded colors happen.

## 2. Fonts — the configured family only

- ❌ `font-family: 'Inter', …` in CSS, a `<link>` to Google Fonts in a component, a
  second `next/font` call, `style={{ fontFamily: '…' }}`.
- ✅ The app font flows from one place (the font var / `fontFamily.sans`); components
  use `font-sans` (or inherit). Change the font by editing that one definition.
- Multi-script apps (Thai/Burmese/Lao/CJK…): keep a fallback stack on the font token
  so scripts the primary font lacks still render.

## 3. The check (run before committing)

Grep the changed components for escapees — this must come back **empty**. **Don't
hardcode `src/`** — App-Router repos put code in `app/`, `components/`, `lib/` (no
`src/`), and monorepos under `apps/*`. Resolve the real source roots first, and use
`--include` filters (portable) instead of `**` brace-globs (need bash `globstar`, off
by default → silently match nothing):

```
# Resolve source roots that actually exist (fallback to cwd); scope to the diff when you can:
ROOTS=$(ls -d app src components lib apps packages 2>/dev/null); [ -z "$ROOTS" ] && ROOTS=.
INC='--include=*.ts --include=*.tsx --include=*.jsx --include=*.css --include=*.scss'
EXC='--exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist --exclude-dir=build'
# raw Tailwind palette + raw black/white utilities
grep -rnE '\b(bg|text|ring|border|from|to|via|fill|stroke|divide|placeholder)-(amber|sky|emerald|red|rose|orange|yellow|green|teal|cyan|blue|indigo|violet|purple|fuchsia|pink|gray|slate|zinc|neutral|stone|white|black)(-[0-9]+)?(/[0-9]+)?\b' $INC $EXC $ROOTS
# inline color literals (allow the token definitions themselves)
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgb\(|rgba\(|hsl\(' $INC $EXC $ROOTS | grep -v ':root'
# stray font-family
grep -rniE 'font-family|fontFamily' $INC $EXC $ROOTS | grep -v 'var(--font'
```
(Best: scope to changed files — `git diff --name-only … | grep -E '\.(tsx?|css|scss)$'` — and grep those; the roots above are the whole-repo fallback.)

Anything that matches is either (a) migrated to a token, or (b) a genuinely
theme-constant that you ADD as a token (e.g. `ink`, `scrim`) — not left raw.

## 4. Report

- **Tokens?** every new/changed color is a semantic token; list any token you added.
- **Font?** no stray font-family; the app font is still single-sourced.
- **Grep clean?** the three checks above return empty (or you justify + tokenize).

## Anti-patterns (reject these)

- `text-neutral-500`, `bg-amber-500/15`, `ring-white/10` in a component — use
  `text-fg-dim`, `bg-warn/15`, `ring-line/10`.
- `text-[#fff]` / `style={{ color: '#000' }}` — token it.
- A component that imports its own font or sets `font-family`.
- Adding a brand-new hue inline because "there's no token for it" — add the token.
