#!/usr/bin/env python3
"""Install the ioun plugin into AI coding tools other than Claude Code (Claude Code: use the plugin).

    git clone https://github.com/IounOm/ioun ~/ioun
    python3 ~/ioun/install.py --tool codex            # or antigravity | copilot | cursor | all
    python3 ~/ioun/install.py --tool codex --dry-run  # show what would change
    python3 ~/ioun/install.py --tool codex --uninstall
    python3 ~/ioun/install.py --update                # git pull this clone, re-run every tool installed before

What it installs, per tool (user level, all projects):
  skills  linked (copied when links are not allowed, e.g. Windows without Developer Mode)
          into the tool's skills folder — `git pull` updates linked skills on its own
  agents  converted to the tool's subagent format (Codex: TOML)
  rules   the session rules (rules/delivery.md) inside a managed block of the tool's global
          instructions file; your own text in that file is kept. Cursor has no such file:
          the installer prints the text to paste into Cursor Settings → Rules once.
Hooks are Claude Code only for now (each tool has its own hook schema and trust step).
State: ~/.ioun/installed.json (what was written, so --uninstall removes exactly that).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("IOUN_HOME", Path.home()))
REPO = Path(__file__).resolve().parent
PLUGIN = REPO / "plugins" / "ioun"
STATE = HOME / ".ioun" / "installed.json"
BEGIN, END = "<!-- ioun:start (managed by the ioun plugin install.py — edits inside are overwritten) -->", "<!-- ioun:end -->"
NOTE = (
    "This tool has the ioun skills installed. Where these rules or skills say `ioun:<name>`, "
    "use the skill or agent named `<name>`. Paths like `standards/x.md` are relative to {root}.\n\n"
)

TOOLS = {
    "codex": {
        "skills": [".agents/skills"],
        "agents": (".codex/agents", "toml"),
        "rules": ".codex/AGENTS.md",
    },
    "antigravity": {
        "skills": [".gemini/config/skills"],
        "agents": (".gemini/config/agents", "md"),
        "rules": ".gemini/GEMINI.md",
    },
    "copilot": {
        "skills": [".copilot/skills"],
        "agents": (".copilot/agents", "md"),
        "rules": ".copilot/copilot-instructions.md",
    },
    "cursor": {
        "skills": [".cursor/skills"],
        "agents": (".cursor/agents", "md"),
        "rules": None,
    },
}


def frontmatter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---\n") and (end := text.find("\n---\n", 4)) != -1:
        for line in text[4:end].splitlines():
            if m := re.match(r"^([A-Za-z_-]+):\s*(.*)$", line):
                meta[m.group(1)] = m.group(2).strip()
        return meta, text[end + 5 :]
    return meta, text


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state: dict, dry: bool) -> None:
    if not dry:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def fingerprint(p: Path) -> str:
    """Content hash of a file or folder (what the installer wrote), to recognise it later."""
    h = hashlib.sha256()
    files = sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
    for f in files:
        h.update(str(f.relative_to(p) if p.is_dir() else f.name).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def ours(dst: Path, managed: dict) -> bool:
    """Only touch what we can prove we wrote: a link into this clone, or unchanged content."""
    if dst.is_symlink():
        try:
            return Path(os.readlink(dst)).resolve().is_relative_to(REPO)
        except OSError:
            return False
    return dst.exists() and managed.get(str(dst)) == fingerprint(dst)


def link_or_copy(src: Path, dst: Path, dry: bool, managed: dict) -> str:
    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() and Path(os.readlink(dst)) == src:
            return "ok"
        if not ours(dst, managed):
            return "SKIPPED — a folder of yours already has this name (rename it, then re-run)"
        if not dry:
            shutil.rmtree(dst) if dst.is_dir() and not dst.is_symlink() else dst.unlink()
    if dry:
        return "would link"
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        dst.symlink_to(src, target_is_directory=src.is_dir())
        return "linked"
    except OSError:
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
        return "copied (re-run after git pull)"


def agent_file(src: Path, kind: str) -> tuple[str, str]:
    meta, body = frontmatter(src.read_text(encoding="utf-8"))
    name, desc = meta.get("name", src.stem), meta.get("description", "")
    if kind == "toml":
        esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')  # noqa: E731
        lit = body.strip().replace("\'\'\'", "\'\' \'")  # TOML literal string: no escapes needed
        text = f'name = "{esc(name)}"\ndescription = "{esc(desc)}"\ndeveloper_instructions = \'\'\'\n{lit}\n\'\'\'\n'
        return f"{name}.toml", text
    # Claude-specific `tools:` / `model:` names can make other tools' subagents hang — drop them.
    return f"{name}.md", f"---\nname: {name}\ndescription: {desc}\n---\n{body}"


def rules_text() -> str:
    rules = (PLUGIN / "rules" / "delivery.md").read_text(encoding="utf-8")
    return NOTE.format(root=PLUGIN.as_posix()) + rules


def write_block(path: Path, block: str, dry: bool) -> str:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    managed = f"{BEGIN}\n{block.rstrip()}\n{END}\n"
    if BEGIN in current and END in current:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", lambda _: managed, current, flags=re.S)
    else:
        new = (current.rstrip() + "\n\n" if current.strip() else "") + managed
    if new == current:
        return "ok"
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
    return "would update" if dry else "updated"


def remove_block(path: Path, dry: bool) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"\n*" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "\n", text, flags=re.S).strip()
        if not dry:
            path.unlink() if not new else path.write_text(new + "\n", encoding="utf-8")


def install(tool: str, dry: bool, state: dict) -> None:
    spec, written = TOOLS[tool], {}
    managed = state.get(tool, {}).get("files", {})
    managed = managed if isinstance(managed, dict) else {}
    for base in spec["skills"]:
        for skill in sorted(p for p in (PLUGIN / "skills").iterdir() if p.is_dir()):
            dst = HOME / base / skill.name
            result = link_or_copy(skill, dst, dry, managed)
            print(f"  skill  {dst}: {result}")
            if not result.startswith("SKIPPED"):
                written[str(dst)] = "" if dst.is_symlink() or dry else fingerprint(dst)
    adir, kind = spec["agents"]
    for src in sorted((PLUGIN / "agents").glob("*.md")):
        name, text = agent_file(src, kind)
        dst = HOME / adir / name
        if dst.exists() and not ours(dst, managed):
            print(f"  agent  {dst}: SKIPPED — a file of yours already has this name")
            continue
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
        print(f"  agent  {dst}")
        written[str(dst)] = "" if dry else fingerprint(dst)
    if spec["rules"]:
        dst = HOME / spec["rules"]
        print(f"  rules  {dst}: {write_block(dst, rules_text(), dry)}")
        state.setdefault(tool, {})["rules"] = str(dst)
    else:
        print("  rules  Cursor has no user-level rules file: paste this once into Cursor Settings → Rules →")
        print("         User Rules (re-paste after an update that changes rules/delivery.md):\n")
        print(rules_text())
    state.setdefault(tool, {})["files"] = written


def uninstall(tool: str, dry: bool, state: dict) -> None:
    info = state.get(tool, {})
    files = info.get("files", {})
    for f in files if isinstance(files, dict) else {}:
        p = Path(f)
        if (p.is_symlink() or p.exists()) and not ours(p, files):
            print(f"  keep   {p} (changed since install — yours now)")
            continue
        if p.is_symlink() or p.is_file():
            print(f"  remove {p}")
            if not dry:
                p.unlink()
        elif p.is_dir():
            print(f"  remove {p}/")
            if not dry:
                shutil.rmtree(p)
    if info.get("rules"):
        print(f"  rules  {info['rules']}: managed block removed")
        remove_block(Path(info["rules"]), dry)
    state.pop(tool, None)


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", choices=[*TOOLS, "all"])
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--update", action="store_true", help="git pull this clone, then re-install every tool installed before")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    state = load_state()
    if a.update:
        if not a.dry_run:
            subprocess.run(["git", "-C", str(REPO), "pull", "--ff-only", "--quiet"], check=False)
        tools = [t for t in state if t in TOOLS]
        if not tools:
            print("nothing installed yet — run with --tool first")
            return 1
    elif a.tool:
        tools = list(TOOLS) if a.tool == "all" else [a.tool]
    else:
        ap.print_help()
        return 2
    for t in tools:
        print(f"{'uninstall' if a.uninstall else 'install'} {t}{' (dry run)' if a.dry_run else ''}:")
        (uninstall if a.uninstall else install)(t, a.dry_run, state)
    save_state(state, a.dry_run)
    if not a.dry_run and not a.uninstall:
        print("done — restart the tool to load skills, agents and rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
