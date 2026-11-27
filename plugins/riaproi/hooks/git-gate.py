#!/usr/bin/env python3
"""PreToolUse(Bash): non-blocking reminder of the gates before a git commit / push.

It does NOT ask the dev to confirm: the model is expected to RUN the gates itself and, if they
pass, push without waiting. This only keeps the rules salient. Never blocks (always exit 0).
Gates: i18n-guard + verify-changes (+ media-lifecycle / design-system / money when relevant).
Also nudges once per clone when the repo ships a pre-push guard that is not wired up.
Pure standard library (no jq), so it runs on macOS, Linux and Windows.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

TIER = " TIER? trivial/small/feature/risky — did this follow its path? (rules/delivery.md § Default delivery flow)"

# `git <option soup> push|commit` — catches `git -C <path> commit` too. A rare false positive is
# harmless (this hook only reminds) while a miss is not. push wins if a command chains both.
OPTS = r"git(?:\s+-\S+(?:\s+[^\s-]\S*)?)*\s+"  # unambiguous (no ReDoS); input is capped below
PUSH = re.compile(OPTS + r"push(?:\s|$)")
COMMIT = re.compile(OPTS + r"commit(?:\s|$)")


def git_exe() -> str | None:
    """Absolute path to git from PATH only — never the current directory (on Windows a repo
    could plant its own git.exe, which a bare "git" would run from the cwd first)."""
    import os

    exts = os.environ.get("PATHEXT", ".EXE").split(os.pathsep) if os.name == "nt" else [""]
    cwd = os.path.realpath(os.getcwd())
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d or not os.path.isabs(d) or os.path.realpath(d) == cwd:
            continue
        for e in exts:
            cand = os.path.join(d, "git" + e.lower() if os.name == "nt" else "git")
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
    return None


def git(*args: str) -> str:
    exe = git_exe()
    if not exe:
        return ""
    try:
        res = subprocess.run([exe, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return res.stdout.strip() if res.returncode == 0 else ""


def guard_hint() -> str:
    """One-line nudge IFF the repo ships a pre-push guard that core.hooksPath does not point at
    (a fresh clone: git has no post-clone hook, so this surfaces it at the first commit/push)."""
    root = git("rev-parse", "--show-toplevel")
    if not root:
        return ""
    wired = git("config", "--get", "core.hooksPath")
    for d in (".githooks", "scripts/git-hooks"):
        if (Path(root) / d / "pre-push").is_file():
            if wired == d:
                return ""
            return (
                f" 🔒 This repo ships {d}/pre-push but it is not active. If the user trusts this repo, "
                f'suggest they enable it ("git config core.hooksPath {d}") — ask first, never enable it yourself.'
            )
    return ""


BRIDGE = " Update README / docs in the same PR if setup, features, structure or data flow changed."


def message(cmd: str) -> str:
    op = "push" if PUSH.search(cmd) else "commit" if COMMIT.search(cmd) else ""
    if not op:
        return ""
    if op == "push":
        return (
            "⚠️ Pushing to GitHub — you must have RUN the gates and seen them pass: i18n-guard + "
            "verify-changes (+ media-lifecycle / design-system / money if relevant). Docs-only: skip "
            "code checks. Never push straight to a branch that auto-deploys — branch → PR → CI."
            + BRIDGE + TIER + guard_hint()
        )
    return (
        "⚠️ Reminder: run i18n-guard + verify-changes (+ money if price/฿ calc or display touched) "
        "before this reaches GitHub." + BRIDGE + TIER + guard_hint()
    )


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    cmd = cmd[:4000] if isinstance(cmd, str) else ""
    msg = message(cmd) if isinstance(cmd, str) else ""
    if msg:
        sys.stdout.reconfigure(encoding="utf-8")
        # systemMessage = shown to the user only; additionalContext = what the MODEL reads (the one
        # that must act on it). Both, so the human sees the reminder and the agent gets it too.
        out = {"systemMessage": msg, "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}}
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
