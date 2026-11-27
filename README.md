# riaproi

*riaproi* — from the Thai *riap roi*: neat, finished properly.

Delivery reflexes for AI coding agents — the checks and habits that should fire on their own:
run the project's gates before every commit, keep user-facing text translatable, route colors
through design tokens, round money one way, plan big work before building it, and review it
adversarially before it ships.

> **Generated repository.** Everything here is published from a private source by a script.
> Pull requests that edit files cannot be merged — open an issue instead.

## Install (Claude Code)

```bash
claude plugin install riaproi --marketplace IounOm/riaproi
```

Older Claude Code without `--marketplace`: `claude plugin marketplace add IounOm/riaproi`, then
`claude plugin install riaproi@iounom`.

Then turn on auto-update once: `/plugin` → **Marketplaces** → `iounom` → enable auto-update.
Without it, update by hand: `claude plugin update riaproi@iounom`.

Skills and agents are namespaced: type `/riaproi:verify-changes`, or let the agent pick skills
from their descriptions. Session rules load automatically at session start.

## What's inside

| Kind | Items |
| --- | --- |
| Skills | `core-web-vitals` · `design-system` · `feature-lead` · `frontend-design` · `grill-with-docs` · `handoff` · `i18n-guard` · `marketing-analytics` · `marketing-copywriting` · `marketing-cro` · `marketing-schema` · `marketing-seo-audit` · `media-lifecycle` · `money` · `project-structure` · `react-best-practices` · `ui-ux-pro-max` · `verify-changes` · `web-accessibility` · `web-best-practices` · `web-kit` · `web-performance` · `web-quality-audit` · `web-seo` |
| Agents | `backend-node` · `code-reviewer` · `db-postgres` · `devops-cicd` · `frontend-react` · `qa-engineer` · `release-gatekeeper` · `security-auditor` · `spec-challenger` · `task-planner` |
| Hooks | git commit/push gate reminder · destructive-SQL guard for the Supabase MCP · session rules |
| Standards | git-worktree-parallel-sessions · money-rounding-standard · readme-and-diagram-standard |

Hooks are Python 3.9+ (standard library only) launched through `hooks/run.sh`, so they run on
macOS, Linux and Windows (Git Bash).

## Other AI tools (Codex · Antigravity · GitHub Copilot · Cursor)

Skills use the open Agent Skills format, so other tools can load them too:

```bash
git clone https://github.com/IounOm/riaproi ~/riaproi
python3 ~/riaproi/install.py --tool codex      # or antigravity | copilot | cursor | all
python3 ~/riaproi/install.py --update          # later: pull + refresh every tool installed
```

The installer links the skills into each tool's skills folder, converts the agents to the
tool's subagent format, and writes the session rules into a managed block of the tool's global
instructions file (Cursor: prints them to paste into Settings → Rules). Your own skills, agents
and instructions are never overwritten. Hooks are Claude Code only for now.

## License

MIT — see [LICENSE](LICENSE). Bundled third-party skills keep their own license and copyright (the `LICENSE` file in
each skill folder). Each starts with an "Overrides" section — the only text added on top of the
pinned upstream:

| Skill | Upstream | License |
| --- | --- | --- |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/2de1134dc4d1cfe112934611ae5803ae17a1bd7e/.claude/skills/ui-ux-pro-max) @ `2de1134` | MIT |
| `frontend-design` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/44490cccaf6d9f82fdeec9416fbf7c9bd72575dc/plugins/frontend-design/skills/frontend-design) @ `44490cc` | Apache-2.0 |
| `react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices) @ `1a2c79d` | MIT |
| `web-seo` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/seo) @ `afa8da9` | MIT |
| `web-performance` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/performance) @ `afa8da9` | MIT |
| `web-accessibility` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/accessibility) @ `afa8da9` | MIT |
| `web-best-practices` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/best-practices) @ `afa8da9` | MIT |
| `core-web-vitals` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/core-web-vitals) @ `afa8da9` | MIT |
| `web-quality-audit` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00/skills/web-quality-audit) @ `afa8da9` | MIT |
| `marketing-seo-audit` | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1/skills/seo-audit) @ `5b2b400` | MIT |
| `marketing-schema` | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1/skills/schema) @ `5b2b400` | MIT |
| `marketing-copywriting` | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1/skills/copywriting) @ `5b2b400` | MIT |
| `marketing-cro` | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1/skills/cro) @ `5b2b400` | MIT |
| `marketing-analytics` | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1/skills/analytics) @ `5b2b400` | MIT |
