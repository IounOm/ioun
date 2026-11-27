---
name: file-placement
description: Decide a file's home and name BEFORE writing it whenever it outlives the session — an export, a download, a generated report, PDF, sheet or deck. Find the owning standard (project/team plugin, repo docs), list the target folder and copy its siblings' naming, never overwrite a file already sent (re-issue = new date, same day -rev2), never leave a deliverable in Downloads, Desktop or a scratchpad, and report the final absolute path. Use whenever you are about to save or hand over such a file.
---

# file-placement — every lasting file gets a home and a name first

A deliverable saved "somewhere for now" is a file nobody finds again. Decide where it lives and
what it is called before the first write.

## 1 · Find the owning standard

Look, in this order, for the rule that owns this kind of file:

1. A team or project plugin's standard (its `standards/`, rules or skills).
2. The repo's own docs (`docs/README.md`, naming rules, `CONTRIBUTING.md`, `AGENTS.md`).
3. A folder convention the user already uses for this kind of file.

Nothing covers it → ask the user once, then write the answer into that standard (not into a
private memory), so the next session finds it.

## 2 · Match the folder

- List the target folder first and copy its siblings' pattern exactly: date prefix, separators,
  case, language.
- Dates as `YYYY-MM-DD` unless the standard says otherwise; the document's own date, else the day
  it was received — not "today" by default.
- **Never overwrite a file that was already sent or shared.** A re-issue gets the new date; a
  second version on the same day gets `-rev2`, `-rev3`.

## 3 · Write, then clean up

- Scratchpad and temp folders hold intermediates only — delete them once the deliverable lands.
- Never leave a deliverable in `Downloads`, `Desktop` or a scratchpad.
- Report the final absolute path (or the shared link) to the user.
- A team plugin may ship a filing skill for its own storage (shared drive, document system) — when
  one fits, use it instead of choosing the place by hand.
