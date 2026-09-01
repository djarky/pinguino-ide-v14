#!/bin/sh
#
# Launch Pinguino's IDE
echo "Launch Pinguino's IDE ..."
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASEDIR"

if [ -f "$BASEDIR/venv/bin/python" ]; then
    "$BASEDIR/venv/bin/python" pinguino-ide.py "$@"
elif command -v pipenv >/dev/null 2>&1; then
    pipenv run python pinguino-ide.py "$@"
else
    python3 pinguino-ide.py "$@"
fi
