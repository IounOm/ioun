#!/usr/bin/env python3
"""PreToolUse guard for Supabase MCP write tools.

Reads the hook JSON on stdin. If the SQL contains a destructive statement,
emits permissionDecision "ask" so the dev must confirm before it runs.
Non-destructive queries produce no output -> normal permission flow continues.
"""
import sys, json, re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # can't parse -> don't block

ti = data.get("tool_input") or {}
# execute_sql + apply_migration both carry the SQL under "query"
sql = ti.get("query") or ""
if not isinstance(sql, str) or not sql.strip():
    sys.exit(0)

# Match on BOTH the raw SQL and a comment-stripped copy: stripping alone can be fooled by a
# comment marker inside a string literal ("SELECT '--'; DROP TABLE x").
no_line = re.sub(r"--.*?$", " ", sql, flags=re.M)
clean = re.sub(r"/\*.*?\*/", " ", no_line, flags=re.S)

patterns = [
    r"\bdrop\s+\w+",                       # DROP TABLE/SCHEMA/DATABASE/VIEW/FUNCTION/POLICY/…
    r"\balter\s+table\b[^;]*\bdrop\b",      # ALTER TABLE t DROP [COLUMN] c / DROP CONSTRAINT
    r"\btruncate\b",
    r"\bdelete\s+from\b",
    r"\bdo\s*\$|\bexecute\b",              # dynamic SQL can assemble any statement
    r"\bgrant\b|\brevoke\b",                # privilege changes (Supabase: exposes data via anon/authenticated)
    r"\bdisable\s+row\s+level\s+security\b|\bno\s+force\s+row\s+level\b",
    r"\bcreate\s+or\s+replace\b",          # silently swaps a function/view/policy
    r"\balter\s+table\b[^;]*\b(rename|alter\s+column)\b",
]


def unscoped_update(s: str) -> bool:
    """UPDATE … SET … whose WHERE is missing or trivially true — string literals removed first."""
    s = re.sub(r"'(?:[^']|'')*'", "''", s)
    for stmt in s.split(";"):
        if re.search(r"\bupdate\b[^;]*\bset\b", stmt, re.I):
            m = re.search(r"\bwhere\b(.*)$", stmt, re.I | re.S)
            if not m or re.fullmatch(r"\s*(true|1\s*=\s*1|'1'\s*=\s*'1')\s*", m.group(1), re.I):
                return True
    return False


if any(re.search(p, s, re.I) for p in patterns for s in (sql, clean)) or unscoped_update(clean):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Destructive or dynamic SQL detected (DROP/ALTER…DROP/TRUNCATE/DELETE/UPDATE without WHERE/DO/EXECUTE) on Supabase - confirm before running.",
        }
    }))

sys.exit(0)
