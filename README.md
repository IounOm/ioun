# reflex

Delivery reflexes for AI coding agents — the checks and habits that should fire on their own:
run the project's gates before every commit, keep user-facing text translatable, route colors
through design tokens, round money one way, plan big work before building it, and review it
adversarially before it ships.

> **Generated repository.** Everything here is published from a private source by a script.
> Pull requests that edit files cannot be merged — open an issue instead.

## Install (Claude Code)

```bash
claude plugin install reflex --marketplace IounOm/reflex
```

Older Claude Code without `--marketplace`: `claude plugin marketplace add IounOm/reflex`, then
`claude plugin install reflex@iounom`.

Then turn on auto-update once: `/plugin` → **Marketplaces** → `iounom` → enable auto-update.
Without it, update by hand: `claude plugin update reflex@iounom`.

Skills and agents are namespaced: type `/reflex:verify-changes`, or let the agent pick skills
from their descriptions. Session rules load automatically at session start.

## What's inside

| Kind | Items |
| --- | --- |
| Skills | `design-system` · `feature-lead` · `grill-with-docs` · `handoff` · `i18n-guard` · `media-lifecycle` · `money` · `project-structure` · `verify-changes` |
| Agents | `backend-node` · `code-reviewer` · `db-postgres` · `devops-cicd` · `frontend-react` · `qa-engineer` · `release-gatekeeper` · `security-auditor` · `spec-challenger` · `task-planner` |
| Hooks | git commit/push gate reminder · destructive-SQL guard for the Supabase MCP · session rules |
| Standards | git-worktree-parallel-sessions · money-rounding-standard · readme-and-diagram-standard |

Hooks are Python 3.9+ (standard library only) launched through `hooks/run.sh`, so they run on
macOS, Linux and Windows (Git Bash).

## Other AI tools (Codex · Antigravity · GitHub Copilot · Cursor)

Skills use the open Agent Skills format, so other tools can load them too:

```bash
git clone https://github.com/IounOm/reflex ~/reflex
python3 ~/reflex/install.py --tool codex      # or antigravity | copilot | cursor | all
python3 ~/reflex/install.py --update          # later: pull + refresh every tool installed
```

The installer links the skills into each tool's skills folder, converts the agents to the
tool's subagent format, and writes the session rules into a managed block of the tool's global
instructions file (Cursor: prints them to paste into Settings → Rules). Your own skills, agents
and instructions are never overwritten. Hooks are Claude Code only for now.

## License

MIT — see [LICENSE](LICENSE).
