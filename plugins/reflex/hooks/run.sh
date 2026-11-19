#!/bin/sh
# reflex hook launcher: run a Python hook with whichever Python 3.9+ exists (python3 · python · py),
# so the same hooks work on macOS, Linux and Windows (Git Bash). No Python → warn and exit 0:
# a missing interpreter must never block the user's tool calls.
here="$(cd "$(dirname "$0")" && pwd)"
script="$1"
shift
for py in python3 python py; do
  if command -v "$py" >/dev/null 2>&1 &&
    "$py" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
    exec "$py" "$here/$script" "$@"
  fi
done
echo "reflex: Python 3.9+ not found (python3 / python / py) - reflex hooks are off until it is installed" >&2
exit 0
