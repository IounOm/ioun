#!/usr/bin/env python3
"""SessionStart: load the reflex delivery rules into the session (stdout becomes context)."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
rules = (root / "rules" / "delivery.md").read_text(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print(
    "# reflex session rules (rules/delivery.md)\n"
    f"Plugin root: {root.as_posix()} - paths like `standards/x.md` below are relative to it. "
    "This plugin's skills and agents are named `reflex:<name>`.\n"
)
print(rules)
