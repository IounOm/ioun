# UI review — checklist before a UI PR

> Template from the web-kit. Translate to the team's language (Thai for Thai teams) and fill the
> `<...>` paths. Keep it short: link the project's own rules instead of copying them.

## 1. Tokens and theme

- Every color, font and radius comes from `<path to tokens.css>`; no raw palette class, hex or
  font-family in components (`riaproi:design-system` gate).
- Works in light and dark mode; the brand color appears only as decoration, never as a button.

## 2. Text and language

- Every string goes through `<i18n layer path>`, all locales have the key (`riaproi:i18n-guard`).
- Thai text: `line-height` >= 1.6, no truncation of tone marks, no all-caps or letter-spacing.
- Long Thai and English labels both fit (try the longest locale at 320 px wide).

## 3. Accessibility (WCAG 2.2 AA)

- Keyboard: every action reachable with Tab, visible focus ring, Esc closes dialogs.
- Labels: every input has a visible label; errors are announced and tied to the field.
- Contrast: text 4.5:1, UI parts 3:1 (checked on the token pairs).
- `bun run lint` (jsx-a11y) and the axe tests pass.
- Live check: Chrome DevTools MCP `lighthouse_audit` (accessibility, best practices, SEO for
  public pages) on the changed page; attach the score or the fixed findings to the PR.
- Motion: every animation respects `prefers-reduced-motion`.
- Public pages before release: run the web-kit design-quality URL audit (impeccable) on mobile
  and desktop; fix contrast and tiny-text findings, treat slop findings as advice.

## 4. States

- Loading, empty, error and permission-denied states exist and use the shared components.
- Destructive actions confirm; forms keep input after a server error.

## 5. Performance (public pages)

- Chrome DevTools MCP performance trace: LCP < 2.5 s, CLS < 0.1, INP < 200 ms on a mid-range
  mobile profile. Images have width/height and modern formats.

## 6. Screenshots

- Before/after screenshots (mobile + desktop, light + dark when the page changed visually).
