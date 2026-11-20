# web-kit templates

Copy these into a new web project (admin back office, public site, landing page, e-commerce).
The `ioun:web-kit` skill explains when and why; this table says where each file goes.

| File | Copy to | Adapt |
| --- | --- | --- |
| `.mcp.json` | repo root | First `bun add -d --exact shadcn@<version>` (the MCP runs that locked local copy, not `npx`, so transitive deps stay in the lockfile). `--cwd` = the folder holding `components.json` (single app: `.`). Keep versions pinned and the telemetry flags; bump deliberately. |
| `tokens.css` | the app's global stylesheet (e.g. `src/styles/globals.css`) | Replace the neutral values with the brand; keep the role names. |
| `eslint-a11y.mjs` | merge into `eslint.config.mjs` | Next.js already ships `jsx-a11y` via `eslint-config-next`; then only add the stricter rules. |
| `a11y.test.tsx` | next to a component (`*.test.tsx`) | Needs `vitest`, `jsdom`, `@testing-library/react`, `vitest-axe`. |
| `docs/patterns/ui-review.md` | `docs/patterns/ui-review.md` | Fill the project paths. Write it in the team's language. |

Security (from a review of this kit): `.mcp.json` and `.claude/` changes always get a human diff
read before merge (Claude Code remembers MCP approval by server name, so a swapped command runs
without a new prompt). Where the GitHub plan allows, require a review + CODEOWNERS on
`/.mcp.json`, `/.claude/`, `/.github/`. A CI paths filter that skips docs must use
`predicate-quantifier: every` and may skip only inert text (`docs/**`, `**/*.md`,
`.claude/skills/**`), never `.mcp.json` or `.claude/settings*.json`.

Rules the kit assumes: one design-token layer (`ioun:design-system` skill), one i18n layer
(`ioun:i18n-guard`), money through one helper (`ioun:money`), Prettier gate (`ioun:verify-changes`).
